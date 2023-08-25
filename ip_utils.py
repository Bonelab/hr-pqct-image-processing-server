import os

DATE = "DATE_FINISHED"

DEST = 'destination'
BATCHES = 'batches'
DEL = 'del'
FAILED = 'failed'
LOGS = 'logs'
MODELS = 'models'
DONE = 'processed'
REC = 'rec'
TMP = 'tmp'
DIRS = [BATCHES, DEL, DEST, FAILED, LOGS, MODELS, DONE, REC, TMP]


def get_abs_paths(directory):
    files = os.listdir(directory)
    n_files = []
    for f in files:
        f = os.path.join(directory, f)
        f = os.path.abspath(f)
        f = os.path.normpath(f)
        n_files.append(f)
    return n_files


# Converts a file path from the vms format to the linux format
def convert_path(path):
    if "[" in path or "]" in path:
        path = path.replace(":", "")
        path = path.replace(".", "/")
        path = path.replace("[", "/")
        path = path.replace("]", "/")
        path = "/" + path
    return path







