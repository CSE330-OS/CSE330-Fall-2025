#!/bin/bash

# Zip format compliance
TOTAL_FILES=0
TOTAL_DIRS=0
EXTRA_FILES=""

# Kernel module correctness
KERNEL_MODULE_NAME="my_module"
KERNEL_MODULE_ERR=""
KERNEL_MODULE_MSG=""
KERNEL_MODULE_PTS=0
KERNEL_MODULE_TOTAL=50

# System call correctness
SYSCALL_ERR=""
SYSCALL_MSG=""
SYSCALL_PTS=0
SYSCALL_TOTAL=50

# Resubmission correctness
RESUBMIT_ERR=""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

check_file ()
{
    local file_name=$(realpath "$1" 2>/dev/null)

    if [ -e ${file_name} ]; then
        let TOTAL_FILES=TOTAL_FILES+1
        echo "[log]: - file ${file_name} found"
        return 0
    else
        return 1
    fi
}

check_dir ()
{
    local dir_name=$(realpath "$1" 2>/dev/null)

    if [ -d ${dir_name} ]; then
        let TOTAL_DIRS=TOTAL_DIRS+1
        echo "[log]: - directory ${dir_name} found"
        return 0
    else
        return 1
    fi
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

compile_module ()
{
    pushd "module" 1>/dev/null
    make_err=$(make 2>&1 1>/dev/null)

    if [ $? -ne 0 ] ; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-50 points) Failed to compile your kernel module: ${make_err}"
        popd 1>/dev/null
        return 1
    fi

    echo "[log]: - Compiled successfully"
    popd 1>/dev/null
    return 0
}

load_module_with_params ()
{
    pushd "module" 1>/dev/null

    # Check to make sure kernel object exists
    if [ ! -e "${KERNEL_MODULE_NAME}.ko" ]; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-20 points) Failed to find your kernel object ${KERNEL_MODULE_NAME}.ko"
        popd 1>/dev/null
        return 1
    fi

    # Insert kernel module - check exit code
    sudo dmesg -C
    sudo insmod "${KERNEL_MODULE_NAME}.ko" charParameter="Fall" intParameter=2025
    if [ $? -ne 0 ]; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-20 points) Insmod exitted with non-zero return code"
        popd 1>/dev/null
        return 1
    fi

    # Check lsmod to make sure module is loaded
    if ! lsmod | grep -q "^${KERNEL_MODULE_NAME}"; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-20 points) Kernel module does not appear in lsmod"
        return 1
    fi

    popd 1>/dev/null
    return 0
}

check_module_output ()
{
    local output=`sudo dmesg`
    if ! echo ${output} | grep -E "$1" 1>/dev/null; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-20 points) Incorrect output: ${output}"
        echo "[log]: - Output incorrect: ${output}"
        return 1
    fi

    return 0
}

unload_module ()
{
    sudo dmesg -C && sudo rmmod "${KERNEL_MODULE_NAME}"

    # Checking for successful module removal
    if lsmod | grep -q "^${KERNEL_MODULE_NAME}"; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-10 points) Failed to unload kernel module"
        echo "[log]: - Failed to unload kernel module"
        return 1
    fi

    return 0
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

check_kernel_module ()
{
    local STATUS=0

    # Step 1: Check directory - stop if failed
    echo "[log]: Look for module directory"
    if ! check_dir "module"; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-50 points) Failed to find module directory"
        return 1
    fi

    # Step 2: Check Makefile - stop if failed
    echo "[log]: Look for Makefile"
    if ! check_file "module/Makefile"; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-50 points) Failed to find your Makefile"
        return 1
    fi

    # Step 3: Check my_module.c - stop if failed
    echo "[log]: Look for source file (my_module.c)"
    if ! check_file "module/my_module.c"; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-50 points) Failed to find your my_module.c source file"
        return 1
    fi

    # Step 4: Compile the kernel module - stop if failed
    echo "[log]: Compile the kernel module"
    if ! compile_module; then
        return 1
    fi

    # Step 5: Load the kernel module - stop if failed
    echo "[log]: Load the kernel module"
    if ! load_module_with_params; then
        return 1
    else
        echo "[log]: - Loaded successfully"
        let KERNEL_MODULE_PTS=KERNEL_MODULE_PTS+20
    fi

    # Step 6: Check output
    echo "[log]: Check dmesg output"
    if ! check_module_output "Hello, I am .*, a student of CSE330 Fall 2025"; then
        let STATUS=1
    else
        echo "[log]: - Output is correct"
        let KERNEL_MODULE_PTS=KERNEL_MODULE_PTS+20
    fi

    # Step 7: Unload module
    echo "[log]: Unload the kernel module"
    if ! unload_module; then
        let STATUS=1
    else
        echo "[log]: - Kernel module unloaded successfully"
        let KERNEL_MODULE_PTS=KERNEL_MODULE_PTS+10
    fi

    return $STATUS
}

check_system_call ()
{
    # Step 1: Check directory - stop if failed
    echo "[log]: Look for kernel_syscall directory"
    if ! check_dir "kernel_syscall"; then
        SYSCALL_ERR="${SYSCALL_ERR}\n - (-50 points) Failed to find kernel_syscall directory"
        return 1
    fi

    # Step 2: Check Makefile - stop if failed
    echo "[log]: Look for Makefile"
    if ! check_file "kernel_syscall/Makefile"; then
        SYSCALL_ERR="${SYSCALL_ERR}\n - (-50 points) Failed to find your Makefile"
        return 1
    fi

    # Step 3: Check my_syscall.c - stop if failed
    echo "[log]: Look for source file (my_syscall.c)"
    if ! check_file "kernel_syscall/my_syscall.c"; then
        SYSCALL_ERR="${SYSCALL_ERR}\n - (-50 points) Failed to find your my_syscall.c source file"
        return 1
    fi

    # Step 4: Check directory - stop if failed
    echo "[log]: Look for userspace directory"
    if ! check_dir "userspace"; then
        SYSCALL_ERR="${SYSCALL_ERR}\n - (-50 points) Failed to find userspace directory"
        return 1
    fi

    # Step 5: Check syscall_in_userspace_test.c - stop if failed
    echo "[log]: Look for source file (syscall_in_userspace_test.c)"
    if ! check_file "userspace/syscall_in_userspace_test.c"; then
        SYSCALL_ERR="${SYSCALL_ERR}\n - (-50 points) Failed to find your userspace code"
        return 1
    fi

    # Step 6: Check directory - stop if failed
    echo "[log]: Look for screenshot directory"
    if ! check_dir "screenshot"; then
        SYSCALL_ERR="${SYSCALL_ERR}\n - (-50 points) Failed to find screenshot directory"
        return 1
    fi

    # Step 7: Check syscall_output.png - stop if failed
    echo "[log]: Look for syscall_output screenshot"
    if ! check_file "screenshot/syscall_output.*"; then
        SYSCALL_ERR="${SYSCALL_ERR}\n - (-50 points) Failed to find your syscall_output screenshot"
        return 1
    else
        echo "[log]: - Screenshot found"
    fi

    let SYSCALL_PTS=SYSCALL_PTS+50
    return 0
}
