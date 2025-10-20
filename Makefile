# Makefile in the grading folder

# Define the path to the source code directory
SOURCE_CODE_DIR = extracted/source_code

# Define the target for compiling the kernel module
all:
	@echo "Entering the source code directory: $(SOURCE_CODE_DIR)"
	@cd $(SOURCE_CODE_DIR) && make

# Define a target to clean up the source code folder (optional)
clean:
	@echo "Cleaning the source code directory: $(SOURCE_CODE_DIR)"
	@cd $(SOURCE_CODE_DIR) && make clean
