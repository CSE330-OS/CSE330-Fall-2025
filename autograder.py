#!/bin/python3

__copyright__   = "Copyright 2025, VISA Lab"
__license__     = "MIT"

"""
File: autograder.py
Author: Kritshekhar Jha
"""

import os
import sys
import pdb
import glob
import shutil
import zipfile
import logging
import argparse
import subprocess
import pandas as pd
import importlib.util

from utils import *
from evaluate_snapshot import *

parser = argparse.ArgumentParser(description='Project path')
parser.add_argument('--mode', type=str, required=False, choices=['start', 'resume'], help='grading mode', default='start')

args            = parser.parse_args()
arg_mode        = args.mode

grade_project           = "Project-2"
roster_csv              = 'class_roster.csv'
grader_results_csv      = f'Project-2-grades.csv'
zip_folder_path         = f'submissions/'
test_module_script      = f'{os.getcwd()}/test_module.sh'

log_file = 'autograder.log'
logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
        )
logger = logging.getLogger()

print_and_log(logger, f'+++++++++++++++++++++++++++++++ CSE330 Autograder  +++++++++++++++++++++++++++++++')
print_and_log(logger, "- 1) The script will first look up for the zip file following the naming conventions as per project document")
print_and_log(logger, "- 2) The script will then do a sanity check on the zip file to make sure all the expected files are present")
print_and_log(logger, "- 3) Execute the test cases as per the Grading Rubrics")
print_and_log(logger, "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

print_and_log(logger, f'++++++++++++++++++++++++++++ Autograder Configurations ++++++++++++++++++++++++++++')
print_and_log(logger, f"Grade Project: {grade_project}")
print_and_log(logger, f"Class Roster: {roster_csv}")
print_and_log(logger, f"Zip folder path: {zip_folder_path}")
print_and_log(logger, "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

roster_df 	     = pd.read_csv(roster_csv)
results 	     = []
restart_required = False

if args.mode == 'resume':
    # If mode is 'resume', find the last row of the file
    total_graded_students = reload_graded_results(logger, grader_results_csv)

for index, row in roster_df.iterrows():

    first_name  = row['First Name']
    last_name   = row['Last Name']
    name        = f"{row['Last Name']} {row['First Name']}"
    asuid       = row['ASUID']

    if args.mode == 'resume' and index < total_graded_students:
        continue

    print_and_log(logger, f'++++++++++++++++++ Grading for {last_name} {first_name} ASUID: {asuid} +++++++++++++++++++++')
    grade_points 	= 0
    grade_comments 	= ""
    pattern 		= os.path.join(zip_folder_path, f'*-{asuid}*.zip')
    zip_files 		= glob.glob(pattern)

    if zip_files and os.path.isfile(zip_files[0]):

        zip_file 	= zip_files[0]
        sanity_pass = False

        extracted_folder = f'extracted'
        del_directory(logger, extracted_folder)
        extract_zip(logger, zip_file, extracted_folder)

        km_c                = check_file_exists(logger, "extracted/module/my_module", [".c"])
        km_makefile         = check_file_exists(logger, "extracted/module/Makefile", [""])
        km_syscall          = check_file_exists(logger, "extracted/syscall/my_syscall", [".c"])
        ksyscall_makefile   = check_file_exists(logger, "extracted/syscall/Makefile", [""])
        userspace_test      = check_file_exists(logger, "extracted/userspace/syscall_in_userspace_test", [".c"])
        syscall_img         = check_file_exists(logger, "extracted/screenshot/syscall_output", [".png",".jpg"])

        if syscall_img or (km_c and km_makefile) or ( km_syscall and ksyscall_makefile and userspace_test):
            sanity_pass     = True
            sanity_status   = "Pass"
            test_comments   = "Sanity Test Passed: Enough files found to proceed with grading."
            test_results    = []
        else:
            sanity_pass     = False
            sanity_status   = "Fail"
            test_comments   = f"Sanity Test Failed: All expected files not found. Please check if the zip follows the correct structure as per the project document."
            test_results    = []

        print_and_log(logger, test_comments)
        grade_comments  += test_comments
        results         = test_results

        if sanity_pass:

            sanity_comment = "Unzip submission and check folders/files: PASS"
            cse330_grader  = grader_project2(logger, asuid)
            test_results   = cse330_grader.main(asuid, zip_folder_path, zip_file, extracted_folder, test_module_script)

            grade_points     = test_results["grade_points"]
            grade_comments  += test_results["tc_2"][1] + "\n"
            grade_comments  += test_results["tc_3"][1]
            grade_comments  += f"Total Grade Points: {grade_points}"
            restart_required = test_results["tc_3"][2]

            if km_syscall == False:
                # -25 pts for missing my_syscall.c
                grade_points    -= 25
                message         = "[Grade-Penalty] Points deducted: 25. syscall/my_syscall.c file not found."
                grade_comments  += message
                grade_comments  += f"Final Grade Points: {grade_points}"
                print_and_log(logger, message)
                print_and_log(logger, "--------------------------------------------------------")
                print_and_log(logger, f"Final Grade Points: {grade_points}")
                print_and_log(logger, "--------------------------------------------------------")

            if userspace_test == False:
                # -25 pts for missing syscall_in_userspace_testc
                grade_points -= 25
                print_and_log(logger, "--------------------------------------------------------")
                message         = "[Grade-Penalty] Points deducted: 25. userspace/syscall_in_userspace_test.c file not found."
                grade_comments  += message
                grade_comments  += f"Final Grade Points: {grade_points}"
                print_and_log(logger, message)
                print_and_log(logger, "--------------------------------------------------------")
                print_and_log(logger, f"Final Grade Points: {grade_points}")
                print_and_log(logger, "--------------------------------------------------------")

            if grade_points < 0: grade_points = 0

            results = append_grade_remarks(results, name, asuid, sanity_status, sanity_comment,
                                           "Pass", "Enough files found to proceed with grading !!", test_results["tc_2"][0], test_results["tc_2"][1],
                                           test_results["tc_3"][0], test_results["tc_3"][1], grade_points, grade_comments)

            del_directory(logger, extracted_folder)
        else:
            sanity_comment = f"Unzip submission and check folders/files: FAIL {test_comments}"
            grade_comments += sanity_comment
            tc_2_pts = tc_3_pts = grade_points = 0

            results = append_grade_remarks(results, name, asuid, sanity_status, sanity_comment,
                                           "Fail",   grade_comments, tc_2_pts, grade_comments,
                                           tc_3_pts, grade_comments, grade_points, grade_comments)

            del_directory(logger, extracted_folder)


    else:
        sanity_status           = "Fail"
        sanity_comment          = f"Submission File (.zip) not found for {asuid}."
        print_and_log_error(logger, sanity_comment)
        grade_comments      	+= f"{sanity_comment}.There is a possiblity that student has either misspelled their asuid or student did not submit the assignment. Kindly validate manually."
        print_and_log_error(logger, f"{sanity_comment} There is a possiblity that student has either misspelled their asuid or student did not submit the assignment. Kindly validate manually.")

        tc_2_pts = tc_3_pts = grade_points = 0
        results = append_grade_remarks(results, name, asuid, sanity_status, sanity_comment,
                                       "Fail",   grade_comments, tc_2_pts, grade_comments,
                                       tc_3_pts, grade_comments, grade_points, grade_comments)

    write_to_csv(results, grader_results_csv)

    print_and_log(logger, f"Grading completed for {last_name} {first_name} ASUID: {asuid}")
    print_and_log(logger, "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    if restart_required:
        print_and_log (logger, f'!!!!!!! WARNING !!!!!! : Error encountered while grading for student {last_name} {first_name}. Please reboot your vm and rerun the autograder in resume mode')
        print_and_log(logger, "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        break
    logger.handlers[0].flush()

print_and_log(logger, f"Grading complete for {grade_project}. Check the {grader_results_csv} file.")
