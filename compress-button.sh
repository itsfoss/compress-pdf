#!/bin/bash

#Compress Button


#Output Backend
file=$(cat input.txt) #file path
echo ${file##*/} > .filename.txt #filename
filename=$(cat .filename.txt) #file
finalname=${filename%.pdf} #without
output=$(echo ${finalname##*/}) #extension

dir=$(dirname "${file}")
echo $dir
#Output Backend


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


#Remove Temp
rm .filename.txt
rm input.txt
#Remove Temp

#Compress Button
