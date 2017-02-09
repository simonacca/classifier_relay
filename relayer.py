import argparse
import zmq
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Command line argument parset
parser = argparse.ArgumentParser(description='Relays classifier values to a machine on the network.')
parser.add_argument('--recv-ip', type=str,
                    help='IP address of the receiving computer')
parser.add_argument('--recv-port', type=int, default=5555,
                    help='Port of the receiving computer')
parser.add_argument('--path', type=str,
                    help='Path of the file to be watched')


# File change event handler
class RelayHandler(FileSystemEventHandler):
    def __init__(self, socket):
        self.socket = socket

    def on_modified(self, event):
        print ("Got it!")
        # socket.send(123)


# Execution setup
if __name__ == "__main__":
    args = parser.parse_args()
    
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    # socket.connect("tcp://{}:{}".format(args.recv_ip, args.recv_port))

    observer = Observer()
    event_handler = RelayHandler(socket)
    observer.schedule(event_handler, path=args.path)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
