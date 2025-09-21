# Autograder for Project 3

Make sure that you use the provided autograder and follow the instructions below to test your project submission. Failure to do so may cause you to lose all the project points and there will be absolutely no second chance.

- Download the zip file you submitted from Canvas. 
- Download the autograder from GitHub: `https://github.com/CSE330-OS/CSE330-Fall-2025.git`
  - In order to clone the GitHub repository follow the below steps:
  - `git clone https://github.com/CSE330-OS/CSE330-Fall-2025.git`
  - `cd CSE330-Fall-2025/`
  - `git checkout project-3`
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
+++++++++++++++++++++++++++++++ CSE330 Autograder  +++++++++++++++++++++++++++++++
- 1) The script will first look up for the zip file following the naming conventions as per project document
- 2) The script will then do a sanity check on the zip file to make sure all the expected files are present
- 3) Execute the test cases as per the Grading Rubrics
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++ Autograder Configurations ++++++++++++++++++++++++++++
Project Path: None
Grade Project: Project-3
Class Roster: class_roster.csv
Zip folder path: submissions/
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Found an old version of grading results. Getting rid of it.
++++++++++++++++++ Grading for Torvalds Linus ASUID: 1225754101 +++++++++++++++++++++
Submission file: submissions/project-3-1225754101.zip unzipped to folder: extracted
----------------- Executing Test-Case:1 ----------------
Running test case 1: prod=1, cons=0, size=5, regular processes=0, zombies processes=0
[sudo] password for linustorvalds:
Test Case 1: Script Output: [log]: Creating user TestP4...
[log]: Look for Makefile
[log]: ─ file /home/linustorvalds/GTA-CSE330-Fall-2025/Project-3/grading/extracted/source_code/Makefile found
[log]: Look for source file (producer_consumer.c)
[log]: ─ file /home/linustorvalds/GTA-CSE330-Fall-2025/Project-3/grading/extracted/source_code/producer_consumer.c found
[log]: Compile the kernel module
[log]: ─ Compiled successfully
[log]: Starting 0 normal processes
[log]: Load the kernel module
[log]: ─ Loaded successfully
[log]: Checking the counts of the running kernel threads
[log]: ─ Found all expected threads
[log]: We will now wait some time to give your kernel module time to cleanup
[log]: └─ We will wait 10 seconds
[log]: Checking the pids of all remaining processes against your output
[info]: There are no consumers, so we will make sure items are produced but not consumed
[log]: ┬─ All zombies were produced
[log]: └─ None of the regular processes were consumed
[log]: Unload the kernel module
[log]: ─ Kernel module unloaded successfully
[log]: Checking to make sure kthreads are terminated
[log]: ─ All threads have been stopped
[zombie_finder]: Passed
[final score]: 25.00/25
[log]: Deleting user TestP4…

----------------- Executing Test-Case:2 ----------------
Running test case 2: prod=0, cons=5, size=5, regular processes=0, zombies processes=10
Test Case 2: Script Output: [log]: Creating user TestP4...
[log]: Look for Makefile
[log]: ─ file /home/linustorvalds/GTA-CSE330-Fall-2025/Project-3/grading/extracted/source_code/Makefile found
[log]: Look for source file (producer_consumer.c)
[log]: ─ file /home/linustorvalds/GTA-CSE330-Fall-2025/Project-3/grading/extracted/source_code/producer_consumer.c found
[log]: Compile the kernel module
[log]: ─ Compiled successfully
[log]: Starting 0 normal processes
[log]: Load the kernel module
[log]: ─ Loaded successfully
[log]: Starting zombie processes ...
[log]: ─ Total zombies spawned so far: 10/10
[log]: Checking the counts of the running kernel threads
[log]: ─ Found all expected threads
[log]: We will now wait some time to give your kernel module time to cleanup
[log]: └─ We will wait 10 seconds
[log]: Checking the pids of all remaining processes against your output
[info]: There are no producers, so we will make sure no items are produced or consumed
[log]: ┬─ Zero zombies were produced
[log]: └─ None of the regular processes were consumed
[log]: Unload the kernel module
[log]: ─ Kernel module unloaded successfully
[log]: Checking to make sure kthreads are terminated
[log]: ─ All threads have been stopped
[zombie_finder]: Passed
[final score]: 25.00/25
[log]: Deleting user TestP4...

