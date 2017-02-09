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
    path_dir, path_file = os.path.split(os.path.abspath(args.path))
    return {'dir': path_dir, 'file': path_file}

def read_value(path):
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
        if event.src_path.endswith(split_path(self.path)['file']):
            datapoint = read_value(self.path)
            print('Sending datapoint', datapoint)
            socket.send(datapoint)


# Execution setup
if __name__ == "__main__":
    args = parser.parse_args()

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://{}:{}".format(args.recv_ip, args.recv_port))

    observer = Observer()
    event_handler = RelayHandler(socket, args.path)
    observer.schedule(event_handler, path=split_path(args.path)['dir'])
    observer.start()
    print('Setup completed, watching file')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
