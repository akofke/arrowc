#!/bin/bash
PATH_PREFIX=~/Downloads/examples_pr03/

for i in `seq 1 23`; do
	cat ~/Downloads/examples_pr03/$i-ex-input.txt | pr03 -A | \
	diff - ~/Downloads/examples_pr03/$i-ex-output.txt

	echo $?

done