----------------- Executing Test-Case:3 ----------------
Running test case 3: prod=1, cons=10, size=5, regular processes=0, zombies processes=10
Test Case 3: Script Output: [log]: Creating user TestP4...
[log]: Look for Makefile
[log]: ─ file /home/linustorvalds/GTA-CSE330-Fall-2025/Project-3/grading/extracted/source_code/Makefile found
[log]: Look for source file (producer_consumer.c)
[log]: ─ file /home/linustorvalds/GTA-CSE330-Fall-2025/Project-3/grading/extracted/source_code/producer_consumer.c found
[log]: Compile the kernel module
[log]: ─ Compiled successfully
[log]: Starting 0 normal processes
[log]: Load the kernel module
[log]: ─ Loaded successfully
[log]: Starting zombie processes ...
[log]: ─ Total zombies spawned so far: 10/10
[log]: Checking the counts of the running kernel threads
[log]: ─ Found all expected threads
[log]: We will now wait some time to give your kernel module time to cleanup
[log]: └─ We will wait 10 seconds
[log]: Checking the pids of all remaining processes against your output
[log]: - All 10 zombie processes were correctly produced.
[log]: - All 10 zombies were successfully consumed.
[log]: - All zombie PIDs were validly produced.
[log]: - All zombie PIDs were validly consumed.
[log]: - All zombie PIDs correctly produced and consumed.
[log]: ┬─ All zombies were consumed
[log]: └─ None of the regular processes were consumed
[log]: Unload the kernel module
[log]: ─ Kernel module unloaded successfully
[log]: Checking to make sure kthreads are terminated
[log]: ─ All threads have been stopped
[zombie_finder]: Passed
[final score]: 25.00/25
[log]: Deleting user TestP4...

----------------- Executing Test-Case:4 ----------------
Running test case 4: prod=1, cons=20, size=10, regular processes=50, zombies processes=50
Test Case 4: Script Output: [log]: Creating user TestP4...
[log]: Look for Makefile
[log]: ─ file /home/linustorvalds/GTA-CSE330-Fall-2025/Project-3/grading/extracted/source_code/Makefile found
[log]: Look for source file (producer_consumer.c)
[log]: ─ file /home/linustorvalds/GTA-CSE330-Fall-2025/Project-3/grading/extracted/source_code/producer_consumer.c found
[log]: Compile the kernel module
[log]: ─ Compiled successfully
[log]: Starting 50 normal processes
[log]: Load the kernel module
[log]: ─ Loaded successfully
[log]: Starting zombie processes ...
[log]: ─ Total zombies spawned so far: 10/50
[log]: ─ Total zombies spawned so far: 20/50
[log]: ─ Total zombies spawned so far: 30/50
[log]: ─ Total zombies spawned so far: 40/50
[log]: ─ Total zombies spawned so far: 50/50
[log]: Checking the counts of the running kernel threads
[log]: ─ Found all expected threads
[log]: We will now wait some time to give your kernel module time to cleanup
[log]: └─ We will wait 10 seconds
[log]: Checking the pids of all remaining processes against your output
[log]:: number of zombies: 50
[log]: - All 50 zombie processes were correctly produced.
[log]: - All 50 zombies were successfully consumed.
[log]: - All zombie PIDs were validly produced.
[log]: - All zombie PIDs were validly consumed.
[log]: - All zombie PIDs correctly produced and consumed.
[log]: ┬─ All zombies were consumed
[log]: └─ None of the regular processes were consumed
[log]: Unload the kernel module
[log]: ─ Kernel module unloaded successfully
[log]: Checking to make sure kthreads are terminated
[log]: ─ All threads have been stopped
[zombie_finder]: Passed
[final score]: 25.00/25
[log]: Deleting user TestP4...

--------------------------------------------------------
Total Grade Points: 100.0
--------------------------------------------------------
Removed extracted folder: extracted
Grading completed for Torvalds Linus ASUID: 1225754101
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Grading complete for Project-3. Check the Project-3-grades.csv file.

```
