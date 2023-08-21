from job import JobData
import constants
import os
from datetime import datetime
from datetime import timedelta

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

def parse_com(file_path):
    command_file = {}
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip("$").strip()
            if "!" in line:
                sp = line.split("!")
                line = sp[0]
            if ":==" in line:
                split = line.split(":==")
                if split[1] != "":
                    command_file[split[0].strip()] = split[1].strip()
    return command_file


# Converts a file path from the vms format to the linux format
def convert_path(path):
    if "[" in path or "]" in path:
        path = path.replace(":", "")
        path = path.replace(".", "/")
        path = path.replace("[", "/")
        path = path.replace("]", "/")
        path = "/" + path
    return path


def check_date(date_str):
    dt = datetime.fromisoformat(date_str)
    cur = datetime.today()
    time_diff = cur - dt
    if time_diff > timedelta(days=constants.TIME_TO_DELETE):
        return True
    else:
        return False


def cleanup(directory):
    files = get_abs_paths(directory)
    for file in files:
        to_del = False
        with JobData as jd:
            if jd.data.get(constants.DATE) is None:
                date = datetime.today()
                date_str = date.strftime("%Y-%m-%d")
                jd.data[constants.DATE] = date_str
                jd.data[constants.DATE] = date_str
            elif check_date(jd.data.get(constants.DATE)):
                to_del = True
        if to_del:
            os.remove(file)

