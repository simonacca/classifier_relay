import os
import time
import argparse
import zmq
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DATA_LINE_BEGINNING_TOKEN = 'Time point:'

# Command line argument parset
parser = argparse.ArgumentParser(description='Relays classifier values to a machine on the network.')
parser.add_argument('--recv-ip', type=str,
                    help='IP address of the receiving computer')
parser.add_argument('--recv-port', type=int, default=5555,
                    help='Port of the receiving computer')
parser.add_argument('--path', type=str,
                    help='Path of the file to be watched')

def split_path(path):
    "Splits file path into directory and file"
    path_dir, path_file = os.path.split(os.path.abspath(args.path))
    return {'dir': path_dir, 'file': path_file}

def read_value(path):
    "Reads last line datapoint from file"
    with open(path, 'r') as f:
        line = f.readlines()[-1]
    if not line.startswith(DATA_LINE_BEGINNING_TOKEN):
        return None
    else:
        return float(line.split(' ')[-1])

# File change event handler
class RelayHandler(FileSystemEventHandler):
    def __init__(self, socket, path):
        self.socket = socket
        self.path= path

    def on_modified(self, event):
        "Called when a file is modified"

        try:
            # Checks that the modified file is the one we are interested in
            if event.src_path.endswith(split_path(self.path)['file']):
                # reads the newly appended value
                datapoint = read_value(self.path)
                if datapoint:
                    print('Sending datapoint', datapoint)
                    # sends the new value over the network
                    socket.send_string(str(datapoint))
        except IOError:
            pass


# Main Execution setup
if __name__ == "__main__":
    # command line arguments reading
    args = parser.parse_args()

    # Networking setup
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://{}:{}".format(args.recv_ip, args.recv_port))

    # File watchdog setup
    observer = Observer()
    event_handler = RelayHandler(socket, args.path)
    observer.schedule(event_handler, path=split_path(args.path)['dir'])
    observer.start()
    print('Setup completed, watching file')

    # Graceful stop on ctrl-c press
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
