# Autograder for Project 2

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
```
