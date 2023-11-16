"""
constants.py
Author: Ian Smith
Module to hold needed constants for this program
"""

# Important Directories

DEST = 'destination'
BATCHES = 'batches'
DEL = 'del'
FAILED = 'failed'
DONE = 'processed'
REC = 'rec'
TMP = 'tmp'
STATE = 'state'
DIRS = [BATCHES, DEL, DEST, FAILED, DONE, REC, TMP, STATE]
JOB_DIRS = [BATCHES, DEST, DONE, FAILED]



# Time before a file gets deleted in days
TIME_TO_DELETE = 7


# Important Values from COM file
DATE = "DATE"
F_NAME = "EVAL_FNAME"
TARGET_IMAGE = "TARGET_FILE"
EXT = "FEXT"
EVAL_FEXT = "EVAL_FEXT"
JOB_TYPE = "JOB_TYPE"


# Socket details for communicating from CLI to daemon
ip_addr = "127.0.0.1"
port = 4001
ADDR = (ip_addr, port)


# Log Locations
DEBUG = "logs/debug.log"
ERROR = "logs/error.log"


# Checkpoint Files
QUEUE_CHECKPOINT = '/state/queue.txt'
PROCESS_CHECKPOINT = '/state/process.txt'


# Model setup parameters
RAD_TIB_PATH_TO_ENV = r"\C:\home\ian.smith2\.conda\envs\bl_torch\bin\python"      #"/home/ian.smith2/.conda/envs/bl_torch/bin/python"
RAD_TIB_PATH_TO_START = r"\C:\data\repo\HR-pQCT-Segmentation\segment.py"  #r"/data/repo/HR-pQCT-Segmentation/segment.py"
RAD_TIB_TRAINED_MODELS = "radius_tibia_final"


