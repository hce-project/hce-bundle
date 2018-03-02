#!/bin/bash

#CPU LA
echo "---CPU LA---"
cat /proc/loadavg

# CPU Cores
echo "---cpu cores---"
grep processor /proc/cpuinfo | wc -l

# vmstat
echo "---vmstat---"
vmstat 1 2

# processes
echo "---processes---"
ps xau | wc -l

# threads max
echo "---threads max---"
cat /proc/sys/kernel/threads-max

# threads
echo "---threads actual---"
grep -s '^Threads' /proc/[0-9]*/status | awk '{ sum += $2; } END { print sum; }'

# RAM
echo "---RAM---"
free

# Disk
echo "---Disk---"
df -P

#uptime
echo "---uptime---"
uptime

echo "---END---"
