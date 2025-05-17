"""Seed script to populate the database with user data from a CSV file."""

#!/usr/bin/python3
import sys

processing = __import__("1-batch_processing")

##### print processed users in a batch of 50
try:
    # print("Batch processing started successfully.")
    processing.batch_processing(50)
    # print("Batch processing completed successfully.")
except BrokenPipeError:
    sys.stderr.close()
