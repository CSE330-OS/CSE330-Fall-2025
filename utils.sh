#!/bin/bash

# This is the username of the user we will create and use to test
USERNAME="TestP4"

# Kernel module correctness
KERNEL_MODULE_NAME="producer_consumer"
KERNEL_MODULE_ERR=""
KERNEL_MODULE_PTS=0
KERNEL_MODULE_TOTAL=2500

# Function to check if comm output is empty and print "None" if so
check_output() {
    output="$1"
    if [ -z "$output" ]; then
        echo "None"
    else
        echo "$output"
    fi
}

function arraydiff() {
   awk 'BEGIN{RS=ORS=" "}
        {NR==FNR?a[$0]++:a[$0]--}
        END{for(k in a)if(a[k])print k}' <(echo -n "${!1}") <(echo -n "${!2}")
}

check_file ()
{
    local file_name=$(realpath "$1" 2>/dev/null)

    if [ -e ${file_name} ]; then
        echo "[log]: ─ file ${file_name} found"
        return 0
    else
        return 1
    fi
}

check_dir ()
{
    local dir_name=$(realpath "$1" 2>/dev/null)

    if [ -d ${dir_name} ]; then
        echo "[log]: ─ directory ${dir_name} found"
        return 0
    else
        return 1
    fi
}

compile_module ()
{
    make_err=$(make 2>&1 1>/dev/null)

    if [ $? -ne 0 ] ; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Failed to compile your kernel module: ${make_err}"
        return 1
    fi

    echo "[log]: ─ Compiled successfully"
    return 0
}

load_module_with_params ()
{
    local prod=$1
    local cons=$2
    local size=$3
    local uid=$4

    # Check to make sure kernel object exists
    if [ ! -e "${KERNEL_MODULE_NAME}.ko" ]; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Failed to find your kernel object ${KERNEL_MODULE_NAME}.ko"
        popd 1>/dev/null
        return 1
    fi

    # Insert kernel module - check exit code
    sudo dmesg -C
    sudo insmod "${KERNEL_MODULE_NAME}.ko" prod=${prod} cons=${cons} size=${size} uid=${uid}
    if [ $? -ne 0 ]; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Insmod exitted with non-zero return code"
        popd 1>/dev/null
        return 1
    fi

    # Check lsmod to make sure module is loaded
    if ! lsmod | grep -q "^${KERNEL_MODULE_NAME}"; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Kernel module does not appear in lsmod"
        return 1
    fi

    return 0
}

check_threads ()
{
    local prod=$1
    local cons=$2
    local points=$3

    # Check for producers
    local count=$(sudo ps aux | grep "Producer-" | wc -l)
    let count=count-1

    if [ "${count}" -ne "${prod}" ]; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Found ${count} producer threads, expected ${prod} (-${points} points)"
        return 1
    fi

    # Check for consumers
    local count=$(sudo ps aux | grep "Consumer-" | wc -l)
    let count=count-1

    if [ "${count}" -ne "${cons}" ]; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Found ${count} consumer threads, expected ${cons} (-${points} points)"
        return 1
    fi

    # All is good
    return 0
}

start_processes ()
{
    local regular=$1
    local zombies=$2

    for ((i=0; i<regular; i++)); do
        sudo -u "$USERNAME" bash -c "procgen regular" 2>/dev/null &
    done

    for ((i=0; i<zombies; i++)); do
        #sudo -u "$USERNAME" bash -c "procgen zombie" 2>/dev/null &
	sudo -u "$USERNAME" bash -c "procgen zombie" 2>&1 | sudo tee -a /home/$USERNAME/zombies.txt > /dev/null &
    done
}

