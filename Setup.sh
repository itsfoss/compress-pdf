#!/bin/bash

#PDF-Compressor Setup


#Setup Colors
R='\e[38;5;9m'  #Red
G='\e[38;5;10m' #Green
B='\e[38;5;4m'  #Blue
Y='\e[38;5;11m' #Yellow
W='\e[38;5;7m'  #White
#Setup  Colors

echo
echo

#Banner
echo -e "........................................"
echo -e "..####...######..######..##..##..#####.."
echo -e ".##......##........##....##..##..##..##."
echo -e "..####...####......##....##..##..#####.."
echo -e ".....##..##........##....##..##..##....."
echo -e "..####...######....##.....####...##....."
echo -e "........................................"
#Banner

echo
echo

#Python3 Version
python3 -V > .python3_v.txt
v="$(awk '{print $2}' .python3_v.txt)"
echo $v | tr -d '.' |  sed 's/./& /g' > .python3_v2.txt
version="$(awk '{print $1}' .python3_v2.txt)"
#Python3 Version

#Ghostscript Version

#Ghostscript Version


#PDF-Compressor Install
if(( $version -eq $3))
then
  echo -e "  Requirements"
  echo -e " -------------------"
  echo
  echo -e " Python3: ${G} [ok] \e[0m"
  echo
  echo
  echo
  echo
  read -p " * Proceed to Install? [y/n] $> " yn
  case $yn in
    [Yy]* )
    echo
    echo
    echo
    echo
    echo -e "${W}-------------------------------------------"
    echo -e "${R} PDF-Compressor is ready to be installed.. "
    echo -e "${W}-------------------------------------------"
    #Code
    echo
    ;;
    [Nn]* )
    echo
    echo
    echo
    echo
    echo -e " ${Y} Byee..See you again :) \e[0m"
    echo
    exit
    ;;
esac
fi
#PDF-Compressor Install

#Unnecessary File Removal
rm .python3_v.txt
rm .python3_v2.txt
#Unnecessary File Removal


#PDF-Compressor Setup

#It's FOSS team
