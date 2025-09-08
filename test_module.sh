#!/bin/bash

# !!! DO NOT MOVE THIS FILE !!!
source utils.sh

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

run_test ()
{
    local FINAL_TOTAL=0
    local FINAL_PTS=0

    local zip_file=$(realpath "$1")
    local unzip_dir="unzip_$(date +%s)"

    mkdir -p ${unzip_dir}
    pushd ${unzip_dir} 1>/dev/null
    unzip ${zip_file} 1>/dev/null
    echo "Unzipping to \"${unzip_dir}\""

    if check_kernel_module; then
        echo -e "[my_module]: Passed with ${KERNEL_MODULE_PTS} out of ${KERNEL_MODULE_TOTAL}"
    else
        echo -e "[my_module]: Failed with ${KERNEL_MODULE_PTS} out of ${KERNEL_MODULE_TOTAL} because:${KERNEL_MODULE_ERR}."
    fi

    let FINAL_TOTAL=KERNEL_MODULE_TOTAL
    let FINAL_PTS=KERNEL_MODULE_PTS
    echo "[Total Score]: ${FINAL_PTS} out of ${FINAL_TOTAL}"

    popd 1>/dev/null
    rm -r ${unzip_dir}
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

if [ "$#" -ne 1 ]; then
    echo "Zip using this command: zip -r Project-2-ASUID.zip module/ kernel_syscall/ userspace/ screenshot/"
    echo "Run the script using this command: ./test_module.sh /path/to/your/submission.zip"
    exit 1
fi

if [ -e "$1" ]; then
    run_test "$1"
else
    echo "File $1 does not exist"
    exit 1
fi
