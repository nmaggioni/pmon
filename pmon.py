#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
A simple performance monitor for Unix processes that outputs scaled graphs.
"""

import argparse
import datetime
import time

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Missing 'matplotlib' package. Please refer to: http://matplotlib.org/users/installing.html")
    plt = None
    exit(1)
try:
    import psutil
except ImportError:
    print("Missing 'psutil' package. Please refer to: https://pypi.python.org/pypi/psutil")
    psutil = None
    exit(1)

__author__ = "Niccolò Maggioni"
__license__ = "MIT"

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true")
parser.add_argument("-t", "--timeout", help="The duration of the monitoring in seconds.", type=int, default=0)
parser.add_argument("PID", help="The PID to monitor.", type=int)
args = parser.parse_args()

p = None
try:
    p = psutil.Process(args.PID)
except psutil.NoSuchProcess:
    print("No process found with that PID.")
    exit(1)


def min_or_zero(values):
    min(values) - 1 if min(values) - 1 >= 0 else 0


def b_to_mb(b):
    return round(b / (1024 * 1024))


cpu, threads, mem_pct, mem_vms, mem_rss = [], [], [], [], []
cmdline = " ".join(p.cmdline())
ppid = p.ppid()
cores = p.cpu_affinity()
create_time = datetime.datetime.fromtimestamp(p.create_time()).strftime("%d-%m-%Y %H:%M:%S")
niceness = p.nice()

for i in range(3):
    p.cpu_percent()  # First values should be discarded
    time.sleep(0.1)

elapsed = 0
print("Press CTRL+C to stop monitoring.")
while True:
    try:
        if args.timeout:
            if elapsed == args.timeout:
                break
            print("Time left: " + str(args.timeout - elapsed) + "s          ", end="\r")

        if p.is_running():
            cpu.append(round(p.cpu_percent(), -1))
            mem_vms.append(b_to_mb(p.memory_info().vms))
            mem_rss.append(b_to_mb(p.memory_info().rss))
            mem_pct.append(round(p.memory_percent(), -1))
            threads.append(p.num_threads())

            elapsed += 1
            time.sleep(1)
        else:
            print("Process is not running anymore.")
            break
    except KeyboardInterrupt:
        break

# Graphspace configuration
rows = 3
cols = 2
fig = plt.figure(1)

# CPU Percentage plot
plt.subplot(rows, cols, 1)
plt.ticklabel_format(useOffset=False)
plt.title("CPU")
plt.plot(cpu)
plt.ylabel("CPU (%)")
plt.xlabel("Time (s)")
plt.xlim(0, elapsed - 1)
plt.ylim(min_or_zero(cpu), max(cpu) + 1)
plt.grid(True)

# Threads Number plot
plt.subplot(rows, cols, 3)
plt.ticklabel_format(useOffset=False)
plt.title("Threads")
plt.plot(threads, '--')
plt.ylabel("Threads")
plt.xlabel("Time (s)")
plt.xlim(0, elapsed - 1)
plt.ylim(min(threads) - 1, max(threads) + 1)
plt.grid(True)

# Memory Percentage plot
plt.subplot(rows, cols, 2)
plt.ticklabel_format(useOffset=False)
plt.title("Memory (%)")
plt.plot(mem_pct)
plt.ylabel("Memory (%)")
plt.xlabel("Time (s)")
plt.xlim(0, elapsed - 1)
plt.ylim(min_or_zero(mem_pct), max(mem_pct) + 1)
plt.grid(True)

# Virtual Memory plot
plt.subplot(rows, cols, 4)
plt.ticklabel_format(useOffset=False)
plt.title("Memory (VMS)")
plt.plot(mem_vms, 'g-')
plt.ylabel("Memory (MB)")
plt.xlabel("Time (s)")
plt.xlim(0, elapsed - 1)
plt.ylim(min(mem_vms) - 1, max(mem_vms) + 1)
plt.grid(True)

# Resident Memory plot
plt.subplot(rows, cols, 6)
plt.ticklabel_format(useOffset=False)
plt.title("Memory (RSS)")
plt.plot(mem_rss, 'r-')
plt.ylabel("Memory (MB)")
plt.xlabel("Time (s)")
plt.xlim(0, elapsed - 1)
plt.ylim(min(mem_rss) - 1, max(mem_rss) + 1)
plt.grid(True)

# Graphspace cleanup
fig.tight_layout()
plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.2)

# Additional text
fig.text(0.005, 0.09, "Command: \"" + cmdline + "\"")
fig.text(0.005, 0.05, "Cores: " + str(cores) + " - Niceness: " + str(niceness) + " - Parent PID: " + str(ppid))
fig.text(0.005, 0.01, "Started at: " + create_time + " - Monitored for: " + str(elapsed) + "s")

plt.show()
