"""
File: grade_project2.py
Author: Kritshekhar Jha
Description: Grading script for Project-2
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

from evaluate_snapshot import *

class grader_project2():
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

    def validate_syscall_output(self, asuid, zip_folder_path, zip_file):

        comments        = ""
        total_points    = 50
        points_deducted = 0

        try:
            zip_file_path = os.path.join(zip_folder_path, f'tmp-{asuid}')
            os.makedirs(zip_file_path, exist_ok=True)
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(zip_file_path)

            syscall_file_path   = None
            image_files         = []

            for root, dirs, files in os.walk(zip_file_path):
                for file in files:
                    if file.startswith("syscall_output"):
                        syscall_file_path = os.path.join(root, file)
                    if file.lower().endswith(('.png', '.jpeg')):
                        image_files.append(os.path.join(root, file))

            if syscall_file_path:
                syscall_status, syscall_extracted_text = check_syscall_output(syscall_file_path)
                if syscall_status == 'Pass':
                    points_deducted = 0
                    comments = "[TC-1-log] syscall_output correct.\n"
                    self.print_and_log("[TC-1-log] syscall_output correct.")

                    comments += f"[TC-1-log] Points deducted: {points_deducted}"
                    self.print_and_log(f"[TC-1-log] Points deducted: {points_deducted}")
                else:
                    points_deducted = total_points
                    comments = "[TC-1-log] syscall_output doesn't have desired output.Please validate manually\n"
                    self.print_and_log_error(f"[TC-1-log] syscall_output doesn't have desired output.Please validate manually")

                    comments += f"[TC-1-log] Points deducted: {points_deducted}"
                    self.print_and_log_error(f"[TC-1-log] Points deducted: {points_deducted}")
            else:
                points_deducted = total_points
                comments        = "[TC-1-log] syscall_output file Not Found. Please validate manually. Points deducted: {points_deducted}"
                self.print_and_log(comments)

            shutil.rmtree(zip_file_path)

        except (subprocess.CalledProcessError, Exception) as e:
            self.print_and_log_error(f"[TC-1-log] Error executing the script: {e}")
            self.print_and_log_error(f"[TC-1-log] Script Error (stderr): {e.stderr}")
            points_deducted = total_points
            self.print_and_log_error(f"[TC-1-log] Points deducted: {points_deducted}")

        return (total_points - points_deducted), comments

    def validate_kernel_module(self, zip_folder_path, zip_file, test_module_script):

        comments            = ""
        kernel_module_err   = ""
        total_points        = 50
        points_deducted     = 0
        restart_required    = False

        try:
            result_kernel        = subprocess.run([test_module_script, zip_file], capture_output=True, text=True, check=True)
            kernel_stdout_output = result_kernel.stdout
            kernel_stderr_output = result_kernel.stderr
            #self.print_and_log("[TC-2-log] test_module: Script Output (stdout):")
            #self.print_and_log(kernel_stdout_output)

            if kernel_stderr_output:
                self.print_and_log_error("[TC-2-log] test_module: Script Error (stderr):")
                self.print_and_log_error(kernel_stderr_output)

            kernel_pattern              = r'\[my_module\]: (Passed|Failed) with (\d+) out of (\d+)'
            total_score_kernel_pattern  = r'\[Total Score\]: (\d+) out of (\d+)'

            kernel_match = re.search(kernel_pattern, kernel_stdout_output)
            if kernel_match:
                kernel_status   = kernel_match.group(1)
                kernel_pts      = int(kernel_match.group(2))
                kernel_total    = int(kernel_match.group(3))
                points_deducted = kernel_total - kernel_pts

                 # Assign points based on pass/fail status
                if kernel_status == "Passed":
                    comments        = f"[TC-2-log] Kernel module test passed.\n"
                    self.print_and_log(f"[TC-2-log] Kernel module test passed. {kernel_stdout_output}")
                else:
                    kernel_module_err    = f"[Tc-2-log] Kernel module test failed with {kernel_pts} out of {kernel_total} points because of error: {kernel_stdout_output}"
                    self.print_and_log_error(kernel_module_err)
                    comments            += kernel_module_err + "\n"
                    kernel_module_pass   = False
            else:
                kernel_module_err    = f"[TC-2-log] Test Failed: test_module Sanity Failed."
                self.print_and_log_error(kernel_module_err)
                comments            += kernel_module_err + "\n"
                kernel_module_pass   = False

            # Check the total score from the test output
            kernel_total_match = re.search(total_score_kernel_pattern, kernel_stdout_output)
            if kernel_total_match:
                kernel_total_pts        = int(kernel_total_match.group(1))
                kernel_total_possible   = int(kernel_total_match.group(2))
                points_deducted         = (total_points - kernel_total_pts)
                points_comments         = f"[TC-2-log] Points deducted:{points_deducted}"
                self.print_and_log(points_comments)
                comments                += points_comments + "\n"

        except (subprocess.CalledProcessError, Exception) as e:
            points_deducted     = total_points
            kernel_module_err   = f"[TC-2-log] Error executing the script: {e}. Points deducted:{points_deducted}"
            self.print_and_log_error(kernel_module_err)
            comments            += kernel_module_err + "\n"

        if "rmmod: ERROR" in kernel_module_err:
            restart_required = True

        return (total_points - points_deducted), comments, restart_required

    def main(self, asuid, zip_folder_path, zip_file, extracted_folder, test_module_script):

        test_results        = {}
        syscall_file_path   = None
        image_files         = []

        for root, dirs, files in os.walk(extracted_folder):
            for file in files:
                if file.startswith("syscall_output"):
                    uname_file_path = os.path.join(root, file)
                if file.lower().endswith(('.png', '.jpg')):
                    image_files.append(os.path.join(root, file))

        self.print_and_log("----------------- Executing Test-Case:1 ----------------")
        test_results["tc_2"] = self.validate_syscall_output(asuid, zip_folder_path, zip_file)
        self.print_and_log("----------------- Executing Test-Case:2 ----------------")
        test_results["tc_3"] = self.validate_kernel_module(zip_folder_path, zip_file, test_module_script)

        grade_points = sum(result[0] for result in test_results.values())
        if grade_points == 99.99: grade_points = 100
        if grade_points < 0: grade_points = 0
        self.print_and_log("--------------------------------------------------------")
        self.print_and_log(f"Total Grade Points: {grade_points}")
        self.print_and_log("--------------------------------------------------------")
        test_results["grade_points"] = grade_points

        return test_results

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
