#!/usr/bin/env python3

from time import sleep
import subprocess
import shutil
import sys
import pdb
import re
import os

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

err_log = ""
final_score = 33.33


def log_mistake(line: str):
    global err_log
    err_log += f' - {line}\n'


def cal_src_read_points(old_src_reads: float, src_reads: float,
                        old_cache_reads: float, cache_reads: float,
                        expected_src: float, expected_cache: float, test_case: int):
    global final_score
    print('[log]: Checking data read from source device')
    size_read = (src_reads - old_src_reads + cache_reads - old_cache_reads) / 1024
    # print(f'The size of read is: {int(size_read)} or {size_read}')

    if (size_read - expected_cache) != expected_src:
        if test_case == 2:
            points = 5.0
        else: 
            points = 10.0

        final_score -= points
        print(f'[log]: └─ {size_read - expected_cache}MB read from source device expected '
              f'{expected_src}MB (-${points} points)')
    else:
        print(f'[log]: └─ {size_read - expected_cache}MB read from source device expected '
              f'{expected_src}MB')


def cal_cache_read_points(old_cache_reads: float, cache_reads: float,
                          old_src_reads: float, src_reads: float,
                          expected_cache: float, expected_src: float, test_case: int):
    global final_score
    print('[log]: Checking data read from cache device')
    size_read = (cache_reads - old_cache_reads + src_reads - old_src_reads) / 1024
    # print(f'The size of read is: {int(size_read)} or {size_read}')

    if (size_read - expected_src) != expected_cache:
        if test_case == 2:
            points = 5.0
        else: 
            points = 10.0

        final_score -= points
        print(f'[log]: └─ {size_read - expected_src}MB read from cache device expected '
              f'{expected_cache}MB (-${points} points)')
    else:
        print(f'[log]: └─ {size_read - expected_src}MB read from cache device expected '
              f'{expected_cache}MB')


def cal_hit_points(old_hits: float, hits: float, old_misses: float,
                   misses: float, expected_hits: float,
                   expected_misses: float, test_case: int):
    global final_score
    print('[log]: Checking number of cache hits')
    num_hits = 0

    if hits == 0 and old_hits == 0:
        num_hits = 0
    else:
        num_hits = hits - old_hits + misses - old_misses - expected_misses
    
    hit_diff = (expected_hits - num_hits)
    # print(f'The hit diff: {hit_diff}')
    

    if hit_diff != 0:
        if test_case  == 2:
            points = (11.66/expected_hits) * hit_diff
        else: 
            points = (23.33/expected_hits) * hit_diff

        final_score -= points
        print(f'[log]: └─ Found {num_hits} hits expected '
              f'{expected_hits} (-${points} points)')
    else:
        print(f'[log]: └─ Found {num_hits} hits expected '
              f'{expected_hits}')


def cal_miss_points(old_misses: float, misses: float, old_hits: float,
                    hits: float, expected_misses: float, expected_hits: float, test_case: int):
    global final_score
    print('[log]: Checking number of cache misses')
    num_misses = 0

    if misses == 0 and old_misses == 0:
        num_misses = 0
    else:
        num_misses = misses - old_misses + hits - old_hits - expected_hits
    
    miss_diff = (expected_misses - num_misses)
    # print(f'The miss diff: {miss_diff}')

    if miss_diff != 0:
        if test_case == 2:
            points = (11.66/expected_misses) * miss_diff
        else: 
            points = (23.33/expected_misses) * miss_diff
        final_score -= points
        print(f'[log]: └─ Found {num_misses} misses expected '
              f'{expected_misses} (-${points} points)')
    else:
        print(f'[log]: └─ Found {num_misses} misses expected '
              f'{expected_misses}')


def get_device_reads(dev: str):
    try:
        # Run iostat command to fetch device stats
        result = subprocess.run(["iostat", dev], text=True,
                                capture_output=True, check=True)
        iostat_output = result.stdout  # Extract the command output from stdout
        device_name = dev.split("/")[-1]

        kb_read = parse_kb_read(iostat_output, device_name)
        return kb_read

    # Parse iostat_output to extract the read statistics for `dev`
    # Example parsing (replace with your parsing logic):
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to run iostat command: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error fetching device reads: {e}")


def parse_kb_read(iostat_output: str, device: str) -> int:

    try:
        lines = iostat_output.splitlines()
        header_index = None

        # Find the header line and the device line
        for i, line in enumerate(lines):
            if line.strip().startswith("Device"):
                header_index = i
                break

        if header_index is None:
            raise ValueError("No 'Device' header found in iostat output.")

        # Extract column names to determine the `kB_read` position
        headers = lines[header_index].split()
        if "kB_read" not in headers:
            raise ValueError("'kB_read' column not found in iostat output.")

        kb_read_index = headers.index("kB_read")

        # Look for the device row
        for line in lines[header_index + 1:]:
            if line.strip().startswith(device):
                columns = line.split()
                return int(columns[kb_read_index])

        raise ValueError(f"Device '{device}' not found in iostat output.")

    except Exception as e:
        raise RuntimeError(f"Error parsing kB_read value: {e}")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


