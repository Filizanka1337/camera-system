#!/bin/bash

# Checking Python version
python3 --version | grep "Python 3.9" >/dev/null

if [ $? -ne 0 ]; then
    # Python 3.9 is not installed, using apt-get to install
    sudo apt-get update
    sudo apt-get install python3.9
fi

# Reading the "requirements.txt" file
while IFS= read -r line; do
    # Installing libraries using pip
    python3 -m pip install "$line"
done < requirements.txt

echo "Installation completed."
