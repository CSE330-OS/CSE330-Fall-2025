# Autograder for Project 2

Make sure that you use the provided autograder and follow the instructions below to test your project submission. Failure to do so may cause you to lose all the project points and there will be absolutely no second chance.

- Download the zip file you submitted from Canvas. 
- Download the autograder from GitHub: `https://github.com/CSE330-OS/CSE330-Fall-2025.git`
  - In order to clone the GitHub repository follow the below steps:
  - `git clone https://github.com/CSE330-OS/CSE330-Fall-2025.git`
  - `cd CSE330-Fall-2025/`
  - `git checkout project-2`
- Create a directory `submissions` in the CSE330-Fall-2025 directory and move your zip file to the submissions directory.

## Prepare to run the autograder
- Install all the dependencies using the provided script `install.sh`
- Populate the `class_roster.csv`
 
## Run the autograder
- To run the autograder: ```python3 autograder.py```
- The autograder will look for submissions for each entry present in the class_roster.csv
- For each submission the autograder:
  - Extracts the required files from the submission and parses the entries.
  - Test the project as per the grading rubrics and allocate grade points.
    
## Sample Output

```
linustorvalds@cse330:~/GTA-CSE330-Fall-2025/Project-2/grading$ python3 autograder.py
+++++++++++++++++++++++++++++++ CSE330 Autograder  +++++++++++++++++++++++++++++++
- 1) The script will first look up for the zip file following the naming conventions as per project document
- 2) The script will then do a sanity check on the zip file to make sure all the expected files are present
- 3) Execute the test cases as per the Grading Rubrics
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++ Autograder Configurations ++++++++++++++++++++++++++++
Grade Project: Project-2
Class Roster: class_roster.csv
Zip folder path: submissions/
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++ Grading for  Torvalds  Linus ASUID: 1225754101 +++++++++++++++++++++
Removed extracted folder: extracted
Submission file: submissions/project-2-1225754101.zip unzipped to folder: extracted
[Sanity check] File found: extracted/module/my_module.c
[Sanity check] File found: extracted/module/Makefile
[Sanity check] File found: extracted/syscall/my_syscall.c
[Sanity check] File found: extracted/syscall/Makefile
[Sanity check] File found: extracted/userspace/syscall_in_userspace_test.c
[Sanity check] File found: extracted/screenshot/syscall_output.png
Sanity Test Passed: Enough files found to proceed with grading.
----------------- Executing Test-Case:1 ----------------
[TC-1-log] Extracted text: Linustorvaldscse33: GTACSE330Fall2025Project2my_syscall gcc o syscall_in_userspace_test syscall_in_userspace_test.c Linustorvaldscse330: GTACSE330Fall2025Project2my_syscall .syscall_in_userspace_test my_syscall returned Linustorvaldscse33: GTACSE330Fall2025Project2my_syscall sudo dmesg tail n 1 sudo password for Linustorvalds: 34695 .616215 This is the new system call Linus Torvalds implemented. Linustorvaldscse330: GTACSE330Fall2025Project2my_syscall Jj
Pass
[TC-1-log] syscall_output correct.
[TC-1-log] Points deducted: 0
----------------- Executing Test-Case:2 ----------------
[TC-2-log] Kernel module test passed. Unzipping to "unzip_1756323140"
[log]: Look for kernel_module directory
[log]: - directory /home/linustorvalds/GTA-CSE330-Fall-2025/Project-2/grading/unzip_1756323140/module found
[log]: Look for Makefile
[log]: - file /home/linustorvalds/GTA-CSE330-Fall-2025/Project-2/grading/unzip_1756323140/module/Makefile found
[log]: Look for source file (my_module.c)
[log]: - file /home/linustorvalds/GTA-CSE330-Fall-2025/Project-2/grading/unzip_1756323140/module/my_module.c found
[log]: Compile the kernel module
[log]: - Compiled successfully
[log]: Load the kernel module
[log]: - Loaded successfully
[log]: Check dmesg output
[log]: - Output is correct
[log]: Unload the kernel module
[log]: - Kernel module unloaded successfully
[my_name]: Passed with 50 out of 50
[Total Score]: 50 out of 50
[TC-2-log] Points deducted:0
--------------------------------------------------------
Total Grade Points: 100
--------------------------------------------------------
Removed extracted folder: extracted
Grading completed for  Torvalds  Linus ASUID: 1225754101
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Grading complete for Project-2. Check the Project-2-grades.csv file.
```
