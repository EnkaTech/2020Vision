#!/bin/bash
# This script copies the files in order to run
# automatically at startup

# root always has the ID 0
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit 1
fi

TARGET="/opt/2020vision/"
SYSD_DIR="/lib/systemd/system/"

if [[ -d $TARGET ]]; then
    echo "$TARGET already exists as a directory. Replace it?(y/n): "
    read -n 1 ans
    
    if [[ $ans == "y" ]] || [[ $ans == "Y" ]]; then
	rm -r $TARGET
    else exit
    fi
fi


mkdir $TARGET
echo "Copying python scripts to $TARGET"
for file in *.py; do

    cp $file "${TARGET}${file}"
done

echo "Copying the service file to $TARGET"
cp 2020vision.service "${SYSD_DIR}2020vision.service"

echo "Done!"
echo "Read the instructions on README for enabling the service"
exit 0
