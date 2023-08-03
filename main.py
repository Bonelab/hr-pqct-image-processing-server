# main.py Version 2.0
# Author: Ian Smith
# Description: Main file for HR-pQCT Image Processing Server, creates the threads with the event loops for the
# main functionality of the program
# Created: 2023-05-19
# Dependencies: pytorch, Anaconda, torchvision, cuda toolkit


from job import JobManager
from send import Send
from process import Processor
from queue_manager import State
from ip_logging import Logger
from send import Send
import ip_utils

import os
import socket
import time
import threading
import shutil
import pickle

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


# Change to 2 paths, rec-img and rec-com
PATH = 'rec'  # Some directory path where incoming files will go
BATCHES = 'batches'
FAILED = 'failed'
DESTINATION = 'destination'

ip_addr = "127.0.0.1"
port = 4000
ADDR = (ip_addr, port)


class Main:
    def __init__(self):
        ip_utils.ensure_directories_exist()

        self.logs = Logger()
        self.file_manager = JobManager(self.logs)
        self.job_queue = State(self.logs)
        self.processor = Processor(self.logs)
        self.transfer = Send(self.logs)
        self.file_manager = JobManager(self.logs)


        self.main()
        self.logs.log_debug("Server Started")

    # Main method of the program, sets up the threads for each individual process and performs startup routines
    def main(self):
        # Monitor directory thread
        threading.Thread(target=self.monitor, args=()).start()  # Passing fn as reference
        # Worker thread
        threading.Thread(target=self.processing).start()
        # CLI thread
        threading.Thread(target=self.cli_handle(), args=()).start()

    @staticmethod
    def send_to_cli(dat, con, cmd):
        to_send = [cmd, dat]
        to_send = pickle.dumps(to_send)
        con.sendall(to_send)

    # This method is meant to be called in its own thread, it uses a socket to communicate with the command line
    # interface
    def cli_handle(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(ADDR)
        server.listen()
        while True:
            conn, client_addr = server.accept()  # Blocking code, use conn to send data back to the cli
            data = conn.recv(1024)
            cmd = pickle.loads(data)
            # Form [<command>, <arg1>, <arg2>, ..., <argn>]
            command = cmd[0]

            if command == "jobs":
                jbs = self.job_queue.get_jobs()
                self.send_to_cli(jbs, conn, cmd[0])
            elif command == "completed":
                comp = self.job_queue.get_completed_jobs()
                self.send_to_cli(comp, conn, cmd[0])
            elif command == "info":
                inf = self.job_queue.get_job_com(cmd[1])
                self.send_to_cli(inf, conn, cmd[0])
            elif command == "move":
                try:
                    self.job_queue.move_queue(cmd[1], cmd[2])
                    jbs = self.job_queue.get_jobs()
                    self.send_to_cli(jbs, conn, cmd[0])
                except ValueError:
                    pl = "Exception"
                    self.send_to_cli(pl, conn, cmd[0])
            elif command == "restart":
                self.job_queue.restart_job(cmd[1])
                jbs = self.job_queue.get_jobs()
                self.send_to_cli(jbs, conn, cmd[0])
            elif command == "delete":
                self.job_queue.remove_from_queue(cmd[1])
                jbs = self.job_queue.get_jobs()
                self.send_to_cli(jbs, conn, cmd[0])
            elif command == "quit":
                self.send_to_cli("quit", conn, cmd[0])
                quit()
            else:
                pass

    # This method is meant to be called on its own thread, it monitors the directory where the files will be
    # transferred to from vms
    def monitor(self):
        last = time.time()
        while True:
            if time.time() - last > 3600:  # Checks every hour to clean up files that are more than a
                # ip_utils.cleanup(DESTINATION)                       # week old
                last = time.time()
            file_list = ip_utils.get_abs_paths(PATH)
            if len(file_list) != 0:
                for file in file_list:
                    file = os.path.abspath(file)
                    if file.lower().endswith(".com"):
                        try:
                            job_dir = self.file_manager.create_job_data(file)
                            job_path = self.file_manager.move(job_dir, BATCHES)
                            self.job_queue.enqueue(job_path)
                            break
                        except FileNotFoundError:
                            shutil.move(file, FAILED)
                            break
            time.sleep(1)

    # This is the worker function, it pulls jobs off of the queue and processes them and sends back the processed images
    # when done
    def processing(self):
        while True:
            if self.job_queue.JOB_QUEUE.not_empty:
                job_path = self.job_queue.dequeue()  # First item is gotten from the queue
                job_path1 = self.file_manager.move(job_path, DESTINATION)
                self.processor.process_image(job_path1)
                job_path2 = self.file_manager.move(job_path1, DONE)
                self.transfer.send(job_path2)

            time.sleep(1)


def main():
    Main()


if __name__ == "__main__":
    main()
