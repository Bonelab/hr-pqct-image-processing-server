"""
main.py
Author: Ian Smith
Description: Handles startup processes and contains all the main event loops for the program
Created: 2023-05-19
Dependencies: pytorch, Anaconda, torchvision, cuda toolkit
Package Dependencies: psutil, daemon, pwd
"""
import traceback

from job import JobManager
from process import Processor
from queue_manager import ManagedQueue
from ip_logging import Logger
from send import Send
from ip_cli import CLI
import constants, ip_utils


import os
import time
import threading
import shutil


class Main:
    def __init__(self):
        """
        Constructor method
        """
        self.logs = Logger()
        self.file_manager = JobManager(self.logs)
        self.processor = Processor(self.logs, self.file_manager)
        self.job_queue = ManagedQueue(self.logs)
        self.transfer = Send(self.logs)
        self.Cli = CLI(self.job_queue, self.processor, self.transfer, self.file_manager, self)

        self.running = True
        self.paused = True

        self.start()
        self.logs.log_debug("Server Started")

    def start(self):
        """
        Method to start the main threads for the program
        :return: None
        """
        # Monitor directory thread
        threading.Thread(target=self.monitor, args=()).start()  # Passing fn as reference
        # Worker thread
        threading.Thread(target=self.processing).start()
        # CLI thread
        threading.Thread(target=self.cli_handle(), args=()).start()
        

    def cli_handle(self):
        """
        Method for activating CLI event loop
        :return: None
        """
        while self.running:
            self.Cli.cli()
            
    def set_processing_state(self, state):
        self.paused = state

    def monitor(self):
        """
        Method to start the event loop to monitor the rec directory, format files and enqueue them
        :return: None
        """
        last = time.time()
        while self.running:
            if time.time() - last > 3600:  # Checks every hour to clean up files that are more than a
                self.file_manager.cleanup(constants.FAILED)                       # week old
                self.file_manager.cleanup(constants.DONE)
                last = time.time()
            file_list = os.listdir(constants.REC)
            if len(file_list) != 0:
                for file in file_list:
                    file = 'rec/' + file
                    file = os.path.abspath(file)
                    if file.lower().endswith(".yaml"):  # change to .yaml?
                        try:
                            job_dir = self.file_manager.create_job_data(file)
                            job_path = self.file_manager.move(job_dir, constants.BATCHES)
                            self.job_queue.enqueue(job_path)
                            break
                        except FileNotFoundError as e:
                            self.logs.log_error(f"{e}")
                            self.logs.log_error(traceback.format_exc())
                            try:
                                shutil.move(file, constants.FAILED)
                            except shutil.Error as e:
                                os.remove(file)
                            break
            time.sleep(1)

    def processing(self):
        """
        Method to handle the event loop for processing jobs
        :return: None
        """
        while self.running:
            
            if self.paused:
                time.sleep(1)
                continue
        
            if self.job_queue.JOB_QUEUE.not_empty:
                job_path = self.job_queue.dequeue()  # First item is gotten from the queue
                job_path = self.file_manager.move(job_path, constants.DEST)
                is_successful = self.processor.process_image(job_path)
                if is_successful: # If the image is processed successfully then it gets sent 
                    is_successful = self.transfer.send(job_path) 
                    job_path = self.file_manager.move(job_path, constants.DONE)
                    if not is_successful: # Failed transfer of files will move the files to the failed directory
                        self.file_manager.move(job_path, constants.FAILED)
                else:
                    self.file_manager.move(job_path, constants.FAILED)
            time.sleep(1)


if __name__ == "__main__":
    Main()