compare_pids () {
    local status=0
    local final=0

    local prod=$1
    local cons=$2
    local regular=$3
    local zombies=$4
    local max_score=20
    local score=$max_score

    if [ "${prod}" -eq 0 ]; then
	local producer_points=$(( max_score * 100 / 2 ))
	local per_prod_points=$(echo "scale=2; $producer_points / $zombies" | bc)
	local consumer_points=$(( max_score * 100 / 2 ))
	local per_cons_points=$(echo "scale=2; $consumer_points / $zombies" | bc)
    fi

    # Get current processes (for logging/debug)
    local zombie_pids_alive=($(ps -u "$USERNAME" -f | grep -E "procgen" | grep -E "defunct" | awk '{ print $2 }' | sort | uniq))

    # Extract dmesg logs
    local dmesg_log=$(sudo dmesg | grep -E "has (produced|consumed) a zombie process with pid [0-9]+ and parent pid [0-9]+")

    local produced_pids=()
    local consumed_pids=()

    while IFS= read -r line; do
        if [[ $line == *"produced a zombie process"* ]]; then
            pid=$(echo "$line" | grep -oP "with pid \K[0-9]+")
            produced_pids+=("$pid")
        elif [[ $line == *"consumed a zombie process"* ]]; then
            pid=$(echo "$line" | grep -oP "with pid \K[0-9]+")
            consumed_pids+=("$pid")
        fi
    done <<< "$dmesg_log"

    mapfile -t produced_pids < <(printf "%s\n" "${produced_pids[@]}" | sort -n | uniq)
    mapfile -t consumed_pids < <(printf "%s\n" "${consumed_pids[@]}" | sort -n | uniq)

    produced_pids=($(printf "%s\n" "${produced_pids[@]}" | grep -v '^$'))
    consumed_pids=($(printf "%s\n" "${consumed_pids[@]}" | grep -v '^$'))

    local produced_count=${#produced_pids[@]}
    local consumed_count=${#consumed_pids[@]}

    # Check 1: If there is no space to produce items,
    # there will never be any output.
    if [ "${size}" -eq 0 ]; then
        echo "[info]: The size is zero so we will check to make sure no items are produced or consumed"
        if [ "${produced_count}" -ne 0 ]; then
            KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-20 points) Size is zero, yet items have been produced"
	    status=1
	    return ${status}
        else
	    let final=final+2000
	    KERNEL_MODULE_PTS=$(echo "$KERNEL_MODULE_PTS + $final" | bc)
            return 0
        fi

        # Check for consumed items
        if [ "${consumed_count}" -ne 0 ]; then
            KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-20 points) Size is zero, yet items have been consumed"
	    status=1
	    return ${status}
        else
	    let final=final+2000
	    KERNEL_MODULE_PTS=$(echo "$KERNEL_MODULE_PTS + $final" | bc)
            return 0
        fi
    fi

    # Check 2: No producers means no output because no items will ever
    # be produced (or consumed, since there is nothing to consume)
    if [ "${prod}" -eq 0 ]; then
        echo "[info]: There are no producers, so we will make sure no items are produced or consumed"

        if [ "${produced_count}" -ne 0 ]; then
            KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-20 points) There are no producers, yet items have been produced"
	    status=1
	    return ${status}
        else
	    let final=final+2000
	    KERNEL_MODULE_PTS=$(echo "$KERNEL_MODULE_PTS + $final" | bc)
            return 0
        fi
    fi

    # Check 3: If there are producers, and no consumers, then the
    # total number of items produced is bound by the size
    if [ "${cons}" -eq 0 ]; then
        echo "[info]: There are no consumers, so we will make sure items are produced but not consumed"

        # Check for items produced - should equal the size
        if [ "${produced_count}" -ne 0 ]; then
            KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-20 points) There are no consumers, yet the producers have produced more than size"
	    echo $KERNEL_MODULE_ERR
	    status=1
	    return ${status}
        else
	    let final=final+2000
	    KERNEL_MODULE_PTS=$(echo "$KERNEL_MODULE_PTS + $final" | bc)
            return 0
        fi

        # Check for items consumed - should equal zero
        if [ "${consumed_count}" -ne 0 ]; then
            KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - (-20 points) There are no consumers, yet items have been consumed"
	    echo $KERNEL_MODULE_ERR
	    status=1
	    return ${status}
        else
	    let final=final+2000
	    KERNEL_MODULE_PTS=$(echo "$KERNEL_MODULE_PTS + $final" | bc)
            return 0
        fi
    fi


    # --- Validate Producer ---
    if [[ "$produced_count" -ne "$zombies" ]]; then
        echo "[log]: - Expected $zombies zombies, but only $produced_count were produced (via dmesg)"
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - Expected $zombies zombies, but found $produced_count produced."
        status=1
    else
        echo "[log]: - All $zombies zombie processes were correctly produced."
    fi

    # --- Validate Consumer ---
    if [[ "$consumed_count" -lt "$produced_count" ]]; then
        local missing=$((produced_count - consumed_count))
        echo "[log]: - Only $consumed_count out of $produced_count zombies were consumed."
        echo "[log]: └─ $missing zombies not consumed."
        status=1
    else
        echo "[log]: - All $consumed_count zombies were successfully consumed."
    fi

    # --- Validate correctness of produced PIDs ---
    local wrong_produced=0
    for pid in "${produced_pids[@]}"; do
        if ! printf "%s\n" "${zombie_pids_alive[@]}" | grep -q -w "$pid"; then
            ((wrong_produced++))
        fi
    done

    if [[ $wrong_produced -gt 0 ]]; then
	local deduction=$(echo "scale=2; $per_prod_points * $wrong_produced" | bc)
	score=$(echo "$producer_points - $deduction" | bc)
	score=$(echo "$score < 0" | bc -l | grep -q 1 && echo 0 || echo "$score")
	final=$(echo "$final + $score" | bc)
    	local deduct=$(echo "scale=2; ${deduction} / 100" | bc)
	echo "[log]: - $wrong_produced incorrectly produced PIDs"
	echo "[log]: └─ Deducting $deduct points from module score."
	KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - $wrong_produced invalid zombie PIDs produced (-${deduct} points)"
	status=1
    else
	final=$(echo "$final + 1000" | bc)
	echo "[log]: - All zombie PIDs were validly produced."
    fi

    # --- Validate correctness of consumed PIDs ---
    local wrong_consumed=0
    for pid in "${consumed_pids[@]}"; do
        if ! printf "%s\n" "${zombie_pids_alive[@]}" | grep -q -w "$pid"; then
            ((wrong_consumed++))
        fi
    done

    if [[ $wrong_consumed -gt 0 ]]; then
	local deduction=$(echo "scale=2; $per_cons_points * $wrong_consumed" | bc)
	score=$(echo "$consumer_points - $deduction" | bc)
	score=$(echo "$score < 0" | bc -l | grep -q 1 && echo 0 || echo "$score")
	final=$(echo "$final + $score" | bc)
    	local deduct=$(echo "scale=2; ${deduction} / 100" | bc)
	echo "[log]: - $wrong_consumed incorrectly consumed PID"s
	echo "[log]: └─ Deducting $deduct points from module score."
	KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n - $wrong_produced invalid zombie PIDs consumed (-${deduct} points)"
	status=1
    else
	final=$(echo "$final + 1000" | bc)
	echo "[log]: - All zombie PIDs were validly consumed."
    fi

    # --- Success case ---
    if [[ $wrong_produced -eq 0 && $wrong_consumed -eq 0 && $produced_count -eq $zombies && $consumed_count -eq $zombies ]]; then
        echo "[log]: - All zombie PIDs correctly produced and consumed."
    fi

    final=$(echo "$final < 0" | bc -l | grep -q 1 && echo 0 || echo "$final")
    KERNEL_MODULE_PTS=$(echo "$KERNEL_MODULE_PTS + $final" | bc)

    return ${status}
}


unload_module ()
{
    sudo dmesg -C && sudo rmmod "${KERNEL_MODULE_NAME}"

    # Checking for successful module removal
    if lsmod | grep -q "^${KERNEL_MODULE_NAME}"; then
        KERNEL_MODULE_ERR="${KERNEL_MODULE_ERR}\n ─ Failed to unload kernel module"
        echo "[log]: ─ Failed to unload kernel module"
        return 1
    fi

    return 0
}
