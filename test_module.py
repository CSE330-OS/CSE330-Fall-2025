#!/usr/bin/env python3

"""

There are various `print()` statements already in the code for you
to uncomment, if you wish to have them to debug.

"""

from time import sleep
from sys import argv
import subprocess
import random
import os
import re

num_swapped_correct = 0
num_present_correct = 0
num_invalid_correct = 0
err_log = ""

# If this happens at any point, we simply stop testing and you
# will be left with what ever points you have
module_cant_unload = False
module_cant_load = False

"""

Process management

"""


def set_swap(enable: bool):
    cmd = 'swapon' if enable else 'swapoff'
    proc = subprocess.Popen([cmd, '-a'])
    proc.communicate()


def start_testp5_proc(arg: int):
    if not os.path.exists('./testp5'):
        print('Cannot find testp5 binary. Run the script in the same'
              'directory as testp5, and make sure you have compiled it.')
        exit(1)
    return subprocess.Popen(['./testp5', f'{arg}'])


def stop_testp5_proc(proc):
    proc.terminate()
    proc.wait()


"""

Procfs management

"""


def __get_address_ranges(pid: int):
    maps_path, ranges = f'/proc/{pid}/maps', list()
    with open(maps_path, 'r') as file:
        for line in file.readlines():
            line = re.split(r"[ \t\n\r-]+", line)
            ranges.append((int(line[0], 16), int(line[1], 16)))
    return ranges


# We make large heap allocations, hence we want to find the largest
# virtual address space amongst all virtual address spaces. It is
# not as simple as just looking for the one that is named "heap",
# if allocations are large enough they are placed elsewhere
def __get_largest_address_range(addr_ranges: list):
    return max(addr_ranges, key=lambda x: x[1] - x[0])


def __get_pagemap_info(addr_range: (int, int), pid: int):
    pagemap_path, page_size = f'/proc/{pid}/pagemap', 0x1000
    start_addr, end_addr = addr_range[0], addr_range[1]
    swapped, present = list(), list()

    for i in range(start_addr, end_addr, page_size):
        index = int((i / page_size) * 8)
        with open(pagemap_path, 'rb') as file:
            file.seek(index)
            data = int.from_bytes(file.read(8), 'little')

            is_swapped = ((data >> 62) & 1) != 0
            is_present = ((data >> 63) & 1) != 0
            pfn = data & 0x7fffffffffffff

            if is_swapped:
                swapped.append((i, pfn))

            elif is_present:
                present.append((i, pfn))

    # Order matters here, be careful
    return swapped, present


def get_pages_info(pid: int):
    swap_pages, present_pages = list(), list()
    addr_ranges = __get_address_ranges(pid)
    largest_range = __get_largest_address_range(addr_ranges)
    s, p = __get_pagemap_info(largest_range, pid)
    present_pages.extend(p)
    swap_pages.extend(s)
    return swap_pages, present_pages


def gen_invalid_addrs(swap_pages: list, present_pages: list, count: int):
    existing_addr, unique_addr = set(swap_pages + present_pages), set()
    while len(unique_addr) < count:
        address = random.getrandbits(64)
        if address not in existing_addr:
            unique_addr.add(address)
    return list(unique_addr)


"""

Error Logging and Scoring

"""


def cal_score(num_present: int, num_swapped: int, num_invalid: int):
    global num_swapped_correct, num_present_correct, num_invalid_correct
    total_count = num_present + num_swapped + num_invalid

    present_score = num_present_correct / num_present if num_present > 0 else 0
    swapped_score = num_swapped_correct / num_swapped if num_swapped > 0 else 0
    invalid_score = num_invalid_correct / num_invalid if num_invalid > 0 else 0

    score = (present_score * (num_present / total_count)) + \
            (swapped_score * (num_swapped / total_count)) + \
            (invalid_score * (num_invalid / total_count))
    return score


def calc_deduct(num_correct: int, total: int):
    return ((total - num_correct) / total) * (1 / 3)


def log_mistake(line: str):
    global err_log
    err_log += f' - {line}\n'


"""

Test Case Helpers

"""


def __load_module(module_path: str, pid: int, addr: int):
    module_path_full = os.path.abspath(module_path)
    global module_cant_load

    # Check to make sure kernel object exists
    if not os.path.exists(module_path):
        err_str = 'kernel object does not exist, please compile before ' \
                    'running the script as root'
        module_cant_load = True
        log_mistake(err_str)
        raise Exception(err_str)

    # Check if already loaded
    with open("/proc/modules", "r") as file:
        modules = [line.split()[0] for line in file.readlines()]
        if "memory_manager" in modules:
            err_str = 'memory_manager kernel module is already loaded'
            module_cant_load = True
            log_mistake(err_str)
            raise Exception(err_str)

    # Run the insmod command
    cmd = ["insmod", module_path_full, f"pid={pid}", f"addr={addr}"]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    # Check for valid insertion
    if proc.returncode != 0:
        err_str = 'memory_manager.ko kernel module failed to load ' \
                        '(insmod returned a non-zero exit code)'
        module_cant_load = True
        log_mistake(err_str)
        raise Exception(err_str)


