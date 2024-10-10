#!/bin/bash

# URL to the manifest
MANIFEST_URL="https://registry.ollama.ai/v2/library/llama3.2/manifests/1b"

# Function to download a file from the registry
download_file() {
    local digest=$1
    local url="https://registry.ollama.ai/v2/library/llama3.2/blobs/${digest}"
    local file_name="blobs/${digest}" # Use the full digest as the file name

    # Create the directory if it doesn't exist
    mkdir -p $(dirname "$file_name")

    # Download the file
    echo "Downloading $url to $file_name"
    curl -L -o "$file_name" "$url"
}

# Fetch the manifest JSON
manifest_json=$(curl -s "$MANIFEST_URL")

# Extract the digest values from the JSON
digests=$(echo "$manifest_json" | jq -r '.layers[].digest')

# Download each file
for digest in $digests; do
    download_file "$digest"
done

# Download the config file
config_digest=$(echo "$manifest_json" | jq -r '.config.digest')
download_file "$config_digest"