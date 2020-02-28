#!/bin/bash

#Compressing action

#Extract the file path
file=$(cat input.txt)

#Remove path and extension for outut file name
filename=$(basename "${file}")

#Prepare the output file name
output_file="$(dirname "${file}")/${filename%.pdf}_compressed.pdf"

#Keep backslashes as ghost script doesn't handle it properly
file=${file//\\}
output_file=${output_file//\\}

#Default compression is high resolution
level=prepress

#script arguments
for arg in "$@"
do
    if [ "$arg" == "-l" ]
    then
        level=prepress
    fi
    if [ "$arg" == "-m" ]
    then
        level=ebook
    fi
    if [ "$arg" == "-x" ]
    then
        level=screen
    fi
done
#script arguments

#Compress File

gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
-dPDFSETTINGS=/$level -dNOPAUSE -dQUIET -dBATCH \
-sOutputFile="${output_file}" "${file}"

#Success Message
if [ $?==0 ]
then
  python3 success.py
fi

#Remove Temp
rm input.txt