def __read_kern_log():
    prefix = "[CSE330-Memory-Manager]"
    with open("/var/log/kern.log", "r") as file:
        for line in reversed(file.readlines()):
            if prefix in line:
                return line.strip()
    err_str = 'Could not parse kernel log, please double check ' \
            'your output format to make sure it matches the doc'
    raise Exception(err_str)


def __parse_phys_addr(line: str):
    search = re.search(r'physical address \[(\w+)\]', line)
    if search:
        return search.group(1)
    err_str = 'Could not parse phys-address, please double check ' \
            'your output format to make sure it matches the doc'
    raise Exception(err_str)


def __parse_swap_addr(line: str):
    search = re.search(r'swap identifier \[(\w+)\]', line)
    if search:
        return search.group(1)
    err_str = 'Could not parse swapID, please double check ' \
            'your output format to make sure it matches the doc'
    raise Exception(err_str)


def __parse_invalid_addr(line: str):
    pattern = r'physical address \[NA\] swap identifier \[NA\]'
    search = re.search(pattern, line)
    if search:
        return search.group(0)
    err_str = 'Could not parse output, please double check ' \
            'your output format to make sure it matches the doc'
    raise Exception(err_str)


def is_hex(s):
    return bool(re.fullmatch(r"0[xX][0-9a-fA-F]+|[0-9a-fA-F]+", s))


def __is_page_present(line: str):
    try:
        addr = __parse_phys_addr(line)
        if not is_hex(addr):
            return False
        return True
    except:
        return False


def __is_page_swapped(line: str):
    try:
        addr = __parse_swap_addr(line)
        if not is_hex(addr):
            return False
        return True
    except:
        return False


def __is_page_invalid(line: str):
    try:
        _ = __parse_invalid_addr(line)
        return True
    except:
        return False


