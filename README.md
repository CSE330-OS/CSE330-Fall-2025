# Autograder for Project 4

Make sure that you use the provided autograder and follow the instructions below to test your project submission. Failure to do so may cause you to lose all the project points and there will be absolutely no second chance.

- Download the zip file you submitted from Canvas. 
- Download the autograder from GitHub: `https://github.com/CSE330-OS/CSE330-Fall-2025.git`
  - In order to clone the GitHub repository follow the below steps:
  - `git clone https://github.com/CSE330-OS/CSE330-Fall-2025.git`
  - `cd CSE330-Fall-2025/`
  - `git checkout project-4`
- Create a directory `submissions` in the CSE330-Fall-2025 directory and move your zip file to the submissions directory.

## Prepare to run the autograder
- Install all the dependencies using the provided script `install.sh`
- Populate the `class_roster.csv`
- You MUST only allocate 4GB of RAM to ensure the test scripts can trigger swapping.
- You MUST enable swap on your VM. Check if swap is enabled using `free -h`; if not you can follow below steps on how to enable swap using a swapfile
  - For example to have 1GB swap, create a 1 GiB file (`/mnt/1GiB.swap`) to use as swap:
  - `sudo dd if=/dev/zero of=/mnt/1GiB.swap bs=1024 count=1048576`
  - Set the swap file permissions to `600` to prevent other users from being able to read potentially sensitive information from the swap file `sudo chmod 600 /mnt/1GiB.swap`
  - Format the file as swap:  `sudo mkswap /mnt/1GiB.swap`
  - Enable use of swap:  `sudo swapon /mnt/1GiB.swap`
  - Swap is now available and can also be verified with: `sudo cat /proc/swaps`
  - To enable swap file at bootup add the swap file details to `/etc/fstab` so it will be available at bootup:
    `echo '/mnt/1GiB.swap swap swap defaults 0 0' | sudo tee -a /etc/fstab`
    
- The script reads multiple files from procfs and `/var/log/kern.log` to validate your code. Hence the script MUST always be run with sudo.
- You must compile a C source, `testp5.c` file into a binary before proceeding with autograder.py. Please read the README for more details. You can use the given [Makefile](https://github.com/CSE330-OS/CSE330-Fall-2025/tree/sample-code/project-4) for this.
- To test virtual addresses that are present in physical memory, the test script will disable swap and allocate 1GB of memory (to ensure they do not get swapped out during the testing).
- To test virtual addresses that are in swap, the test script will enable swap and should perform a much larger memory allocation to ensure pages are being moved to swap. We suggest you allocate as much as the memory size of your VM.
- Since this script reads `/var/log/kern.log` and multiple files from procfs to validate your output, it ***MUST*** be run with `sudo`.

## Run the autograder
- To run the autograder: ```sudo python3 autograder.py```
- The autograder will look for submissions for each entry present in the class_roster.csv
- For each submission the autograder:
  - Extracts the required files from the submission and parses the entries.
  - Test the project as per the grading rubrics and allocate grade points.
    
## Sample Output

```
linustorvalds@cse330:~/Autograder-Fall-2025/Project-4$ sudo python3 autograder.py
+++++++++++++++++++++++++++++++ CSE330 Autograder  +++++++++++++++++++++++++++++++
- 1) The script will first look up for the zip file following the naming conventions as per project document
- 2) The script will then do a sanity check on the zip file to make sure all the expected files are present
- 3) Execute the test cases as per the Grading Rubrics
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++ Autograder Configurations ++++++++++++++++++++++++++++
Grade Project: Project-4
Class Roster: class_roster.csv
Zip folder path: submissions/
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++ Grading for Torvalds Linus ASUID: 1225754101 +++++++++++++++++++++
Submission file: submissions/project4-1225754101.zip unzipped to folder: extracted
[Sanity check] File found: extracted/source_code/memory_manager.c
[Sanity check] File found: extracted/source_code/Makefile
Make stdout:
Entering the source code directory: extracted/source_code
make[1]: Entering directory '/home/linustorvalds/Autograder-Fall-2025/Project-4/extracted/source_code'
make -C /lib/modules/6.16.2CSE330Fall2025LinusTorvalds/build M=/home/linustorvalds/Autograder-Fall-2025/Project-4/extracted/source_code modules
make[2]: Entering directory '/home/linustorvalds/linux-6.16.2'
make[3]: Entering directory '/home/linustorvalds/Autograder-Fall-2025/Project-4/extracted/source_code'
  CC [M]  memory_manager.o
  MODPOST Module.symvers
  CC [M]  memory_manager.mod.o
  CC [M]  .module-common.o
  LD [M]  memory_manager.ko
make[3]: Leaving directory '/home/linustorvalds/Autograder-Fall-2025/Project-4/extracted/source_code'
make[2]: Leaving directory '/home/linustorvalds/linux-6.16.2'
make[1]: Leaving directory '/home/linustorvalds/Autograder-Fall-2025/Project-4/extracted/source_code'

----------------- Executing Test-Case:1 ----------------
Running test case 1: scalar=1, num_present=100, num_swapped=0, num_invalid=0
Test Case 1: Script Output: [log]: Disable swap
[log]: Waiting for 5 seconds to allow pages to be present and/or to be moved to swap
[log]: Checking 100 random present pages
[log]: - 100/100 correct
[log]: Enabling swap
[memory_manager]: Passed (100.0/100)

----------------- Executing Test-Case:2 ----------------
Running test case 2: scalar=4, num_present=0, num_swapped=100, num_invalid=0
Test Case 2: Script Output: [log]: Enabling swap
[log]: Waiting for 5 seconds to allow pages to be present and/or to be moved to swap
[log]: Checking 100 random swapped pages
[log]: - 100/100 correct
[memory_manager]: Passed (100.0/100)

----------------- Executing Test-Case:3 ----------------
Running test case 3: scalar=1, num_present=0, num_swapped=0, num_invalid=100
Test Case 3: Script Output: [log]: Disable swap
[log]: Waiting for 5 seconds to allow pages to be present and/or to be moved to swap
[log]: Checking 100 random invalid pages
[log]: - 100/100 correct
[log]: Enabling swap
[memory_manager]: Passed (100.0/100)

--------------------------------------------------------
Total Grade Points: 100.0
--------------------------------------------------------
Removed extracted folder: extracted
Grading completed for Torvalds Linus ASUID: 1225754101
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Grading complete for Project-4. Check the Project-4-grades.csv file.
linustorvalds@cse330:~/Autograder-Fall-2025/Project-4$
```

