#!/bin/bash

ssh "adk62@eecslinab4.case.edu" "pr05/arrowc ${1} -o out <(cat <&0); cat out" 