# main_1.7.py Version 1.0
# Author: Ian Smith
# Description: Main file for Autosegment_Server, creates the threads with the event loops for the main functionality of
# the program
# Created: 2023-05-19
# Dependencies: pytorch, Anaconda, torchvision, cuda toolkit

import shutil
import threading
from job import JobTracker
from state import State
import job
import socket
import pickle
import time



# Change to 2 paths, rec-img and rec-com
PATH = 'rec'    # Some directory path where incoming files will go
BATCHES = 'batches'
FAILED = 'failed'
DESTINATION = 'destination'


ip_addr = "127.0.0.1"
port = 4000
ADDR = (ip_addr, port)




class Main:
    def __init__(self):
        self.info = State()
        self.main()

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


    # This method is meant to be called in its own thread, it uses a socket to communicate with the command line interface
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
                jbs = self.info.get_jobs()
                self.send_to_cli(jbs, conn, cmd[0])
            elif command == "completed":
                comp = self.info.get_completed_jobs()
                self.send_to_cli(comp, conn, cmd[0])
            elif command == "info":
                inf = self.info.get_job_com(cmd[1])
                self.send_to_cli(inf, conn, cmd[0])
            elif command == "move":
                try:
                    self.info.move_queue(cmd[1], cmd[2])
                    jbs = self.info.get_jobs()
                    self.send_to_cli(jbs, conn, cmd[0])
                except ValueError:
                    pl = "Exception"
                    self.send_to_cli(pl, conn, cmd[0])
            elif command == "restart":
                self.info.restart_job(cmd[1])
                jbs = self.info.get_jobs()
                self.send_to_cli(jbs, conn, cmd[0])
            elif command == "delete":
                self.info.remove_from_queue(cmd[1])
                jbs = self.info.get_jobs()
                self.send_to_cli(jbs, conn, cmd[0])
            elif command == "quit":
                self.send_to_cli("quit", conn, cmd[0])
                quit()
            else:
                pass


    # This method is meant to be called on its own thread, it monitors the directory where the files will be transferred to
    # from vms
    def monitor(self):
        last = time.time()
        while True:
            if time.time() - last > 3600:                       # Checks every hour to clean up files that are more than a
                self.info.cleanup(DESTINATION)                       # week old
                last = time.time()
            file_list = job.get_abs_paths(PATH)
            if len(file_list) != 0:
                item = JobTracker()
                for file in file_list:
                    if file.lower().endswith(".com"):
                        try:
                            item.set_up_from_file(file)
                            self.info.enqueue(item)
                            break
                        except FileNotFoundError:
                            shutil.move(file, FAILED)
                            break
            time.sleep(1)

    # This is the worker function, it pulls jobs off of the queue and processes them and sends back the processed images
    # when done
    def processing(self):
        while True:
            if self.info.JOB_QUEUE.not_empty:
                item = self.info.dequeue()  # First item is gotten from the queue
                self.info.set_current(item)
                print('{} dequeued'.format(item.name))  # Debug
                item.process()
                # item.send()
                item.send()  # TODO change in final ver to send
                self.info.set_current(None)
            time.sleep(1)


def main():
    Main()


if __name__ == "__main__":
    main()