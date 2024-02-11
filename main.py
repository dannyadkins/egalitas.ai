import argparse
import logging

# Setup argument parser to accept log level
parser = argparse.ArgumentParser(description='Configure log level for the application.')
parser.add_argument('-l', '--log_level', type=str, help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)', default='INFO')

def run():

    # This is a monolithic run function that performs all steps of the pipeline
    # In the future, we will break this down into smaller functions that interact via a message queue

    # Fetch document from source URL 
    # - This might involve taxonomy/process discovery/function writing
    # - Or just executing the function if we already know how 

    # Extract data from document 

    # Extract metadata from document (e.g. title, author, date, topics.)

    # Perform side effects on document (e.g. create/update other entities like people, cases)
    # - This involves sequences of actions like lookups to see which entities we have already 
    # - Requires knowledge of entire schema 

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