#!/bin/bash

# Set LD_LIBRARY_PATH to include Python libraries
export LD_LIBRARY_PATH="/opt/hostedtoolcache/Python/3.12.3/x64/lib:$LD_LIBRARY_PATH"

# Add your commands here
python script.py
