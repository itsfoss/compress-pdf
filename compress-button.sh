#!/bin/bash

#Compressing action

#Extract the file path
file=$2

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
if [ "$1" == "-l" ]
   then
       level=prepress
elif [ "$1" == "-m" ]
   then
       level=ebook
elif [ "$1" == "-x" ]
   then
       level=screen
fi

#Compress File

gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
-dPDFSETTINGS=/$level -dNOPAUSE -dQUIET -dBATCH \
-sOutputFile="${output_file}" "${file}"

#Success Message
if [ $?==0 ]
then
  python3 success.py
fi
