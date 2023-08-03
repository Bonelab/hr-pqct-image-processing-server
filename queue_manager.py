# queue_manager.py Version 1.0
# Author: Ian Smith
# Description: This class is intended to manage and shared resources between the threads in main_1.7.py for the
# Autosegment_Server project.
# Created: 2023-06-20
import os
import threading
from job import JobData
from queue import Queue
import copy

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
        self.current = None
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
            if item.data.get(F_NAME).lower() == jobname.lower():
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
            if item.data.get(F_NAME).lower() == jobname.lower():
                item.append_to_com()
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
        return ip_utils.get_abs_paths(DEST)

    # Functionality for restart command
    def restart_job(self, j_name):
        comp = self.get_completed_jobs()
        for item in comp:
            if j_name.casefold() in item.casefold():
                batch = JobData()
                batch.set_up_from_file(item)
                self.enqueue(batch)
