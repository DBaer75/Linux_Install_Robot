#!/usr/bin/env python3

import os
import sys


buff = str(sys.argv[1]) + ' ' + str(sys.argv[2])
print(buff)
os.system(buff)
#os.system("$PATH")
#print('$PATH')
#resource = 'source ~/catkin_ws/devel/setup.sh'
#os.system(resource)
os.system("$PATH")
print('test')