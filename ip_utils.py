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
MASKS = 'processed'
REC = 'rec'
TMP = 'tmp'
DIRS = [BATCHES, DEL, DEST, FAILED, LOGS, MODELS, MASKS, REC, TMP]


def ensure_directories_exist(dirs=None):
    if dirs is None:
        dirs = DIRS
    for folder in dirs:
        _create_directory_if_not_exist(folder)


def _create_directory_if_not_exist(folder):
    full_path = os.path.join(os.getcwd(), folder)
    if not os.path.exists(full_path):
        os.mkdir(full_path)


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


# Appends the date to the end of the com file, important for cleaning up the garbage after a week
def append_to_com(com_file):
    with open(com_file, 'a') as f:
        date = datetime.today()
        date_string = date.strftime("%Y-%m-%d")
        f.write('$ DATE_FINISHED :== {}'.format(date_string))


# Remove date at the end of the com file
def rm_from_com(com_file):
    with open(com_file, 'r') as f:
        lines = f.readlines()
    with open(com_file, 'w') as f:
        for line in lines:
            if 'DATE_FINISHED' not in line:
                f.write(line)


def check_date(date_str):
    dt = datetime.fromisoformat(date_str)
    cur = datetime.today()
    time_diff = cur - dt
    if time_diff > timedelta(days=7):
        return True
    else:
        return False


def cleanup(self, directory):
    files = get_abs_paths(directory)
    for file in files:
        if file.lower().endswith(".com"):
            cmd = parse_com(file)
            if cmd.get(DATE) is None:
                fle = JobData()
                fle.set_up_from_file(file)
                fle.append_to_com()
            elif self.check_date(cmd.get(DATE)):
                fle = JobData()
                fle.set_up_from_file(file)
                fle.remove()
