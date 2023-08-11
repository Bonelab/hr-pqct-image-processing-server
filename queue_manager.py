# queue_manager.py Version 1.0
# Author: Ian Smith
# Description: This class is intended to manage and shared resources between the threads in main_1.7.py for the
# Autosegment_Server project.
# Created: 2023-06-20
import os
import threading
from queue import Queue

from job import JobData
import ip_utils

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


class State:
    def __init__(self, logger):
        self.lock = threading.Lock()
        self.JOB_QUEUE = Queue()
        self._perform_startup()
        self.logs = logger

    def _perform_startup(self):
        lis = ip_utils.get_abs_paths(BATCHES)
        for item in lis:
            self.JOB_QUEUE.put(item)

    def enqueue(self, job_dir):
        jd = JobData(job_dir)
        self.logs.log_debug("Enqueued {}".format(jd.image_file_name))
        self.JOB_QUEUE.put(job_dir)

    def dequeue(self):
        jd = JobData(self.JOB_QUEUE.get())
        self.logs.log_debug("Dequeued {}".format(jd.image_file_name))
        return jd.base

    def queue_to_list(self):
        a = []
        while not self.JOB_QUEUE.empty():
            a.append(self.JOB_QUEUE.get())
        return a

    # Functionality for move function
    def move_queue(self, jobname, index):
        index = int(index)
        index = index - 1
        a = self.queue_to_list()
        if index > len(a) - 1:
            raise ValueError("Index out of range of the queue")
        to_move = None
        for item in a:  # Finding item that needs to be moved in the queue
            if jobname.lower() in JobData(item).data.get(F_NAME):
                a.remove(item)
                to_move = item
                break
        a.insert(index, to_move)  # Moving requested item
        for item in a:  # Putting everything back on the queue
            self.JOB_QUEUE.put(item)

    # Functionality for remove command
    def remove_from_queue(self, jobname):
        a = self.queue_to_list()
        for item in a:
            if JobData(item).data.get(F_NAME).lower() == jobname.lower():
                item.append_to_com()
                os.remove(item)
            else:
                self.JOB_QUEUE.put(item)

    # Functionality for jobs command
    def get_jobs(self, arg=F_NAME):
        a = self.queue_to_list()
        b = []
        for path in a:
            b.append(JobData(path))
            self.JOB_QUEUE.put(path)
        return b
