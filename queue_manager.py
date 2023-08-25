"""
queue_manager.py
Author: Ian Smith
Description: This module contains only one class ManagedQueue which is to be used as the main job queue for the system
Created: 2023-06-20
"""
import os
import threading
from queue import Queue
import constants

from job import JobData
import ip_utils


class ManagedQueue:
    def __init__(self, logger):
        """
        Constructor Method
        :param logger: Injected logger from the ip_logging module
        """
        self.lock = threading.Lock()
        self.JOB_QUEUE = Queue()
        self._perform_startup()
        self.logs = logger

    def _perform_startup(self):
        """
        After a restart/crash this method allows for the jobs that were on the queue to be re-queued
        :return:None
        """
        lis = ip_utils.get_abs_paths(constants.BATCHES)
        for item in lis:
            self.JOB_QUEUE.put(item)

    def enqueue(self, job_dir):
        """
        Method to enqueue a job
        :param job_dir: Base directory of a job
        :return: None
        """
        jd = JobData(job_dir)
        self.logs.log_debug("Enqueued {}".format(jd.image_file_name))
        self.JOB_QUEUE.put(job_dir)

    def dequeue(self):
        """
        Method to dequeue a job from the ManagedQueue
        :return: Base directory of a job
        """
        jd = JobData(self.JOB_QUEUE.get())
        self.logs.log_debug("Dequeued {}".format(jd.image_file_name))
        return jd.base

    def queue_to_list(self):
        """
        Method to turn the queue into a list
        :return:
        """
        a = []
        while not self.JOB_QUEUE.empty():
            a.append(self.JOB_QUEUE.get())
        return a

    # Functionality for move function
    def move_queue(self, jobname, index):
        """
        Method to move a job on the queue, primarily used by the CLI
        :param jobname: Name of job to be moved
        :param index: Index of where you want the job to be moved on the queue
        :return: None
        """
        index = int(index)
        index = index - 1  # index - 1 because when the queue is displayed via the CLI 0 represents the item being processed
        a = self.queue_to_list()
        if index > len(a) - 1 or index < 0:
            raise ValueError("Index out of range of the queue")
        to_move = None
        for item in a:  # Finding item that needs to be moved in the queue
            if jobname.lower() in JobData(item).data.get(constants.F_NAME):
                a.remove(item)
                to_move = item
                break
        a.insert(index, to_move)  # Moving requested item
        for item in a:  # Putting everything back on the queue
            self.JOB_QUEUE.put(item)

    def remove_from_queue(self, jobname):
        """
        Allows for the removal of a job from the queue, primarily used by the CLI
        :param jobname: Name of a job
        :return:
        """
        a = self.queue_to_list()
        for item in a:
            if JobData(item).base_name.lower() == jobname.lower():
                item.append_to_com()
                os.remove(item)
            else:
                self.JOB_QUEUE.put(item)

    # Functionality for jobs command
    def get_jobs(self):
        """
        Method to return a list of jobs that are on the queue, primarily used by the CLI
        :return: Returns a list of jobs from the queue
        """
        a = self.queue_to_list()
        b = []
        for path in a:
            b.append(JobData(path))
            self.JOB_QUEUE.put(path)
        return b
