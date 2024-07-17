#!/usr/bin/env python3
from pprint import pprint
import re
import os
import subprocess
import sys
import csv
from typing import Optional, Tuple, Dict, List
from argparse import ArgumentParser
from pathlib import Path
import hashlib

# we need from the user the path to the split homework submissions
parser = ArgumentParser(
    description=
    'A script to grade the homeworks on a question by question basis')
parser.add_argument('--hw_dir',
                    type=str,
                    required=True,
                    help='The directory of the homework you wish to grade')
parser.add_argument('-e', help="Exit the script on error")

# TODO -> function to save the grades to the filesystem / database


def compute_max_grade(exercise_path: str, solution_file: str) -> str:
    """
    input: exercise directory, question for which to get the max grade
    output: max grade for that question
    
    1. split the solution file,
    2. for each split, run it against the grader
    3. parse the points obtained to get the max points for that question
    """
    # TODO
    pass


def parse_max_grades(grades_path: str) -> Optional[Dict[str, str]]:
    """
    Reads the points from a json file in the folder otherwise return None
    input: path to a json file containing the grades for each question
    output: json string containing the maximum grades per question
    """
    # TODO
    pass


def parse_points(grader_output: str) -> int:
    """
    input: the output from the grader
    output: the grade obtained, None if not found
    """
    res = re.findall('(\d+ points)', grader_output)
    if len(res) > 0:
        return int(res[0].split()[0])

    return 0


def parse_errors(report_txt: str) -> Dict[str, str]:
    """
    input: text from a generated report
    output: dict containing the number of errors based on the following
            categories :- type errors
                        - syntax errors
                        - pattern matching
                        - unused variables
                        - argument application
                        - unbound values
    """
    errors = {
        'type_errors':
        re.findall('This expression has type', report_txt, re.IGNORECASE),
        'syntax_errors':
        re.findall('Syntax Error', report_txt, re.IGNORECASE),
        'pattern_match_not_exhaustive':
        re.findall('pattern-matching is not exhaustive', report_txt,
                   re.IGNORECASE),
        'unused_variable':
        re.findall('unused variable', report_txt, re.IGNORECASE),
        'unbound_value':
        re.findall('unbound value', report_txt, re.IGNORECASE),
        'argument_application':
        re.findall('too many arguments', report_txt, re.IGNORECASE),
    }

    return errors


def parse_error_category_count(report_txt: str) -> int:
    """
    input: text from the generated report
    ouput: total number of errors
    """
    errors = parse_errors(report_txt)

    return sum([len(errs) for errs in errors.values()])


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
    report_name = '-'.join([submission.parts[-2], submission.parts[2]])

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


def write_header(csv_file: str, fields: List[str]) -> None:
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()


def write_info(id: str,
               info,
               fields: List[str]) -> None:
    """
    Write the grade and error count information into a csv file.
    Assumes the csv file already has a header
    """
    with open(hw_csv, 'a', newline='') as f:
        writer = csv.DictWriter(f, fields)
        writer.writerows(info)


if __name__ == '__main__':
    args = parser.parse_args()

    # check that the directory exists
    hw_parent_dir = Path(args.hw_dir)
    if not hw_parent_dir.exists():
        print('Invalid homework directory, please ensure the directory exists')
        sys.exit(1)

    hw_dirs = list(
        filter(lambda x: x.is_dir() and ('grade' in x.name or 'compile' in x.name),
               hw_parent_dir.iterdir()))

    for hw_dir in hw_dirs[0:1]:
        print(f"hw_dir: {hw_dir}")
        q_dirs = sorted(list(filter(lambda x: 'q' in x.name,
                                    hw_dir.iterdir())))
        print(f"q_dirs: {q_dirs}")
        hw_solution_dir = hw_dir.joinpath('exercise')
        hw_csv = f'{hw_dir}.csv'
        hw_program_transformation_csv = f'{hw_dir}_transformations.csv'
        event_key = 'grade' if 'grade' in hw_dir.name else 'compile'
        
        header = ['id', 'timestamp', 'question', 'grade', 'error_count', 'event_key']
        transformations_header = ['id', 'version', 'event_key']
        write_header(hw_csv, header)
        write_header(hw_program_transformation_csv, transformations_header)

        # grade the questions for each student
        for q_dir in q_dirs:
            student_sub_dirs = list(
                filter(lambda x: '.' not in x.name,
                       q_dir.joinpath('student_submissions').iterdir()))
            for student_sub_dir in student_sub_dirs[0:1]:
                sorted_submissions = sorted(student_sub_dir.iterdir(),
                                            key=lambda x: x.stem)

                prev_submission: Optional[str] = None
                prev_grade: Optional[int] = None
                error_count: int = 0

                # keep track of program transformations, as a list of
                # sha256 digests
                encountered_programs = list()
                
                for submission in sorted_submissions:
                    encountered_programs.append({'id': student_sub_dir.name,
                                                 'sha256sum': hashlib.sha256(submission.encode()).hexdigest(),
                                                 'event_key': event_key
                                                 })
                    # grade submission, record results in a csv file
                    # keep track of the previous submission and score
                    grader_text, report_txt_filename = grade_submission(
                        submission, hw_solution_dir)

                    if not (grader_text
                            and report_txt_filename):
                        print(
                            f'Encountered error while grading question\
                            {q_dir.name} for student {student_sub_dir.name}'
                        )
                        if args.e == 'exit':
                            sys.exit(-1)
                        continue

                    if 'Failure' not in grader_text and not (Path(report_txt_filename).exists()):
                        # count errors here
                        error_count += parse_error_category_count(grader_text) if grader_text else 0

                    grade = parse_points(grader_text)
                    submission_text = Path(submission).read_text()

                    # check if the submission is the same as the last one
                    if grade == prev_grade and submission_text == prev_submission:
                        # a duplicate submission, skip this
                        continue
                    
                    # otherwise, write the information to the csv files
                    timestamp = submission.name.split('.')[0]
                    
                    write_info([{'id': student_sub_dir.name,
                                'timestamp': timestamp,
                                'question': q_dir.name,
                                'grade': grade,
                                'error_count': error_count,
                                'event_key': event_key
                                }],
                               hw_csv,
                               header)

                    prev_grade = grade
                    prev_submission = submission_text

                    # delete dumped reports
                    for report_file in Path().glob('*.report.*'):
                        report_file.unlink()

                # store info about encountered program versions in
                # a separate csv
                write_info(encountered_programs,
                           hw_program_transformation_csv,
                           transformations_header)
