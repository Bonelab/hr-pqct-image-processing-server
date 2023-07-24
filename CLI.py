# CLI.py
# Author: Ian Smith
# Description: Allows for communication with the main part of Autosegment_Server while it is daemonized
# Created: 2023-06-16
import os
import socket
import pickle
import argparse
import sys
import psutil
from main import Main
import subprocess

JOBNAME = "EVAL_FNAME"
FILE_TYPE = "FEXT"
JOB_TYPE = ""
CLIENT_ADDR = "CLIENT_HOSTNAME"
ACCOUNT_NAME = "CLIENT_USERNAME"

FORMAT = "utf-8"
ip_addr = "127.0.0.1"
PORT = 4000
ADDR = (ip_addr, PORT)
pid = "/tmp/main.pid"


def is_daemonized():
    if os.path.exists(pid):
        with open(pid) as f:
            did = int(f.read().strip())
            return psutil.pid_exists(did)
    else:
        return False


# Form [<command>, <arg1>, <arg2>, ..., <argn>]
# SEND: Sends the command to the server
def send(msg, cli):
    msg = pickle.dumps(msg)
    cli.sendall(msg)


# What needs to be done for each
# Several commands need to be created as args here
# Jobs      -j: Prints a list of jobs on queue and whichever is currently processing
#           What is needed for this command
#           * State.py must be able to return a list of all jobs on its queue and what is currently being processed
# Completed -c: Prints off a list of recently completed jobs
#           Should we have a list of all completed jobs as well or just recently completed?
#           What is needed here
#           * Server side needs to be able to track and store recently completed jobs
#           * Server side needs to handle deleting jobs after a certain timeframe (1 week?)
#           * Server side needs to be able to return a list of recently competed jobs
# restart   -r <jobname>: restarts a job
#           What is needed here
#           * Ability to find a job by EVAL_FNAME upper or lower
#           * Meshes well with case above
#           * Signal to server what job in completed should eb put back on queue
# info      -i <jobname>: Prints out info about a job
#           What is needed here
#           * By default returns info of job currently being processed
#           * Ability to find job by EVAL_FNAME
#           * Return com file dictionary and display needed data from that
# Start     -start: Starts the server
#           What is needed here
#           * Check if the process is already running (Set the PID and check for it?)
#           * Run command as subprocess.run
# Stop      -stop: stops the server
#           * Check if it is running
#           * End process/change scheduling
# Move      -m <jobname><new_pos>
#           What is needed for this
#           * Ability to rearrange queue


def create_parser():
    parser = argparse.ArgumentParser(description="Segmentation Server for HR-pQCT scans")
    parser.add_argument(
        "-j",
        "--jobs",
        action="store_true",
        default=False,
        help="Shows a list of jobs currently on queue and currently being processed"
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store",
        type=str,
        default=None,
        help="Delete a job from the queue that is not currently active"
    )
    parser.add_argument(
        "-r",
        "--restart",
        action="store",
        metavar="JOBNAME",
        help="Restart a job that has recently been finished")
    parser.add_argument(
        "-c",
        "--completed",
        action="store_true",
        default=False,
        help="Shows jobs completed within the last week"
    )
    parser.add_argument(
        "-i",
        "--info",
        metavar="JOBNAME",
        action="store",
        type=str,
        default=None,
        help="Get information about a specific job"
    )
    parser.add_argument(
        "-m",
        "--move",
        metavar=("JOBNAME", "NEW_POSITION"),
        nargs=2,
        action="store",
        default=None,
        help="Move an item within the queue"
    )
    parser.add_argument(
        "-s",
        "--start",
        action="store_true",
        default=False,
        help="Starts the segmentation server"
    )
    parser.add_argument(
        "-q",
        "--quit",
        action="store_true",
        default=False,
        help="Shuts down segmentation server"
    )

    return parser


def handle_args(cli, args):
    if is_daemonized():
        nm = vars(args)
        for key in nm:
            if not (nm.get(key) is None or nm.get(key) is False):
                cmd = [key]
                if isinstance(nm.get(key), list):
                    cmd = cmd + nm.get(key)
                else:
                    cmd.append(nm.get(key))
                send(cmd, cli)

    # Handle special cases (Start)
    # Turn namespace to dict
    # Get args that are not None or False
    # Send command + args to server side code


def handle_response(data):
    command = data[0]
    if command == "jobs":
        print("Jobs in queue: (0 is being processed)")
        print_jobs(data[1])
    elif command == "move":
        print("Job Moved:")
        print_jobs(data[1])
    elif command == "restart":
        print("Job Re-queued:")
        print_jobs(data[1])
    elif command == "delete":
        print("Job Deleted")
        print_jobs(data[1])
    elif command == "completed":
        print("Completed Jobs")
        print_jobs(data[1])
    elif command == "info":
        print_info(data[1])
    else:
        print("Invalid Command")
    print()


def print_info(info):
    if info is not None:
        print("Job Information")
        print("Job Name:\t\t{}".format(info.get(JOBNAME)))
        #    print("Job Type:\t\t{}".format(info.get(JOB_TYPE)))
        print("File Type:\t\t{}".format(info.get(FILE_TYPE)))
        print("Client Name:\t{}@{}".format(info.get(ACCOUNT_NAME), info.get(CLIENT_ADDR)))


def print_jobs(job_list):
    count = 0
    for job in job_list:
        if count % 4 == 0 and count != 0:
            sys.stdout.write("\n{}: {}\t\t\t".format(count, job))
        else:
            sys.stdout.write("{}: {}\t\t\t".format(count, job))
        count += 1


def start_server():
    if not is_daemonized():
        print("Starting Server")
        subprocess.Popen(['python3', 'main.py'])
        print("Server Started")


def cli():
    args = create_parser().parse_args()
    if args.start:
        start_server()
    else:
        try:
            CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            CLIENT.connect(ADDR)
            handle_args(CLIENT, args)
            response = pickle.loads(CLIENT.recv(32767))
            handle_response(response)
        except EOFError:
            print("No Response From Server")


cli()
