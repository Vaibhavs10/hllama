#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <hf-repo> <hf-file>"
    exit 1
fi

# Assign the input arguments to variables
hf_repo="$1"
hf_file="$2"

# Download the file from the Hugging Face repository
echo "Downloading file from Hugging Face repository..."
huggingface-cli download "$hf_repo" "$hf_file" --local-dir temp

# Check if the download was successful
if [ $? -ne 0 ]; then
    echo "Failed to download the file."
    exit 1
fi

# Create the Modelfile with the specified content
echo "Creating Modelfile..."
echo "FROM ./$hf_file" > Modelfile

# Check if the file was created successfully
if [ $? -ne 0 ]; then
    echo "Failed to create Modelfile."
    exit 1
fi

echo "Modelfile created successfully."