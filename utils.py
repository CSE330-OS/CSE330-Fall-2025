#!/usr/bin/python3

__copyright__   = "Copyright 2025, VISA Lab"
__license__     = "MIT"

"""
File: utils.py
Author: Kritshekhar Jha
Description: Utilities file
"""
import re
import os
import shutil
import zipfile
import subprocess
import pandas as pd

from grade_project2 import *

def print_and_log(logger, message):
    print(message)
    logger.info(message)

def print_and_log_error(logger, message):
    print(message)
    logger.error(message)

def is_none_or_empty(string):
    return string is None or string.strip() == ""

def print_and_log_warn(logger, message):
    print(message)
    logger.warn(message)

def reload_graded_results(logger, grader_results_csv):
    if os.path.exists(grader_results_csv):
        results_df = pd.read_csv(grader_results_csv)
        if not results_df.empty:
            last_row                = results_df.iloc[-1]
            last_student_id         = last_row['ASUID']
            total_graded_students   = len(results_df)
            print_and_log(logger, f'Last student ID found: {last_student_id} Total sudents graded {total_graded_students}')
            return total_graded_students
        else:
            print_and_log_error(logger, "The CSV file is empty.")
    else:
        print_and_log_error(f"The file {grader_results_csv} does not exist.")

def write_to_csv(data, csv_path):
    df = pd.DataFrame(data)
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_path, mode='w', header=True, index=False)

def del_directory(logger, directory_name):
    try:
        if os.path.exists(directory_name) and os.path.isdir(directory_name):
            shutil.rmtree(directory_name)
            print_and_log(logger, f"Removed extracted folder: {directory_name}")
    except Exception as e:
        print_and_log_error(logger, f"Could not remove extracted folder {directory_name}: {e}")

def extract_zip(logger, zip_path, extract_to):
    """Extract the student's zip file."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print_and_log(logger, f"Submission file: {zip_path} unzipped to folder: {extract_to}")

def check_file_exists(logger, base, extensions):
	found = False
	for ext in extensions:
		path = base + ext
		if os.path.exists(path):
			print_and_log(logger, f"[Sanity check] File found: {path}")
			found = True
			break
	if not found:
		print_and_log_error(logger, f"[Sanity check] file {base} not found !!")

	return found

def append_grade_remarks(results, name, asuid, tc_0_status, tc_0_logs, tc_1_status, tc_1_logs,
                        tc_2_pts, tc_2_logs,
                        tc_3_pts, tc_3_logs,
                        grade_points, grade_comments):

    results = []
    results.append({'Name': name, 'ASUID': asuid, 'Submission-Found': tc_0_status, 'zip-logs': tc_0_logs,
                    'Sanity-Test': tc_1_status, 'Sanity-logs': tc_1_logs,
                    'Test-1-score': tc_2_pts, 'Test-1-logs': tc_2_logs,
                    'Test-2-score': tc_3_pts, 'Test-2-logs': tc_3_logs,
                    'Total Grades':grade_points, 'Comments':grade_comments})
    return results
