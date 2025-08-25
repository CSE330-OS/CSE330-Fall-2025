# Autograder for Project 1

Make sure that you use the provided autograder and follow the instructions below to test your project submission. Failure to do so may cause you to lose all the project points and there will be absolutely no second chance.

- Download the zip file you submitted from Canvas. 
- Download the autograder from GitHub: `https://github.com/CSE330-OS/CSE330-Fall-2025.git`
  - In order to clone the GitHub repository follow the below steps:
  - `git clone https://github.com/CSE330-OS/CSE330-Fall-2025.git`
  - `cd CSE330-Fall-2025/`
  - `git checkout project-1`
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
linustorvalds@cse330:~/Autograder-Fall-2025/Project-1$ python3 autograder.py
+++++++++++++++++++++++++++++++ CSE330 Autograder  +++++++++++++++++++++++++++++++
- 1) The script will first look up for the zip file following the naming conventions as per project document
- 2) The script will then do a sanity check on the zip file to make sure all the expected files are present
- 3) Execute the test cases as per the Grading Rubrics
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++ Autograder Configurations ++++++++++++++++++++++++++++
Grade Project: Project-1
Class Roster: class_roster.csv
Zip folder path: submissions/
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++ Grading for Torvalds  Linus ASUID: 1225754101 +++++++++++++++++++++
Submission file: submissions/project-1-1225754101.zip unzipped to folder: extracted
File found: extracted/uname.png
File found: extracted/lsb_release.png
----------------- Executing Test-Case:1 ----------------
[TC-1-log] lsb_release desired output found.
[TC-1-log] Linustorvaldscse33: lsb_release a No LSB modules are available. Distributor ID: Ubuntu Description: Ubuntu 24.04.3 LTS Release: 24.04 Codename: noble Linustorvaldscse330: Jj
[TC-1-log] Points deducted: 0
----------------- Executing Test-Case:2 ----------------
[TC-2-log] uname desired output found.
[TC-2-log] linustorvaldscse330: uname a Linux cse33 6.16.2CSE330Fall225LinusTorvalds 1 SMP PREEMPT_DYNAMIC Thu Aug 21 16:53:25 UTC 225 aarch6o4 aarch64 aarch6o4 GNULinux Linustorvaldscse330: fj
[TC-2-log] Points deducted: 0
--------------------------------------------------------
Total Grade Points: 100
Removed extracted folder: extracted
Grading completed for Torvalds  Linus ASUID: 1225754101
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Grading complete for Project-1. Check the Project-1-grades.csv file.
linustorvalds@cse330:~/Autograder-Fall-2025/Project-1$
```