# Check if fio is installed on the system
def has_fio():
    return shutil.which('fio') is not None


# Start a fio workload provided the device file and size. We will always do
# read workloads, so there is no reason to be able to configure this.
def start_fio_workload(dev: str, sizemb: int):
    cmd = ['fio', f'--filename={dev}', '--name=test', '--rw=read',
           '--direct=1', f'--size={sizemb}MB', '--numjobs=1']

    if sizemb == 0:
        return
    try:
        _ = subprocess.run(cmd, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, text=True, check=True)
    except subprocess.CalledProcessError as e:
        err_str = f"[test_module]: Could not start fio workload - {e.stderr}"
        log_mistake(err_str)
        raise Exception(err_str)

    print(f'[log]: Issue a {sizemb}MB read workload')
    print(f'[log]: └─ sudo fio --filename={dev} --name=test --rw=read '
          f'--direct=1 --size={sizemb}MB --numjobs=1')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


def make_cache(name: str, cache_dev: str, src_dev: str):

    print('[log]: Creating cache')
    echo_cmd = ['echo', '0', '4194304', 'cache', src_dev,
                cache_dev, '8', '262144']
    dmsetup_cmd = ['dmsetup', 'create', name]
    print(f'[log]: └─ echo 0 4194304 cache {src_dev} {cache_dev} 8 262144 | '
          f'sudo dmsetup create {name}')
    echo_proc = subprocess.Popen(echo_cmd, stdout=subprocess.PIPE)
    dmsetup_proc = subprocess.Popen(dmsetup_cmd, stdin=echo_proc.stdout,
                                    stdout=subprocess.PIPE)
    echo_proc.stdout.close()
    dmsetup_proc.communicate()

    if dmsetup_proc.returncode != 0:
        err_str = "[test_module]: Failed to create cache instance"
        log_mistake(err_str)
        raise Exception(err_str)


