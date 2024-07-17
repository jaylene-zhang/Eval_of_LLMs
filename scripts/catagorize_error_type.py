import os
import pprint
import re
import subprocess
from typing import Optional, Tuple, Dict, List
import pandas as pd
from datetime import datetime


def grade_submission(
        solution_folder: str,
        submission_path: str
) -> Tuple[str, str]:
    """
    input: the path to the student submission, the path to the
           solution FOLDER
    output: the text output from the grader, and the path to the
            generated report as a string
    output: a tuple containing the grade obtained and an error if the
            grader did not successfully run. If the grader failed to run
            the grade obtained is -1
    """
    # report_name = os.path.relpath(submission_path, "/Users/jaylene/Desktop/LLM_Eval")
    # report_name = os.path.relpath(submission_path,'./F2022/exercises')
    report_name = submission_path
    report_cmd = f'learn-ocaml grade --exercises={str(solution_folder)} --grade-student={str(submission_path)} --timeout 60 --dump-reports {report_name}'

    try:
        print(f"running learn-ocaml grade ... ...")
        process = subprocess.run(report_cmd,
                                 shell=True,
                                 timeout=120,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 check=False)
        print(f"generating report {report_name}.report.txt ... ...")
        return process.stdout.decode('utf8'), f'{report_name}.report.txt'
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return '0', 'Error'

def extract_year(date_string):
    match = re.search(r'\d{4}', date_string)
    return int(match.group()) if match else None


def filter_by_year(df, column_name, year=2021):
    # Apply function to 'dates' column
    df['year'] = df[column_name].apply(extract_year)
    # Filter rows where year is 2021
    filtered_df = df[df['year'] == year]
    return filtered_df


def filter(input, output):
    df = pd.read_csv(input)
    filtered_df = filter_by_year(df, df.columns[1])
    filtered_df.to_csv(output, index=False)

def catag_error_type(grader_output):
    grade = grader_output[0]
    if "Error" in grade: # the code cannot compile
        pattern = r"Error(.*?)grader outcomes:"
        match = re.search(pattern, grade)
        if match:
            content_between = match.group(1).strip()
            if "Syntax error" in content_between:
                print("syntax error")
            elif "type" in content_between:
                print("type error")
            elif "unbound value" in content_between:
                print("unbound value")
        else:
            print("No match found")
    else:
        print("the code compiled successfully...")




def main():
    '''clean the data, keep only 2021'''
    # for hw in range(1,11):
    #     file_path = f'/Users/jaylene/Downloads/fall2022_student_submission/compileCodehw{hw}.csv'
    #     output_path = f'/Users/jaylene/Downloads/fall2022_student_submission/compileCodehw{hw}_filtered.csv'
    #     filter(file_path, output_path)

    '''categorize the data'''
    grade_submission("./F2022/exercises/hw5", "./hw5_q1.ml")


if __name__ == "__main__":
    main()
