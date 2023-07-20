# CLI.py
# Author: Ian Smith
# Description: Allows for communication with the main part of Autosegment_Server while it is daemonized
# Created: 2023-06-16


import socket
import pickle
import argparse
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

CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CLIENT.connect(ADDR)


# Form [<command>, <arg1>, <arg2>, ..., <argn>]
# SEND: Sends the command to the server
def send(msg):
    msg = pickle.dumps(msg)
    CLIENT.sendall(msg)


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


def handle_args():
    args = create_parser().parse_args()
    nm = vars(args)
    if args.start:
        print("Starting server")
        subprocess.run("python main_1.7.py")
    else:
        for key in nm:
            if not (nm.get(key) is None or nm.get(key) is False):
                cmd = [key]
                if isinstance(nm.get(key), list):
                    cmd = cmd + nm.get(key)
                else:
                    cmd.append(nm.get(key))
                send(cmd)

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


    # match data[0]:
    #     case "jobs":
    #         print("Jobs in queue: (0 is being processed)")
    #         print_jobs(data[1])
    #     case "move":
    #         print("Job Moved:")
    #         print_jobs(data[1])
    #     case "restart":
    #         print("Job Re-queued:")
    #         print_jobs(data[1])
    #     case "delete":
    #         print("Job Deleted")
    #         print_jobs(data[1])
    #     case "completed":
    #         print("Completed Jobs")
    #         print_jobs(data[1])
    #     case "info":
    #         print_info(data[1])


def print_info(info):
    if info is not None:
        print("Job Information")
        print(f"Job Name:\t\t{info.get(JOBNAME)}")
        #    print(f"Job Type:\t\t{info.get(JOB_TYPE)}")
        print(f"File Type:\t\t{info.get(FILE_TYPE)}")
        print(f"Client Name:\t{info.get(ACCOUNT_NAME)}@{info.get(CLIENT_ADDR)}")


def print_jobs(job_list):
    count = 0
    for job in job_list:
        if count % 4 == 0 and count != 0:
            print(f"\n{count}: {job}\t\t\t", end="")
        else:
            print(f"{count}: {job}\t\t\t", end="")
        count += 1


def main():
    handle_args()
    response = pickle.loads(CLIENT.recv(32767))
    handle_response(response)


if __name__ == "__main__":
    main()
