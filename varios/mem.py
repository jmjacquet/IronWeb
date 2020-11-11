#!/usr/local/bin/python2.5
 
"""
mem.py - A script which calculates, formats, and displays a customer's
memory usage
 
"""
 
import subprocess
import sys
 
CMD = "ps -o rss,command -u %s | grep -v peruser | awk '{sum += $1} END {print sum / 1024}'"
MEM = {}
 
def main():
    proc = subprocess.Popen('groups', shell=True, stdout=subprocess.PIPE)
    proc.wait()
    stdout = proc.stdout.read()
 
    for user in stdout.split():
        proc = subprocess.Popen(CMD % user, shell=True, stdout=subprocess.PIPE)
        proc.wait()
 
        MEM[user] = int(float(proc.stdout.read()))
 
    print
    print 'Total Memory Usage: %i MB' % sum(MEM.values())
    print
    for user in sorted(MEM.keys()):
        print user.ljust(15), str(MEM[user]).rjust(3), 'MB'
    print
    print 'Note: "Total Memory Usage" is only valid when you execute mem using your\
 account\'s primary SSH user.'
    print
 
if __name__ == '__main__':
    main()