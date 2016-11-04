# example of an automation script
# produces all regular tilings with p,q < 10 and places them in the folder regular/

import os

for p in range(3,10):
    for q in range(3,10):
        command = "python coxeter.py -p %d -q %d -s 400 -M 2 -o regular/%d_%d.png"%(p,q,p,q)
        print command
        os.system(command)
