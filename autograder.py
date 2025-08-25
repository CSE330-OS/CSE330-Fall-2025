#!/bin/python3

__copyright__   = "Copyright 2025, VISA Lab"
__license__     = "MIT"

"""
File: autograder.py
Author: Kritshekhar Jha
"""

import os
import pdb
import sys
import glob
import shutil
import zipfile
import logging
import subprocess
import pandas as pd
import importlib.util

from utils import *
from evaluate_snapshot import *

grade_project       = "Project-1"
roster_csv          = 'class_roster.csv'
grader_results_csv  = f'Project-1-grades.csv'
zip_folder_path     = f'submissions/'
script_path         = 'evaluate_snapshot.py'

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

roster_df 	= pd.read_csv(roster_csv)
results 	= []

for index, row in roster_df.iterrows():

    first_name  = row['First Name']
    last_name   = row['Last Name']
    name        = f"{row['Last Name']} {row['First Name']}"
    asuid       = row['ASUID']

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

        uname_path          = "extracted/uname"
        uname_exists		= check_file_exists(logger, uname_path, [".png",".jpg"])
        lsb_release_path    = "extracted/lsb_release"
        lsb_release_exists  = check_file_exists(logger, lsb_release_path, [".png",".jpg"])

        if not uname_exists or not lsb_release_exists:
            sanity_pass     = False
            sanity_status   = "Fail"
            test_comments   = f"Sanity Test Failed: All expected files not found. Please check if the zip follows the correct structure as per the project document."
            test_script_err = ""
        else:
            sanity_pass     = True
            sanity_status   = "Pass"
            test_comments   = "Sanity Test Passed: All expected files found."
            test_err        = ""
            test_script_err = ""

        grade_comments  += test_comments

        if sanity_pass:

            sanity_comment = "Unzip submission and check folders/files: PASS"
            cse330_grader  = grader_project1(logger, asuid)
            test_results   = cse330_grader.main(asuid, extracted_folder)

            grade_points    = test_results["grade_points"]
            grade_comments += test_results["tc_2"][1]
            grade_comments += test_results["tc_3"][1]

            results = append_grade_remarks(results, name, asuid, sanity_status, sanity_comment,
                                           "Pass", "Files Found!!", test_results["tc_2"][0], test_results["tc_2"][1],
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
        sanity_status           = False
        sanity_comment          = f"Submission File (.zip) not found for {asuid}."
        print_and_log_error(logger, sanity_comment)
        grade_comments      	+= "{sanity_comment} There is a possiblity that student has either misspelled their asuid or student did not submit the assignment. Kindly validate manually."
        print_and_log_error(logger, f"{sanity_comment} There is a possiblity that student has either misspelled their asuid or student did not submit the assignment. Kindly validate manually.")

        tc_2_pts = tc_3_pts = grade_points = 0
        results = append_grade_remarks(results, name, asuid, sanity_status, sanity_comment,
                                       "Fail",   grade_comments, tc_2_pts, grade_comments,
                                       tc_3_pts, grade_comments, grade_points, grade_comments)

    write_to_csv(results, grader_results_csv)

    print_and_log(logger, f"Grading completed for {last_name} {first_name} ASUID: {asuid}")
    print_and_log(logger, "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    logger.handlers[0].flush()

print_and_log(logger, f"Grading complete for {grade_project}. Check the {grader_results_csv} file.")		
