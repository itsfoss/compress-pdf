#!/bin/bash

sleep 2
file=$0
if [ -f  $file ]
then
	echo 1
else
	echo 0
fi
