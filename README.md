# Autograder for Project 5

Make sure that you use the provided autograder and follow the instructions below to test your project submission. Failure to do so may cause you to lose all the project points and there will be absolutely no second chance.

- Download the zip file you submitted from Canvas. 
- Download the autograder from GitHub: `https://github.com/CSE330-OS/CSE330-Fall-2025.git`
  - In order to clone the GitHub repository follow the below steps:
  - `git clone https://github.com/CSE330-OS/CSE330-Fall-2025.git`
  - `cd CSE330-Fall-2025/`
  - `git checkout project-5`
- Create a directory `submissions` in the CSE330-Fall-2025 directory and move your zip file to the submissions directory.
- Implement your code in the provided template `dm_lru.c`. Do not make any changes to the other files.

## Prepare to run the autograder
- Install all the dependencies using the provided script `install.sh`
- Populate the `class_roster.csv`
- Add a 2GB virtual disk as the source device and a 1GB virtual disk as the cache device to your VM. Follow the instructions below based on your hypervisor
  - [UTM](https://docs.google.com/document/d/1FzgmOhXvqnyospJ3lSYJWFGDs8GnrFcXZMB_HYWVeck/edit?usp=sharing) 
  - [VMWare](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/7-0/vsphere-virtual-machine-administration-guide-7-0/configuring-virtual-machine-hardwarevm-admin/virtual-disk-configurationvm-admin/add-a-hard-disk-to-a-virtual-machinevm-admin/add-a-new-hard-disk-to-a-virtual-machinevm-admin.html)
  - [Virtualbox](https://progmar.net.pl/en/knowledge-base/virtualbox-adding-removing-disk-drive)
  
  After you have added the source and the cache device you can list all the available devices using `lsblk` command in your VM. Refer to the snapshot below where `/dev/nvme0n2` is the source device and     `/dev/nvme0n3` is the cache device. Note that the specific device names shown in your VM may be different. You can identify them by their sizes.
    <img width="583" height="242" alt="image" src="https://github.com/user-attachments/assets/20f75c11-9b2b-4673-8f54-c764d0e97182" />

## Usage of the autograder 
```
linustorvalds@cse330:~/Autograder-Fall-2025/Project-5$ python3 autograder.py --help
usage: autograder.py [-h] [--mode {start,resume}] --devX DEVX --devY DEVY
CSE330 Autograder
options:
  -h, --help            show this help message and exit
  --mode {start,resume} grading mode
  --devX DEVX           Source Device
  --devY DEVY           Cache Device
linustorvalds@cse330:~/Autograder-Fall-2025/Project-5$
```

## Run the autograder
- To run the autograder: ```sudo python3 autograder.py --devX "nvme0n2" --devY "nvme0n3```
  
Note: Replace `nvme0n2` and `nvme0n3` as per your test setup. 
- The autograder will look for submissions for each entry present in the class_roster.csv
- For each submission the autograder:
  - Extracts the required files from the submission and parses the entries.
  - Test the project as per the grading rubrics and allocate grade points.
    
## Sample Output

```
linustorvalds@cse330:~/GTA-CSE330-Fall-2025/Project-5/grading$ python3 autograder.py --devX "nvme0n2" --devY "nvme0n3"
/home/linustorvalds/.local/lib/python3.12/site-packages/pandas/core/arrays/masked.py:61: UserWarning: Pandas requires version '1.3.6' or newer of 'bottleneck' (version '1.3.5' currently installed).
  from pandas.core import (
+++++++++++++++++++++++++++++++ CSE330 Autograder  +++++++++++++++++++++++++++++++
- 1) The script will first look up for the zip file following the naming conventions as per project document
- 2) The script will then do a sanity check on the zip file to make sure all the expected files are present
- 3) Execute the test cases as per the Grading Rubrics
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++ Autograder Configurations ++++++++++++++++++++++++++++
Grade Project: Project-5
Class Roster: class_roster.csv
Zip folder path: submissions/
Source Device: /dev/nvme0n2
Cache Device: /dev/nvme0n3
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++ Grading for Torvalds Linus ASUID: 1225754101 +++++++++++++++++++++
Submission file: submissions/project-5-1225754101.zip unzipped to folder: extracted
[Sanity check] File found: extracted/source_code/dm_lru.c
Found dm_lru.c  at extracted/source_code/dm_lru.c
Copied 'dm_lru.c' to /home/linustorvalds/GTA-CSE330-Fall-2025/Project-5/grading
Make stdout:
make -C /lib/modules/6.16.2CSE330Fall2025LinusTorvalds/build/ M=/home/linustorvalds/GTA-CSE330-Fall-2025/Project-5/grading modules
make[1]: Entering directory '/home/linustorvalds/linux-6.16.2'
make[2]: Entering directory '/home/linustorvalds/GTA-CSE330-Fall-2025/Project-5/grading'
  CC [M]  dm_cache.o
  CC [M]  dm_lru.o
  LD [M]  dmcache.o
  MODPOST Module.symvers
  CC [M]  dmcache.mod.o
  CC [M]  .module-common.o
  LD [M]  dmcache.ko
make[2]: Leaving directory '/home/linustorvalds/GTA-CSE330-Fall-2025/Project-5/grading'
make[1]: Leaving directory '/home/linustorvalds/linux-6.16.2'

----------------- Executing Test-Case:1 ----------------
Running test case 1: source device:/dev/nvme0n2 cache device:/dev/nvme0n3 hit_ratio:0.0
[sudo] password for linustorvalds:
Test Case 1: Script Output: [log]: Module loaded successfully
[log]: Creating cache
[log]: └─ echo 0 4194304 cache /dev/nvme0n2 /dev/nvme0n3 8 262144 | sudo dmsetup create cache
[log]: Checking cache status
[log]: └─ sudo dmsetup status cache
[log]: Issue a 1024MB read workload
[log]: └─ sudo fio --filename=/dev/mapper/cache --name=test --rw=read --direct=1 --size=1024MB --numjobs=1
[log]: Checking cache status
[log]: └─ sudo dmsetup status cache
[log]: Checking data read from source device
[log]: └─ 1024.0MB read from source device expected 1024MB
[log]: Checking number of cache misses
[log]: └─ Found 262144 misses expected 262144
[log]: Removing cache
[log]: └─ sudo dmsetup remove cache
[log]: Module unloaded successfully
Final score: 33.33
[dmcache]: Passed (33.33/33.33)

----------------- Executing Test-Case:2 ----------------
Running test case 2: source device:/dev/nvme0n2 cache device:/dev/nvme0n3 hit_ratio:0.5
Test Case 2: Script Output: [log]: Module loaded successfully
[log]: Creating cache
[log]: └─ echo 0 4194304 cache /dev/nvme0n2 /dev/nvme0n3 8 262144 | sudo dmsetup create cache
[log]: Issue a 512MB read workload
[log]: └─ sudo fio --filename=/dev/mapper/cache --name=test --rw=read --direct=1 --size=512MB --numjobs=1
[log]: Checking cache status
[log]: └─ sudo dmsetup status cache
[log]: Issue a 1024MB read workload
[log]: └─ sudo fio --filename=/dev/mapper/cache --name=test --rw=read --direct=1 --size=1024MB --numjobs=1
[log]: Checking cache status
[log]: └─ sudo dmsetup status cache
[log]: Checking data read from source device
[log]: └─ 512.0MB read from source device expected 512MB
[log]: Checking data read from cache device
[log]: └─ 512.0MB read from cache device expected 512MB
[log]: Checking number of cache misses
[log]: └─ Found 131072 misses expected 131072
[log]: Checking number of cache hits
[log]: └─ Found 131072 hits expected 131072
[log]: Removing cache
[log]: └─ sudo dmsetup remove cache
[log]: Module unloaded successfully
Final score: 33.33
[dmcache]: Passed (33.33/33.33)

----------------- Executing Test-Case:3 ----------------
Running test case 3: source device:/dev/nvme0n2 cache device:/dev/nvme0n3 hit_ratio:1.0
Test Case 3: Script Output: [log]: Module loaded successfully
[log]: Creating cache
[log]: └─ echo 0 4194304 cache /dev/nvme0n2 /dev/nvme0n3 8 262144 | sudo dmsetup create cache
[log]: Issue a 1024MB read workload
[log]: └─ sudo fio --filename=/dev/mapper/cache --name=test --rw=read --direct=1 --size=1024MB --numjobs=1
[log]: Checking cache status
[log]: └─ sudo dmsetup status cache
[log]: Issue a 1024MB read workload
[log]: └─ sudo fio --filename=/dev/mapper/cache --name=test --rw=read --direct=1 --size=1024MB --numjobs=1
[log]: Checking cache status
[log]: └─ sudo dmsetup status cache
[log]: Checking data read from cache device
[log]: └─ 1024.0MB read from cache device expected 1024MB
[log]: Checking number of cache hits
[log]: └─ Found 262144 hits expected 262144
[log]: Removing cache
[log]: └─ sudo dmsetup remove cache
[log]: Module unloaded successfully
Final score: 33.33
[dmcache]: Passed (33.33/33.33)

--------------------------------------------------------
Total Grade Points: 100
--------------------------------------------------------
Removed extracted folder: extracted
Removed file: /home/linustorvalds/GTA-CSE330-Fall-2025/Project-5/grading/dm_lru.c
Grading completed for Torvalds Linus ASUID: 1225754101
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Grading complete for Project-5. Check the Project-5-grades.csv file.
```

