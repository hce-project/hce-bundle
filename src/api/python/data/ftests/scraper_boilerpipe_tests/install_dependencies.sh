#!/bin/bash

# That script must run with the priveleged user

# Make sure you have installed git command.
# If you haven't one please, install it by:
# apt-get install git


# jpype
git clone https://github.com/originell/jpype.git
echo $?
if [ $? -ne 0 ]; then
    echo failure
    rm -rf jpype
    exit 1
else
    cd jpype
    /usr/bin/python setup.py install
    cd ../
fi
rm -rf jpype

#sharade
pip install charade

# boilerpipe
git clone https://github.com/misja/python-boilerpipe.git
if [ $? -ne 0 ]; then
    echo failure
    rm -rf python-boilerpipe
    exit 1
else
    cd python-boilerpipe
    /usr/bin/python setup.py install
    cd ../
fi
rm -rf python-boilerpipe
