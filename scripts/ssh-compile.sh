#!/bin/bash

ssh 'adk62@eecslinab4.case.edu' 'cat <&0 > ssh_compile_temp.s && gcc -m32 -o ssh_compile_out ssh_compile_temp.s';
scp 'adk62@eecslinab4.case.edu:ssh_compile_out' '~/eecs337/projects/arrowc/scripts/'