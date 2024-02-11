import argparse
import logging

# Setup argument parser to accept log level
parser = argparse.ArgumentParser(description='Configure log level for the application.')
parser.add_argument('-l', '--log_level', type=str, help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)', default='INFO')

def run():
    pass

if __name__ == "__main__":
    args = parser.parse_args()
    
    # set log level 
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {args.log_level}')
    logging.basicConfig(level=numeric_level)

    # kick off a run 
    run()