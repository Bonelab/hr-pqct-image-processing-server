# state.py Version 1.0
# Author: Ian Smith
# Description: This class is intended to manage and shared resources between the threads in main_1.7.py for the
# Autosegment_Server project.
# Created: 2023-06-20
import os
import threading
from job import JobTracker
from queue import Queue
import copy
from datetime import datetime, timedelta
import job

DEST = 'destination'
BATCHES = 'batches'
DEL = 'del'
FAILED = 'failed'
MODELS = 'models'
MASKS = 'processed'
REC = 'rec'
TMP = 'tmp'

DATE = "DATE_FINISHED"
F_NAME = "EVAL_FNAME"
DIRS = [BATCHES, DEL, DEST, FAILED, MODELS, MASKS, REC, TMP]


# TODO logging should go in here
class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.current = None
        self.JOB_QUEUE = Queue()
        self.perform_startup()
        self._check_dirs()


    @staticmethod
    def _check_dirs():
        current_dirs = os.listdir()
        for folder in DIRS:
            if folder not in current_dirs:
                os.mkdir(folder)


    def set_current(self, cur):
        self.lock.acquire()
        self.current = cur
        self.lock.release()

    def get_name(self):
        if self.current is None:
            return None
        else:
            return self.current.name

    def get_current(self):
        self.lock.acquire()
        cur = self.current
        self.lock.release()
        return cur

    def enqueue(self, obj):
        obj.move(BATCHES)
        obj.log_action("Enqueued")
        self.JOB_QUEUE.put(obj)

    def dequeue(self):
        obj = self.JOB_QUEUE.get()
        obj.log_action("Dequeued")
        return obj

    def queue_to_list(self):
        a = []
        while not self.JOB_QUEUE.empty():
            a.append(self.JOB_QUEUE.get())
        return a

    # Functionality for move function
    def move_queue(self, jobname, index):
        index = int(index)
        index = index-1
        a = self.queue_to_list()

        if index > len(a)-1:
            raise ValueError("Index out of range of the queue")
        to_move = None

        for item in a:                                              # Finding item that needs to be moved in the queue
            if item.data.get(F_NAME).lower() == jobname.lower():
                a.remove(item)
                to_move = item
                break

        a.insert(index, to_move)                                    # Moving requested item

        for item in a:                                              # Putting everything back on the queue
            self.JOB_QUEUE.put(item)


    # Functionality for remove command
    def remove_from_queue(self, jobname):
        a = self.queue_to_list()
        for item in a:
            if item.data.get(F_NAME).lower() == jobname.lower():
                item.append_to_com()
                item.move(DEST)
                a.remove(item)
            else:
                self.JOB_QUEUE.put(item)

    # Functionality for jobs command
    def get_jobs(self, arg=F_NAME):
        a = self.queue_to_list()
        b = []
        for obj in a:
            b.append(obj.data.get(arg))
            self.JOB_QUEUE.put(obj)

        if self.current is not None:
            b.insert(0, self.current.name)
        else:
            b.insert(0, 'None')

        return b

    # Functionality for info command
    def get_job_com(self, j_name):
        a = self.queue_to_list()
        com = None

        for obj in a:
            fname = obj.data.get(F_NAME)
            if fname.lower() == j_name.lower():
                com = copy.deepcopy(obj.data)
            self.JOB_QUEUE.put(obj)
        return com

    # Functionality for completed command
    @staticmethod
    def get_completed_jobs():
        return job.get_abs_paths(DEST)

    # Functionality for restart command
    def restart_job(self, j_name):
        comp = self.get_completed_jobs()
        for item in comp:
            if j_name.casefold() in item.casefold():
                batch = JobTracker()
                batch.set_up_from_file(item)
                self.enqueue(batch)

    def perform_startup(self):
        lis = job.get_abs_paths(BATCHES)
        to_queue = []
        for file in lis:
            if file.lower().endswith("com"):
                to_queue.append(file)
        for file in to_queue:
            batch = JobTracker()
            batch.set_up_from_file(file)
            self.JOB_QUEUE.put(batch)


    @staticmethod
    def check_date(date_str):
        print(date_str)     # DEBUG
        dt = datetime.fromisoformat(date_str)
        cur = datetime.today()
        time_diff = cur - dt
        if time_diff > timedelta(days=7):
            return True
        else:
            return False

    def cleanup(self, directory):
        files = job.get_abs_paths(directory)
        for file in files:
            if file.lower().endswith(".com"):
                cmd = job.parse_com(file)

                if cmd.get(DATE) is None:
                    fle = JobTracker()
                    fle.set_up_from_file(file)
                    fle.append_to_com()
                elif self.check_date(cmd.get(DATE)):
                    fle = JobTracker()
                    fle.set_up_from_file(file)
                    fle.move("del")  # TODO change to delete, not just move os.remove(file)