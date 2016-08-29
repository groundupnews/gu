#!/bin/bash

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

daysback=-$1

for file in $(find . -mtime $daysback -iname "*.jpg" -o -iname "*.png"); do
	photographer=$(identify -verbose $file | grep -i exif:Artist | awk '{print $2, $3}')
	echo $file,$photographer,
	identify -verbose $file | grep -i keyword | awk -v PHOTOGRAPHER"=$photographer" -v FILE="$file" '{print FILE "," PHOTOGRAPHER "," $2}'
done

#IFS=$SAVEIFS
