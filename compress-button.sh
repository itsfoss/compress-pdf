#!/bin/bash

#Compress Button


#Output Backend
file=$(cat input.txt) #file path
echo ${file##*/} > .filename.txt #filename
filename=$(cat .filename.txt) #file
finalname=${filename%.pdf} #without
output=$(echo ${finalname##*/}) #extension
dir=$(dirname "${file}")
#Output Backend

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
-sOutputFile=$dir/$output-compressed.pdf $file
#Compress File

#Success Message
if [ -e $dir/$output-compressed.pdf ]
then
  python3 success.py
fi
if [ -s $dir/$output-compressed.pdf ]
then
  python3 error.py
fi
#Success Message

#Remove Temp
rm .filename.txt
rm input.txt
#Remove Temp

#Compress Button