def destroy_cache(name: str):

    dmsetup_cmd = ['dmsetup', 'remove', name]
    proc = subprocess.run(dmsetup_cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        err_str = "[test_module]: Failed to teardown cache"
        log_mistake(err_str)
        raise Exception(err_str)

    print('[log]: Removing cache')
    print(f'[log]: └─ sudo dmsetup remove {name}')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


def __get_cache_stat(lines: list, stat: str):
    prefix, pattern = 'device-mapper: cache:', rf"{stat}:(\d+)"
    for line in lines:

        if prefix not in line:
            continue

        match = re.search(pattern, line)
        if not match:
            continue

        val = int(match.group(1))
        return val

    err_str = f"Could not read cache stat ({stat})"
    log_mistake(err_str)
    raise Exception(err_str)


# Read /var/log/kern.log for dmcache stats
def __read_cache_status():
    with open('/var/log/kern.log', 'r') as kernlog:
        lines = list(reversed(kernlog.readlines()))
        reads = __get_cache_stat(lines, 'Reads')
        hits = __get_cache_stat(lines, 'Cache Hits')
        misses = __get_cache_stat(lines, 'Cache Miss')
    return reads, hits, misses


# Returns relevant cache stats after running dmsetup status
def cache_status(name: str):

    dmsetup_cmd = ['dmsetup', 'status', name]
    proc = subprocess.run(dmsetup_cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        err_str = "[test_module]: Failed to get cache status"
        log_mistake(err_str)
        raise Exception(err_str)

    print('[log]: Checking cache status')
    print(f'[log]: └─ sudo dmsetup status {name}')
    sleep(5)  # We use this to give the kernel time to flush the kernel log
    return __read_cache_status()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


def load_module(module_path: str):
    module_path_full = os.path.abspath(module_path)

    # Check to make sure kernel object exists
    if not os.path.exists(module_path):
        err_str = 'kernel object does not exist, please compile before ' \
                    'running the script as root'
        log_mistake(err_str)
        raise Exception(err_str)

    # Check if already loaded
    with open("/proc/modules", "r") as file:
        modules = [line.split()[0] for line in file.readlines()]
        if "dmcache" in modules:
            err_str = 'dmcache kernel module is already loaded'
            log_mistake(err_str)
            raise Exception(err_str)

    # Run the insmod command
    cmd = ["insmod", module_path_full]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    # Check for valid insertion
    if proc.returncode != 0:
        err_str = 'dmcache.ko kernel module failed to load ' \
                        '(insmod returned a non-zero exit code)'
        log_mistake(err_str)
        raise Exception(err_str)

    print('[log]: Module loaded successfully')


def unload_module():
    cmd = ["rmmod", "dmcache"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        err_str = 'dmcache kernel module failed to unload ' \
                '(rmmod returned a non-zero exit code)'
        log_mistake(err_str)

        raise Exception(err_str)
    print('[log]: Module unloaded successfully')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


def get_dev_storage(dev_path: str):

    try:
        dev_name = os.path.basename(dev_path)
        size_path = f'/sys/block/{dev_name}/size'

        with open(size_path, 'r') as file:
            sectors = int(file.read().strip())
        size_bytes = sectors * 512
        size_gb = size_bytes / (1024 ** 3)
        return size_gb

    except FileNotFoundError:
        err_str = f'Device {dev_path} not found or supported.'
        log_mistake(err_str)
        raise FileNotFoundError(err_str)

    except ValueError:
        err_str = f'Invalid device size for device {dev_path}.'
        log_mistake(err_str)
        raise ValueError(err_str)

    except Exception as e:
        err_str = f'Error calculating device size for {dev_path} - {e}'
        log_mistake(err_str)
        raise Exception(err_str)


# Run fio once to fill the cache, run fio again to achieve the
# targeted hit rate.
def do_cache_test(devname: str, target_hr: float, fill_sizemb: int,
                  src_dev: str, cache_dev: str):
    start_fio_workload(devname, round(fill_sizemb * target_hr))
    old_src_reads = get_device_reads(src_dev)
    old_cache_reads = get_device_reads(cache_dev)
    # print(f'src: {old_src_reads} cache: {old_cache_reads}')
    old_reads, old_hits, old_misses = cache_status('cache')

    start_fio_workload(devname, fill_sizemb)
    src_reads = get_device_reads(src_dev)
    cache_reads = get_device_reads(cache_dev)
    # print(f'src: {src_reads} cache: {cache_reads}')
    reads, hits, misses = cache_status('cache')

    if target_hr == 0.0:
        expected_src = 1024
        expected_cache = 0
        expected_misses = 262144
        expected_hits = 0

        cal_src_read_points(old_src_reads, src_reads, old_cache_reads,
                            cache_reads, expected_src, expected_cache, 1)
        cal_miss_points(old_misses, misses, old_hits, hits,
                        expected_misses, expected_hits, 1)
    elif target_hr == 0.5:
        expected_src = 512
        expected_cache = 512

        expected_misses = 131072
        expected_hits = 131072

        cal_src_read_points(old_src_reads, src_reads, old_cache_reads,
                            cache_reads, expected_src, expected_cache, 2)
        cal_cache_read_points(old_cache_reads, cache_reads, old_src_reads,
                              src_reads, expected_cache, expected_src, 2)

        cal_miss_points(old_misses, misses, old_hits, hits,
                        expected_misses, expected_hits, 2)
        cal_hit_points(old_hits, hits, old_misses, misses,
                       expected_hits, expected_misses, 2)
    elif target_hr == 1.0:
        expected_src = 0
        expected_cache = 1024
        expected_hits = 262144
        expected_misses = 0

        cal_cache_read_points(old_cache_reads, cache_reads, old_src_reads,
                              src_reads, expected_cache, expected_src, 3)
        cal_hit_points(old_hits, hits, old_misses, misses,
                       expected_hits, expected_misses, 3)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


def usage_and_die():
    print('Usage: sudo ./test_module.py /path/to/dmcache.ko /path/to/src_dev '
          '/path/to/cache_dev target_hit_rate')
    exit(1)


if __name__ == "__main__":

    nrargs = 5
    if os.geteuid() != 0 or len(sys.argv) != nrargs:
        usage_and_die()

    cache_dev, src_dev = sys.argv[3], sys.argv[2]
    cache_dev_min_size_gb, src_dev_min_size_gb = 1, 2
    target_hr = float(sys.argv[4])

    # Here, we check if the user has fio (flexible io tester) installed on
    # their system - https://github.com/axboe/fio
    if not has_fio():
        print("[test_module]: Please install fio onto your VM and "
              "run the script again.")
        exit(1)

    # Here, we make sure the devices match the sizes we specify in the doc
    if get_dev_storage(cache_dev) < cache_dev_min_size_gb:
        print("[test_module]: Your cache device is too small.")
        exit(1)
    if get_dev_storage(src_dev) < src_dev_min_size_gb:
        print("[test_module]: Your source device is too small.")
        exit(1)

    # Here, we load the module and make a cache instance
    load_module(sys.argv[1])
    make_cache('cache', cache_dev, src_dev)

    # Here, we initiate the workload based on the target hit rate
    do_cache_test('/dev/mapper/cache', target_hr, 1024, src_dev, cache_dev)

    # Here, we destroy the cache instance and unload the module
    destroy_cache('cache')
    unload_module()

    #pdb.set_trace()
    print(f"Final score: {final_score}")

    if final_score != 33.33:
        if final_score < 0:
            final_score = 0
        print(f'[dmcache]: Failed ({final_score}/33.33)')
        print(err_log, end='')
    else:
        print(f'[dmcache]: Passed ({final_score}/33.33)')
