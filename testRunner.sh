#!/bin/bash
PATH_PREFIX=~/Downloads/examples_pr03/

for i in `seq 0 23`; do
	echo -e "Testing ex $i\n"

	cat ~/Downloads/examples_pr03/$i-ex-input.txt | pr03 -A > \
	~/testResults/$i-proj.txt

	cat ~/Downloads/examples_pr03/$i-ex-output.txt > ~/testResults/$i-ex.txt
	
	cat ~/Downloads/examples_pr03/$i-ex-input.txt | pr03 -A | \
	diff - ~/Downloads/examples_pr03/$i-ex-output.txt >/dev/null
	echo $?

	echo "======================================="
	
done
