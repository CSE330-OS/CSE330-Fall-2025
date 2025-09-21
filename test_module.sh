#!/bin/bash

# !!! DO NOT MOVE THIS FILE !!!
source utils.sh

check_kernel_module ()
{
    local STATUS=0
    local prod=$1
    local cons=$2
    local size=$3
    local regular=$4
    local zombies=$5
    local uid=$(id -u ${USERNAME})

    sudo dmesg -C

    # Step 1: Check Makefile - stop if failed
    echo "[log]: Look for Makefile"
    if ! check_file "Makefile"; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n ─ Failed to find your Makefile"
        return 1
    fi

    # Step 2: Check zombie_killer.c - stop if failed
    echo "[log]: Look for source file (${KERNEL_MODULE_NAME}.c)"
    if ! check_file "${KERNEL_MODULE_NAME}.c"; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n ─ Failed to find your producer_consumer.c source file"
        return 1
    fi

    # Step 3: Compile the kernel module - stop if failed
    echo "[log]: Compile the kernel module"
    if ! compile_module; then
        return 1
    fi

	# Step 4: Start processes
    #echo "[log]: Starting ${regular} normal processes and ${zombies} zombies"
    echo "[log]: Starting ${regular} normal processes"
    start_processes ${regular} 0 &

    sleep 15
    local base_regular=($(ps -u "$USERNAME" -f | grep -E "procgen regular" | awk '{ print $2 }' | sort | uniq))

	# Step 5: Insert the kernel module - stop if failed
    echo "[log]: Load the kernel module"
    if ! load_module_with_params ${prod} ${cons} ${size} ${uid}; then
        return 1
    else
        echo "[log]: ─ Loaded successfully"
    fi

	if [[ "$zombies" -ne 0 ]]; then
		#start zombie process in batches
		total_zombies=${zombies}
		batch_size=1
		zombie_count=0

		if (( total_zombies <= 10 )); then
			batch_size=10
		elif (( total_zombies > 10 && total_zombies <= 100 )); then
			batch_size=10
		else
			batch_size=100
		fi

		echo "[log]: Starting zombie processes ..."
		while [ $zombie_count -lt $total_zombies ]; do
			remaining=$(( total_zombies - zombie_count ))

			if (( remaining < batch_size )); then
				current_batch_size=$remaining
			else
				current_batch_size=$batch_size
			fi

			start_processes 0 $current_batch_size
			((zombie_count += current_batch_size))

			echo "[log]: ─ Total zombies spawned so far: $zombie_count/$total_zombies"
			sleep 20
		done
	fi

	#echo "[log]: ┬ We will wait 20 seconds"
	#sleep 20

    # Step 6: Check the thread count
    echo "[log]: Checking the counts of the running kernel threads"
    #if ! check_threads ${prod} ${cons} 2; then
    if ! check_threads ${prod} ${cons} 2; then
        let STATUS=1
    else
        let KERNEL_MODULE_PTS=KERNEL_MODULE_PTS+200
        echo "[log]: ─ Found all expected threads"
    fi

    # Give the kernel module time to clean everything up
    echo "[log]: We will now wait some time to give your kernel module time to cleanup"
    echo "[log]: └─ We will wait 10 seconds"
    sleep 10

    # Step 7: Analyze all remaining pids - points will be added in compare_pids
    echo "[log]: Checking the pids of all remaining processes against your output"

	# Here we obtain the list of regular process pids and the pids of the zombie parents
	if [[ "$zombies" -ne 0 ]]; then
		local zombies_pids=($(sudo grep -Eo '[0-9]+' /home/$USERNAME/zombies.txt | sort | uniq))
	fi

    #echo "       ├─ These are the pids of processes that need to be saved:  ${base_regular[*]}"
    #echo "       └─ These are the pids of processes (zombie): ${zombies_pids[*]}"

    if ! compare_pids ${prod} ${cons} ${regular} ${zombies}
    then
        let STATUS=1
    else
        #echo "[log]: ┬─ All zombies were consumed"
	if [[ ${prod} -eq 0 ]]; then
        	echo "[log]: ┬─ Zero zombies were produced"
		echo "[log]: └─ None of the regular processes were consumed"
	else
		echo "[log]: ┬─ All zombies were produced"
		echo "[log]: └─ None of the regular processes were consumed"
	fi
    fi

    # Here, we kill any remaining processes that werer running ourselves. At this point the
    # student will not be docked as we are already done checking.
    if pgrep procgen > /dev/null; then
        sudo killall procgen
    fi

    # Step 8: Unload module - stop if failed
    echo "[log]: Unload the kernel module"
    if ! unload_module; then
        return 1
    else
        echo "[log]: ─ Kernel module unloaded successfully"
    fi

    # Step 9: Check all threads - make sure they have stopped
    echo "[log]: Checking to make sure kthreads are terminated"
    if ! check_threads 0 0 3; then
        let STATUS=1
    else
        echo "[log]: ─ All threads have been stopped"
        #let KERNEL_MODULE_PTS=KERNEL_MODULE_PTS+300
    	KERNEL_MODULE_PTS=$(echo "$KERNEL_MODULE_PTS + 300" | bc)
    fi

    return $STATUS
}

run_test ()
{
    local prod=$2
    local cons=$3
    local size=$4
    local regular=$5
    local zombies=$6

    local project_path=$(realpath "$1")
    pushd ${project_path} 1>/dev/null

    if check_kernel_module $prod $cons $size $regular $zombies; then
        echo -e "[zombie_finder]: Passed"
    else
        #echo -e "[zombie_finder]: Failed ${KERNEL_MODULE_ERR}"
        echo -e "[zombie_finder]: Failed"
    fi

    local final_score=$(echo "scale=2; ${KERNEL_MODULE_PTS} / 100" | bc)
    local final_total=$((KERNEL_MODULE_TOTAL / 100))
    echo "[final score]: ${final_score}/${final_total}"
    popd 1>/dev/null
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

if [ "$#" -ne 6 ]; then
    echo "Usage: ./test_module.sh /path/to/your/submission/ <prod> <cons> <size> <regular> <zombies>"
    echo " <prod>    - the number of producer threads for the kernel module"
    echo " <cons>    - the number of consumer threads for the kernel module"
    echo " <size>    - the size of the buffer for the kernel module"
    echo " <regular> - the number of regular processes to spawn for the process generator"
    echo " <zombies> - the number of zombie processes to spawn for the process generator"
    exit 1
fi

# Compiling Process Generator
make 1>/dev/null 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Could not compile the process generator - Exiting"
    exit 1
fi
PROCGEN_PATH=$(realpath ./procgen)
sudo cp $PROCGEN_PATH /usr/bin

# Making the test user (if it doesn't already exist)
if ! id "$USERNAME" &>/dev/null; then
    echo "[log]: Creating user $USERNAME..."
    sudo useradd -m "$USERNAME"
fi

# Start the test
if [ -e "$1" ]; then
    run_test $1 $2 $3 $4 $5 $6
    echo "[log]: Deleting user $USERNAME..."
    sudo userdel -r $USERNAME 2>/dev/null
else
    echo "File $1 does not exist"
    exit 1
fi
