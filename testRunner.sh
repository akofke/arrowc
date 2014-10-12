#!/bin/bash
PATH_PREFIX=~/Downloads/examples_pr03/

for i in `seq 0 10`; do
	echo -e "Testing ex $i\n"
	
	prOut=`cat ~/Downloads/examples_pr03/$i-ex-input.txt | pr03 -A`
	echo $prOut
	echo "-------------------------------------"
	exOut=`cat ~/Downloads/examples_pr03/$i-ex-output.txt`
	echo $exOut
	echo "+++++++++++++++++++++++++++++++++++++"
	echo "======================================="
	
done