def __unload_module(module_path: str):
    global module_cant_unload
    cmd = ["rmmod", "memory_manager"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        err_str = 'memory_manager kernel module failed to unload ' \
                '(rmmod returned a non-zero exit code)'
        module_cant_unload = True
        raise Exception(err_str)


"""

Test Cases Themselves

"""


def __gen_page_offset():
    # I know the mask is redundant, can't hurt
    return random.getrandbits(12) & 0x0FFF


# Returns True if the test runs as expected:
#  - Note, this does not mean that the solution is correct, rather
#    this should return True if the page is not moved to swap while
#    we are checking
def test_physical_addr(module_path: str, pid: int, virt: int, phys: int):

    try:
        __load_module(module_path, pid, virt)
        __unload_module(module_path)
    except:
        return True
    kern_log_output = __read_kern_log()

    # Retry if the page moves while we are checking
    #if not __is_page_present(kern_log_output):
    #    print('retry')
    #    return False

    phys_test = int(__parse_phys_addr(kern_log_output), 16)
    page_offset = virt & 0x0FFF
    phys_correct = (phys * 0x1000) | page_offset

    # print(f'{hex(phys_test)} == {hex(phys_correct)}')

    global num_present_correct
    if phys_test == phys_correct:
        num_present_correct += 1
    else:
        log_mistake(f'Error for virtual address {hex(virt)}: '
                    f'expected physical address {hex(phys_correct)}, '
                    f'got physical address {hex(phys_test)}')
    return True


# Returns True if the test runs as expected:
#  - Note, this does not mean that the solution is correct, rather
#    this should return True if the page is not moved to swap while
#    we are checking
def test_swapped_addr(module_path: str, pid: int, virt: int, phys: int):

    try:
        __load_module(module_path, pid, virt)
        __unload_module(module_path)
    except:
        return True
    kern_log_output = __read_kern_log()

    # Retry if the page moves while we are checking
    if not __is_page_swapped(kern_log_output):
        # print('retry')
        return False

    swap_test = int(__parse_swap_addr(kern_log_output), 16)
    swap_correct = int(phys / 32)

    # print(f'{hex(swap_test)} == {hex(swap_correct)}')

    global num_swapped_correct
    if swap_test == swap_correct:
        num_swapped_correct += 1
    else:
        log_mistake(f'Error for virtual address {hex(virt)}: '
                    f'expected swapID {hex(swap_correct)}, '
                    f'got swapID {hex(swap_test)}')
    return True


def test_invalid_addr(module_path: str, pid: int, virt: int):

    try:
        __load_module(module_path, pid, virt)
        __unload_module(module_path)
    except:
        return True
    kern_log_output = __read_kern_log()

    if not __is_page_invalid(kern_log_output):
        # print('retry')
        return False

    global num_invalid_correct
    if __is_page_present(kern_log_output) or \
            __is_page_swapped(kern_log_output):
        log_mistake(f'Error for virtual address {hex(virt)}: '
                    f'should be invalid address')
    else:
        num_invalid_correct += 1
    return True


"""

Main

"""


def usage_and_die():
    print('Usage: sudo ./test_module.py /path/to/memory_manager.ko '
          '<scalar> <present> <swapped> <invalid>')
    print(' - scalar  : This should change based on RAM size and test case.\n'
          ' - present : The number of present addresses to test.\n'
          ' - swapped : The number of swapped addresses to test.\n'
          ' - invalid : The number of invalid addresses to test.')
    print('This script MUST be run as root and you MUST have compiled '
          'your kernel module before running.')
    exit(1)


if __name__ == "__main__":

    if os.geteuid() != 0:
        usage_and_die()

    if len(argv) != 6:
        usage_and_die()

    path = argv[1]  # Path to kernel object
    scalar = int(argv[2])
    num_present = int(argv[3])
    num_swapped = int(argv[4])
    num_invalid = int(argv[5])

    # We only enable swap if we wish to test swap, otherwise we leave it off
    # to avoid any non-determinism with present pages being moved to swap
    if num_swapped > 0:
        print('[log]: Enabling swap')
        set_swap(enable=True)
    else:
        print('[log]: Disable swap')
        set_swap(enable=False)

    # Start the testp5 process
    proc = start_testp5_proc(scalar)
    print('[log]: Waiting for 5 seconds to allow '
          'pages to be present and/or to be moved '
          'to swap')
    sleep(5)

    # These are each tuple lists of virtual/physical address pairs
    swap_pages, present_pages = get_pages_info(proc.pid)
    invalid_pages = gen_invalid_addrs(swap_pages, present_pages, num_invalid)
    test_passed = True

    """

    Check present pages

    """

    if num_present > 0:

        while len(present_pages) == 0:
            print('[log]: No present pages found, waiting for 5 '
                  'seconds and looking for more')
            sleep(5)
            swap_pages, present_pages = get_pages_info(proc.pid)

        print(f'[log]: Checking {num_present} random present pages')
        for i in range(num_present):

            if module_cant_unload or module_cant_load:
                break

            retry = False
            while not retry:
                page_offset = __gen_page_offset()
                virt, phys = random.choice(present_pages)
                virt = virt | page_offset
                # print(f'{hex(virt)} -> {hex(phys)}')
                retry = test_physical_addr(path, proc.pid, virt, phys)

        if num_present_correct == num_present:
            print(f'[log]: - {num_present_correct}/{num_present} correct')
        else:
            deduct = calc_deduct(num_present_correct, num_present) * 100
            test_passed = False
            print(f'[log]: - {num_present_correct}/{num_present} '
                  f'correct (-{deduct} points)')

    """

    Check swapped pages

    """

    if num_swapped > 0:

        while len(swap_pages) == 0:
            print('[log]: No swap pages found, waiting for 5 '
                  'seconds and looking for more')
            sleep(5)
            swap_pages, present_pages = get_pages_info(proc.pid)

        print(f'[log]: Checking {num_swapped} random swapped pages')
        for i in range(num_swapped):

            if module_cant_unload or module_cant_load:
                break

            retry = False
            while not retry:
                page_offset = __gen_page_offset()
                virt, phys = random.choice(swap_pages)
                virt = virt | page_offset
                # print(f'{hex(virt)} -> {hex(phys)}')
                retry = test_swapped_addr(path, proc.pid, virt, phys)

        if num_swapped_correct == num_swapped:
            print(f'[log]: - {num_swapped_correct}/{num_swapped} correct')
        else:
            deduct = calc_deduct(num_swapped_correct, num_swapped) * 100
            test_passed = False
            print(f'[log]: - {num_swapped_correct}/{num_swapped} '
                  f'correct (-{deduct} points)')

    """

    Check invalid pages

    """

    if num_invalid > 0:

        print(f'[log]: Checking {num_invalid} random invalid pages')
        for i in range(num_invalid):

            if module_cant_unload or module_cant_load:
                break

            virt = random.choice(invalid_pages)
            test_invalid_addr(path, proc.pid, virt)

        if num_invalid_correct == num_invalid:
            print(f'[log]: - {num_invalid_correct}/{num_invalid} correct')
        else:
            deduct = calc_deduct(num_invalid_correct, num_invalid) * 100
            test_passed = False
            print(f'[log]: - {num_invalid_correct}/{num_invalid} '
                  f'correct (-{deduct} points)')

    # Stop the testp5 process
    stop_testp5_proc(proc)

    # Re-enable swap if it was disabled
    if num_swapped == 0:
        print('[log]: Enabling swap')
        set_swap(enable=True)

    final_score = cal_score(num_present, num_swapped, num_invalid)
    final_score = final_score * 100

    if test_passed:
        print(f'[memory_manager]: Passed ({final_score}/100)')
    else:
        print(f'[memory_manager]: Failed - ({final_score}/100)')
        print(err_log, end='')
