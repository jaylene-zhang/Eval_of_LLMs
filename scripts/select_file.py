import csv
import random

# Function to randomly select n lines from a CSV file
def random_lines(file_path, n):
    lines = []
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        lines = [line for line in reader]
    return random.sample(lines, n)

# Paths to your 10 CSV files
csv_files = [
    "/Volumes/天地梅花开/compileCodehw1.csv",
    "/Volumes/天地梅花开/compileCodehw2.csv",
    "/Volumes/天地梅花开/compileCodehw3.csv",
    "/Volumes/天地梅花开/compileCodehw4.csv",
    "/Volumes/天地梅花开/compileCodehw5.csv",
    "/Volumes/天地梅花开/compileCodehw6.csv",
    "/Volumes/天地梅花开/compileCodehw7.csv",
    "/Volumes/天地梅花开/compileCodehw8.csv",
    "/Volumes/天地梅花开/compileCodehw9.csv",
    "/Volumes/天地梅花开/compileCodehw10.csv",
]

# Randomly select 5 lines from each CSV file
selected_lines = []
for file in csv_files:
    selected_lines.extend(random_lines(file, 5))

# Write the selected lines to a new CSV file
output_file = "selected_lines.csv"
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(selected_lines)

print("Selected lines have been written to:", output_file)
