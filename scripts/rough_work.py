import csv
import pandas as pd
import os


# def csv_to_txt(csv_file_path, output_directory):
#     # Step 1: Open the .csv file and turn it into a pandas DataFrame
#     df = pd.read_csv(csv_file_path)
#
#     # Step 2: Extract the fourth column
#     # Note: Column indices are 0-based, so the fourth column has index 3
#     fourth_column = df.iloc[:, 3]
#
#     # Ensure the output directory exists
#     os.makedirs(output_directory, exist_ok=True)
#
#     # Step 3: For each cell in the fourth column, save the content into a .txt file
#     for i, content in enumerate(fourth_column):
#         file_path = os.path.join(output_directory, f'cell_{i}.txt')
#         with open(file_path, 'w') as file:
#             file.write(str(content))  # Convert content to string before writing
#
#
# # Example usage
# csv_file_path = './default_prompt.csv'
# output_directory = './default_prompts'
# csv_to_txt(csv_file_path, output_directory)


import csv
import random


def generate_csv(file_path, num_lines):
    # Open the file in write mode
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the header
        writer.writerow(['HW', 'QS', 'Fixed'])

        for _ in range(num_lines):
            col1 = random.randint(1, 10)
            col2 = random.randint(1, 3)
            col3 = False

            # Ensure Col3 is True only if Col1 is not 9 or 10 and with 30% probability
            if col1 not in [3, 4, 5, 6, 9, 10]:
                col3 = random.random() < 0.4

            # Write the row
            writer.writerow([col1, col2, col3])


# Example usage
csv_file_path = './chatgpt_fix_code_logical.csv'
generate_csv(csv_file_path, 500)