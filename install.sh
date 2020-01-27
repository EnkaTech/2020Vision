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

if [[ -e "${SYSD_DIR}2020vision.service" ]]; then
    echo "Stopping the service..."
    systemctl stop 2020vision.service
fi

if [[ -d $TARGET ]]; then
    echo -n "$TARGET already exists as a directory. Replace it? [y/n]: "
    read -n 1 ans
    echo
    
    if [[ $ans == "y" ]] || [[ $ans == "Y" ]]; then
	rm -r $TARGET
    else exit
    fi
fi


mkdir $TARGET

echo -n "Deploy client mode? [y/N]: "
read -n 1 ans
echo
if [[ $ans == "y" ]] || [[ $ans == "Y" ]]; then
    ln -s main_client.py main.py
else ln -s main_server.py main.py
fi


echo "Copying python scripts to $TARGET"
for file in *.py; do
    cp $file "${TARGET}${file}"
done

echo "Removing temprorary files"
rm main.py

echo "Copying the service file to $SYSD_DIR"
cp 2020vision.service "${SYSD_DIR}2020vision.service"

echo "Changing permissions on the service file"
sudo chmod 644 "${SYSD_DIR}2020vision.service"

echo "Done!"
echo "Read the instructions on README for enabling the service"

echo -n "Enable the service now? [y/n]: "
read -n 1 ans
echo

if [[ $ans == "y" ]] || [[ $ans == "Y" ]]; then
    echo "Refreshing systemd:"
    systemctl daemon-reload
    echo "Enabling the service"
    systemctl enable 2020vision.service
    echo "Done"
fi

exit 0
