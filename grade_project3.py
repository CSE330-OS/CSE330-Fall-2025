__copyright__   = "Copyright 2025, VISA Lab"
__license__     = "MIT"

"""
File: grade_project3.py
Author: Kritshekhar Jha
Description: Grading script for Project-3
"""
import re
import os
import pdb
import time
import json
import shutil
import zipfile
import logging
import argparse
import textwrap
import threading
import subprocess

from utils import *

KM_TIMEOUT = 240

class grader_project3():
    def __init__(self, logger, asuid): 
        self.logger                 = logger
        self.asuid                  = asuid

    def print_and_log(self, message):
        print(message)
        self.logger.info(message)

    def print_and_log_warn(self, message):
        print(message)
        self.logger.warn(message)

    def print_and_log_error(self, message):
        print(message)
        self.logger.error(message)

    def execute_kernel_module(self, asuid, extracted_folder, script_path, num, prod, cons, size, regular, zombies): 

        test_results        = {}
        comments            = ""
        tc_status           = ""
        tc_points           = 0
        kernel_module_err   = ""
        restart_required    = False

        try:
            self.print_and_log(f"----------------- Executing Test-Case:{num} ----------------")
            self.print_and_log(f"Running test case {num}: prod={prod}, cons={cons}, size={size}, regular processes={regular}, zombies processes={zombies}")
            #extracted_folder    = f'extracted_{asuid}'
            #extract_zip(self.logger, zip_file, extracted_folder)
            source_code_path    = find_source_code_path(extracted_folder)
            #TODO: Maybe add a timeout here. 
            result_kernel       = subprocess.run(["sudo", script_path, source_code_path, str(prod), str(cons), str(size), str(regular), str(zombies)],capture_output=True, text=True, check=True, timeout=KM_TIMEOUT)

            kernel_stdout_output = result_kernel.stdout
            kernel_stderr_output = result_kernel.stderr

            self.print_and_log(f"Test Case {num}: Script Output: {kernel_stdout_output}")
            comments += kernel_stdout_output
            tc_logs   = kernel_stdout_output

            if kernel_stderr_output:
                self.print_and_log_error(f"[TC-{num}-log]: Script Error: {kernel_stderr_output}")
                comments += kernel_stderr_output

            zombie_pattern  = r'\[zombie_finder\]: (Passed|Failed)'
            kernel_pattern  = r'\[final score\]: (\d+\.\d{2})/(\d+)'
            zombie_match    = re.search(zombie_pattern, kernel_stdout_output)
            kernel_match    = re.search(kernel_pattern, kernel_stdout_output)

            if zombie_match and kernel_match:
                kernel_status   = zombie_match.group(1)
                kernel_pts      = float(kernel_match.group(1))
                kernel_total    = float(kernel_match.group(2))

                if kernel_status == "Passed":
                    tc_points       += kernel_pts
                    comments        += f"Test Case {num}: Passed with {kernel_pts} out of {kernel_total} points.\n"
                    tc_status       = "Passed"

                else:
                    thread_pattern  = r' - Found (\d+) (producer|consumer) threads, expected (\d+) (-(\d+\.\d{2}) points)'
                    thread_match    = re.search(thread_pattern, kernel_stdout_output)

                    if thread_match:
                        restart_required = True
                        restart_err += "!!!Your kernel module did not properly handle all zombie processes!!!"

                    tc_points           += kernel_pts
                    kernel_module_pass   = False
                    kernel_module_err    = f"Test Case {num}: Failed with {kernel_pts} out of {kernel_total} points because of error: {kernel_stderr_output}"
                    comments            += kernel_module_err + "\n" 
                    tc_status            = "Failed"
                    tc_logs              = kernel_module_err
                    self.print_and_log_error(kernel_module_err)
            else:
                kernel_module_err    = f"Test Failed: For Test Case {num}."
                kernel_module_pass   = False 
                comments            += kernel_module_err + "\n" 
                tc_points            = 0
                tc_status            = "Failed"
                tc_logs              = kernel_module_err
                self.print_and_log_error(kernel_module_err)

        except (subprocess.CalledProcessError, Exception, subprocess.TimeoutExpired)  as e:
            comments            += f"Error executing the script: {e}"
            restart_required     = True
            kernel_module_status = "Failed"
            tc_points            = 0
            tc_status            = "Failed"
            if isinstance(e, subprocess.TimeoutExpired):
                comments        += str(e.stdout)
            tc_logs              = comments

        result = [tc_status, tc_logs, tc_points, comments] 

        return restart_required, result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CSE330 Autograder')
    parser.add_argument('--asuid', type=str, help='ASUID of the student')

    log_file = 'autograder.log'
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger 	= logging.getLogger()
    args 	= parser.parse_args()
    asuid   = args.asuid
    aws_obj = grader_project1(logger, asuid)
