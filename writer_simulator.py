import argparse
import time
import os

DATA_LINE_BEGINNING_TOKEN = 'Time point:'

parser = argparse.ArgumentParser(description=('Copies a file line by line at '
                                'a given speed, simulating the classifier'
                                ' output.'))
parser.add_argument('--input', type=str, help='Path of the input file')
parser.add_argument('--output', type=str, default='out.cto',
                    help='Path of the output file')
parser.add_argument('--sleep', type=float, default=1, help='Sleep time')
args = parser.parse_args()

# Reads input file
with open(args.input, 'r') as f:
    lines = f.readlines()

# Writes to output file
for line in lines:
    with open(args.output, 'a+') as f:
        f.write(line)
    # If the line is not a dataline, wait 0 sec
    # sleep for the defined time otherwise
    time.sleep(args.sleep if line.startswith(DATA_LINE_BEGINNING_TOKEN) else 0)

os.remove(args.output)
