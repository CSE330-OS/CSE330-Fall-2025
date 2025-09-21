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
import pdb
import csv
import shutil
import zipfile
import argparse
import subprocess
import pandas as pd

#from grade_project3 import *

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

def find_first_failed_test_case(row, num_test_cases):
    for i in range(1, num_test_cases + 1):
        log_col = f"TC-{i}-logs"
        if row.get(log_col, "") == "TODO":
            return i
    return None

def reload_graded_results(logger, grader_results_csv, mode, total_tests):

    last_incomplete_row_logs = []
    previous_grade_points   = 0
    previous_grade_comments = ""

    if mode == 'resume':
        results_df = pd.read_csv(grader_results_csv)
        if not results_df.empty:
            #last_incomplete_row     = results_df[results_df["Grading-Status"] == "In-progress"].iloc[-1]

            try:
                mask = results_df["Grading-Status"] == "In-progress"
                if mask.any():
                    last_incomplete_row 		= results_df[mask].iloc[-1]
                    in_progress_rows 			= results_df[results_df["Grading-Status"] == "In-progress"]
                    last_incomplete_row_index 	= in_progress_rows.index[-1]
                    total_graded_students 		= int(last_incomplete_row_index)
                else:
                    mask = results_df["Grading-Status"] == "TODO"
                    last_incomplete_row = results_df[mask].iloc[0]
                    in_progress_rows 	= results_df[results_df["Grading-Status"] == "TODO"]
                    todo_index = results_df[results_df["Grading-Status"] == "TODO"].index.min()
                    above_todo_df = results_df.loc[:todo_index - 1]
                    graded_df = above_todo_df[above_todo_df["Grading-Status"] != "TODO"]
                    total_graded_students = len(graded_df)

            except KeyError:
                print_and_log_error(logger, "Column 'Grading-Status' not found in DataFrame.")
                last_incomplete_row = None

            last_student_id         = last_incomplete_row['ASUID']
            last_student_name       = last_incomplete_row['Name']

            print_and_log(logger, f'Last student ID found: {last_student_id} Total sudents graded {total_graded_students}')
            last_student_sanity_log = last_incomplete_row['Sanity-logs']

            failed_test = find_first_failed_test_case(last_incomplete_row, total_tests)

            if last_student_sanity_log == "!!! Error !!! Encountered while autograding. VM Freezed.":
                print_and_log(logger, f'Last student ID found: {last_student_id}: Script ran into an error grading for this student so it will resume from the next student please manually grade this students submission')
                total_graded_students += 1
                for id in range(1, total_tests + 1):
                    if id > failed_test:
                        results={}
                        results[f'tc_{id}'] = ["Failed", last_student_sanity_log, 0, last_student_sanity_log]
                        update_test_case_result(results_df, last_student_id, id, results)
                        results_df.to_csv(grader_results_csv, mode='w', header=True, index=False)

            if failed_test and failed_test <= total_tests:
                resume_test_case = failed_test
                print_and_log(logger, f'Resuming from Test-Case-{resume_test_case} for the student. {last_student_name}\n')
                for i in range(1, failed_test):
                    last_incomplete_row_logs.append([last_incomplete_row[f'TC-{i}-status'], last_incomplete_row[f'TC-{i}-logs']])
                previous_grade_points   = float(last_incomplete_row['grade_points'])
                previous_grade_comments = last_incomplete_row['Comments']
            else:
                print_and_log(logger, "All test cases completed. Moving to the next student.\n")
                resume_test_case = 1
        else:
            print_and_log(logger,"The CSV file is empty.")

        return total_graded_students, resume_test_case, results_df, previous_grade_points, previous_grade_comments


def write_data_to_csv(data, csv_path):
    df = pd.DataFrame(data)
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_path, mode='w', header=True, index=False)

def write_df_to_csv(df, csv_path):
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

def find_source_code_path(extracted_folder):
    """Locate the 'source_code' folder inside the extracted directory."""
    for root, dirs, _ in os.walk(extracted_folder):
        if 'source_code' in dirs:
            return os.path.join(root, 'source_code')
    raise FileNotFoundError("source_code folder not found.")

def count_fully_graded_students(logger, output_csv):

    df 				 = pd.read_csv(output_csv)
    columns_to_check = [col for col in df.columns if col not in ["Name", "ASUID"]]

    # Check for rows where all columns to check are NOT "TODO"
    fully_graded_mask 	= ~(df[columns_to_check] == "TODO").any(axis=1)
    graded_students 	= df[fully_graded_mask]
    graded_count 		= len(graded_students)
    if graded_count > 0:
        print_and_log(logger, f"Total sudents graded {graded_count}. Last graded student details:{graded_students.iloc[-1]}")
    else:
        print("No students have been fully graded yet.")
    return graded_count

def create_dummy_results_csv(logger, roster_df, output_csv, num_test_cases):

    if os.path.exists(output_csv):
        os.remove(output_csv)
        print_and_log(logger, f'Found a old version of grading results. Getting rid of it.')

    # Fixed headers
    sanity_headers = ["Grading-Status", "Submission-Found", "Zip-logs", "Sanity-Test", "Sanity-logs"]
    grade_headers  = ["Total grades", "Comments"]

    # Dynamic test case headers
    test_case_headers = []
    for i in range(1, num_test_cases + 1):
        test_case_headers.extend([f"TC-{i}-status", f"TC-{i}-logs", f"TC-{i}-score"])

    # All headers
    all_headers = ["Name", "ASUID"] + sanity_headers + test_case_headers + grade_headers

    # Prepare rows with default "TODO" values
    rows = []
    for _, row in roster_df.iterrows():
        name     = f"{row['Last Name']} {row['First Name']}"
        row_data = {"Name": name,"ASUID": row["ASUID"]}

        for header in sanity_headers + test_case_headers + grade_headers:
            row_data[header] = "TODO"
        rows.append(row_data)

    # Write to output CSV
    with open(output_csv, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_headers)
        writer.writeheader()
        writer.writerows(rows)

    results_df 	= pd.read_csv(output_csv)

    return results_df

def update_test_case_result(df, asuid, test_case_num, test_results):

    if asuid not in df['ASUID'].values:
        raise ValueError(f"ASUID {asuid} not found in CSV.")

    key = f"tc_{test_case_num}"
    if key not in test_results:
        raise ValueError(f"Test case result for {key} not found in test_results.")

    status, logs, score, comments = test_results[key]

    status_col = f"TC-{test_case_num}-status"
    logs_col   = f"TC-{test_case_num}-logs"
    score_col  = f"TC-{test_case_num}-score"
    comments_col = "Comments"

    df.loc[df['ASUID'] == asuid, status_col] = status
    df.loc[df['ASUID'] == asuid, logs_col]   = logs
    df.loc[df['ASUID'] == asuid, score_col]  = score

    existing_comments = df.loc[df['ASUID'] == asuid, comments_col].astype(str)
    updated_comments = existing_comments + f"\n[TC-{test_case_num}] {comments}"
    df.loc[df['ASUID'] == asuid, comments_col] = updated_comments


def extract_zip(logger, zip_path, extract_to):
    """Extract the student's zip file."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print_and_log(logger, f"Submission file: {zip_path} unzipped to folder: {extract_to}")
