import os
import subprocess
from pprint import pprint
import re
import sys
import csv
from typing import Optional, Tuple, Dict, List
from argparse import ArgumentParser
from pathlib import Path
import hashlib


def grade_submission(
        submission_path: str,
        solution_folder: str) -> Tuple[str, str]:
    """
    input: the path to the student submission, the path to the
           solution folder
    output: the text output from the grader, and the path to the
            generated report as a string
    output: a tuple containing the grade obtained and an error if the
            grader did not successfully run. If the grader failed to run
            the grade obtained is -1
    """
    report_name = os.path.relpath(submission_path, "/Users/jaylene/Desktop/LLM_Eval")
    report_cmd = f'learn-ocaml grade --exercises={str(solution_folder)} --grade-student={str(submission_path)} --timeout 60 --dump-reports {report_name}'

    try:
        print(f"running learn-ocaml grade ... ...")
        process = subprocess.run(report_cmd,
                                 shell=True,
                                 timeout=120,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 check=False)
        return process.stdout.decode('utf8'), f'{report_name}.report.txt'
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return '0', 'Error'


def iterate_questions(homework_list, soln_list):
    """Iterate over question directories."""
    for i, hw in enumerate(homework_list):
        # hw: .../hw1, .../hw2
        question_dirs = sorted(list(
            filter(lambda x: x.is_dir() and ('qs' in x.name),
                   hw.iterdir())))  # [qs_1, qs_2, ..]
        sol_path = soln_list[i + 2]  # exercises/hw1, exercises/hw2
        for qs in question_dirs:  # qs: .../qs_1
            code_files = sorted(list(qs.iterdir()))  # [.ml files]
            for file in code_files:
                grade_submission(str(file), str(sol_path))


def iterate_homeworks(semester_path):
    """Iterate over homework directories."""
    semester_path = Path(semester_path)
    # print(semester_path)
    hw_dirs = sorted(list(
        filter(lambda x: x.is_dir() and ('exercises' not in x.name),
               semester_path.iterdir())))
    soln_dirs = os.path.join(semester_path, 'exercises')
    soln_dirs = sorted(list(Path(soln_dirs).iterdir()))
    return hw_dirs, soln_dirs


def iterate_semesters(root_dir, target_semester):
    """Iterate over semester directories."""
    semester_path = os.path.join(root_dir, target_semester)
    if not os.path.isdir(semester_path):
        print(f"Semester '{target_semester}' not found.")
        return
    print(f"------- getting paths within {semester_path}  ... ------")
    return iterate_homeworks(semester_path)


if __name__ == '__main__':
    # Root directory where all semesters' homework submissions are located
    root_directory = '/Users/jaylene/Desktop/LLM_Eval'

    # Example: Grading for Fall 2022 semester and dumping reports to 'reports' directory
    hws, solns = iterate_semesters(root_directory, 'F2022')
    iterate_questions(hws, solns)
