
__copyright__   = "Copyright 2025, VISA Lab"
__license__     = "MIT"

"""
File: grade_project1.py
Author: Kritshekhar Jha
Description: Grading script for Project-1
"""
import re
import os
import pdb
import time
import json
import logging
import argparse
import textwrap
import threading
import subprocess

from evaluate_snapshot import *

class grader_project1():
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

    def validate_lts_release(self, lsb_release_file_path):
        comments        = ""
        total_points    = 50
        points_deducted = 0

        if lsb_release_file_path:
            lsb_status, lsb_extracted_text = check_lts_release(lsb_release_file_path)
            if lsb_status == 'Pass':
                points_deducted = 0
                comments        = "[TC-1-log] lsb_release desired output found.\n"
                self.print_and_log("[TC-1-log] lsb_release desired output found.")

                comments        += f"[TC-1-log] {lsb_extracted_text}\n"
                self.print_and_log(f"[TC-1-log] {lsb_extracted_text}")

                comments        += f"[TC-1-log] Points deducted: {points_deducted}"
                self.print_and_log(f"[TC-1-log] Points deducted: {points_deducted}")
            else:
                points_deducted = total_points
                comments        = "[TC-1-log] lsb_release desired output Not Found. Please validate manually\n."
                self.print_and_log_error("[TC-1-log] lsb_release desired output Not Found. Please validate manually.")

                comments        += f"[TC-1-log] {lsb_extracted_text}\n"
                self.print_and_log_error(f"[TC-1-log] {lsb_extracted_text}")

                comments        += f"[TC-1-log] Points deducted: {points_deducted}"
                self.print_and_log_error(f"[TC-1-log] Points deducted: {points_deducted}")

        else:
            points_deducted = total_points
            comments        = "[TC-1-log] lsb_release file Not Found. Please validate manually. Points deducted: {points_deducted}"
            self.print_and_log(comments)

        return (total_points - points_deducted), comments 

    def validate_uname(self, uname_file_path):
        comments        = ""
        total_points    = 50
        points_deducted = 0

        if uname_file_path:
            uname_status, uname_extracted_text = check_kernel_version(uname_file_path)
            if uname_status == 'Pass':
                points_deducted = 0
                comments        = "[TC-2-log] uname desired output found.\n"
                self.print_and_log("[TC-2-log] uname desired output found.")

                comments        += f"[TC-2-log] {uname_extracted_text}\n"
                self.print_and_log(f"[TC-2-log] {uname_extracted_text}")

                comments        += f"[TC-2-log] Points deducted: {points_deducted}"
                self.print_and_log(f"[TC-2-log] Points deducted: {points_deducted}")
            else:
                points_deducted = total_points
                comments        = "[TC-2-log] uname desired output Not Found. Please validate manually\n."
                self.print_and_log_error("[TC-2-log] uname desired output Not Found. Please validate manually")

                comments        += f"[TC-2-log] {uname_extracted_text}\n"
                self.print_and_log_error(f"[TC-2-log] {uname_extracted_text}")

                comments        += f"[TC-2-log] Points deducted: {points_deducted}"
                self.print_and_log_error(f"[TC-2-log] Points deducted: {points_deducted}")
        else:
            points_deducted = total_points
            comments        = "[TC-2-log] uname file Not Found. Please validate manually. Points deducted: {points_deducted}"
            self.print_and_log(comments)

        return (total_points - points_deducted), comments 

    def main(self, asuid, extracted_folder): 

        test_results = {}
        uname_file_path         = None
        lsb_release_file_path   = None
        image_files             = []

        for root, dirs, files in os.walk(extracted_folder):
            for file in files:
                if file.startswith("uname"):
                    uname_file_path = os.path.join(root, file)
                if file.startswith("lsb_release"):
                    lsb_release_file_path = os.path.join(root, file)
                if file.lower().endswith(('.png', '.jpg')):
                    image_files.append(os.path.join(root, file))

        self.print_and_log("----------------- Executing Test-Case:1 ----------------")
        test_results["tc_2"] = self.validate_lts_release(lsb_release_file_path)
        self.print_and_log("----------------- Executing Test-Case:2 ----------------")
        test_results["tc_3"] = self.validate_uname(uname_file_path)

        grade_points = sum(result[0] for result in test_results.values())
        if grade_points == 99.99: grade_points = 100
        if grade_points < 0: grade_points = 0
        self.print_and_log("--------------------------------------------------------")
        self.print_and_log(f"Total Grade Points: {grade_points}")
        test_results["grade_points"] = grade_points

        return test_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload images')
    parser.add_argument('--asuid', type=str, help='ASUID of the student')

    log_file = 'autograder.log'
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger 	= logging.getLogger()
    args 	= parser.parse_args()
    asuid   = args.asuid
    aws_obj = grader_project1(logger, asuid)
