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

#File Size
#Under Construction
#File Size

#Compress File
gs -q -dNOPAUSE -dBATCH -dSAFER -dPDFA=2 -dPDFACompatibilityPolicy=1 \
-dSimulateOverprint=true -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 \
-dPDFSETTINGS=/prepress -dEmbedAllFonts=true -dSubsetFonts=true \
-dAutoRotatePages=/None -dColorImageDownsampleType=/Bicubic \
-dColorImageResolution=150 -dGrayImageDownsampleType=/Bicubic \
-dGrayImageResolution=150 -dMonoImageDownsampleType=/Bicubic \
-dMonoImageResolution=150 -dColorConversionStrategy=/Gray \
-dProcessColorModel=/DeviceGray \
-sOutputFile="${output_file}" "${file}"
#-sOutputFile="${dir}"/output-compressed.pdf "${file}"

#Success Message
if [ $?==0 ]
then
  python3 success.py
fi

#Remove Temp
rm input.txt
