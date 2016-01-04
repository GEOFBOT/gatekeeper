import sys
import os
import subprocess

MAX_TRIES = 50

host = sys.argv[1]
times = sys.argv[2]
filename = sys.argv[3]

for num in range(int(times)):
    print('Testing ' + str(num) + ' of ' + str(times) + ' for ' + str(host))
    z = 1
    tries = 0
    while z != 0:
        # keep trying if it fails
        z = subprocess.call(['C:\\Dev\\phantomjs-2.0.0-windows\\bin\\phantomjs.exe', 'pageload.js', host, str(num), filename])
        tries += 1
        # too many tries (give up)
        if tries > MAX_TRIES:
            print('We tried and failed fifty times. Moving on...')
            break
        
