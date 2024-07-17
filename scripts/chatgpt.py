import openai
import os
import pprint
import re
import subprocess
from typing import Optional, Tuple, Dict, List



# from openai import OpenAI
# client = OpenAI(api_key="479598b156a14cd9be17526d38778c8b")


openai.api_type = "azure"
openai.api_base = "https://reap-gpt-access.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = "479598b156a14cd9be17526d38778c8b"

'''functions for interacting with chatgpt'''
def get_chatgpt_response(messages):
  response = openai.ChatCompletion.create(
                engine="reap-gpt4-1106-access",
                messages = messages,
                temperature=0.7,
                max_tokens=800,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)

  return response.choices[0].message.content

# prompt = "do you know about OCaml?"
# messages = [{"role":"system","content":"You are an AI assistant that helps people program in OCaml."}, {"role": "user", "content": prompt}]

def update_chat(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages

def extract_ocaml_code(response_text):
    ocaml_code_blocks = re.findall(r'```ocaml\s+(.*?)```', response_text, re.DOTALL)
    code = "\n".join(ocaml_code_blocks)
    with open('./model_response', 'w') as file:
        file.write(code)  # Convert content to string before writing
    return code


'''ask the model to generate response w/ feedback'''
def stream_prompt2(messages):
    i = 0
    loop = 'T'
    pprint.pprint(f"___________ attempt {i+1} ___________")
    # pprint.pprint(messages)
    model_response = get_chatgpt_response(messages)
    # print(f"------------ model response ------------")
    # print(model_response, '\n')

    print(f"------------ model code extracted ------------")
    print(extract_ocaml_code(model_response)[0])
    # print(model_response)

    loop = input("Should I continue the loop? Enter T/F ")
    while loop == 'T':
        # new prompt
        i += 1
        pprint.pprint(f"___________ attempt {i+1} ___________")
        new_prompt = input()
        messages = update_chat(messages, "user", new_prompt)
        model_response = get_chatgpt_response(messages)
        # stop += 3
        print(model_response, '\n')
        loop = input("Should I continue the loop? Enter T/F")
        # messages = update_chat(messages, "assistant", model_response)

'''ask the model to generate response wo feedback'''
def stream_prompt(messages):
    # with open('./model_response', 'w') as file:
    #     for i in range(5):
    #         pprint.pprint(f"___________ attempt {i+1} ___________")
    #         # pprint.pprint(messages)
    #         model_response = get_chatgpt_response(messages)
    #         # print(f"------------ model response ------------")
    #         # print(model_response, '\n')
    #         # code = extract_ocaml_code(model_response)[0]
    #         with open('./model_response', 'a') as file:
    #             file.write(str(i+1))
    #             file.write('\n')
    #
    #             file.write(model_response)  # Convert content to string before writing
    #             file.write('\n')
    model_response = get_chatgpt_response(messages)
    return model_response



'''grader'''

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
    report_name = os.path.relpath(submission_path,'./F2022/exercises')
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




'''prompt'''
# prompt = read_file('./default_prompts/6_4.txt')
# print(prompt)

prompt = ''' 
I will give you a buggy ocaml program, a fixed version of it, and two edit scripts that you are gonna decide which one is better.
Some advice in choosing the better edit script will follow. Feel free to add to it or disagree.
1. The edit script should avoid meaningless changes. That is, if a subtree or token needs to be used, no edit should apply to it. The script should not DELETE and re-INSERT it to the tree.
2. The edit script should be high-level and readable. That is, if we need to replace a token with a new one. The best edit is to update this token, rather than deleting it and inserting the new token at the same location.
3. The edit script should be structural-aware. If a subtree should be placed to somewhere else, then the operation should just be a single MOVE, rather than deleting and re-inserting it to the new location.
The code is as follows:
"** source code **"
let join x l = x :: l;;
let rec listReverse l =
  match l with | [] -> [] | hd::tl -> join (listReverse tl) hd;;
** fixed code **
let join x l = l :: x;;
let rec listReverse l =
  match l with | [] -> [] | hd::tl -> join (listReverse tl) hd;;
The two edit scripts are as follows:
** edit script1 **
===
move-tree
---
::: :: [18,20]
to
cons_expression [16,22]
at 2
===
move-tree
---
value_path [16,17]
    value_name: x [16,17]
to
cons_expression [16,22]
at 2
** edit script2 **
===
move-tree
---
value_path [16, 17]
    value_name: x [16, 17]
---
to
cons_expression [16, 22]
at 3
===
===
move-tree
---
value_path [21, 22]
    value_name: l [21, 22]
---
to
cons_expression [16, 22]
at 1
===
'''

messages = [{"role":"system","content":"Hi. I have an OCaml program for you. Later on, I am going to send you an edit script. Your job is to follow strictly the edits to change the OCaml code. Give me the changed code only."},
            {"role": "user", "content": prompt}]
res = stream_prompt(messages)
print(res)

'''grade '''
# grade = grade_submission("./F2022/exercises/hw6", "./model_response")

# print('____________')
# print(len(grade))
# print(grade[0])

