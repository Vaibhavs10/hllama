#!/bin/bash

# Function to download a file from the registry
download_file() {
    local digest=$1
    local url="https://registry.ollama.ai/v2/library/${IMAGE}/blobs/${digest}"
    local file_name="blobs/${digest}" # Use the full digest as the file name

    # Create the directory if it doesn't exist
    mkdir -p $(dirname "$file_name")

    # Download the file
    echo "Downloading $url to $file_name"
    curl -L -o "$file_name" "$url"
}

# Check if an input is provided
if [ -z "$1" ]; then
    echo "Usage: $0 image:tag"
    exit 1
fi

# Extract image and tag from the input
IMAGE=$(echo "$1" | cut -d: -f1)
TAG=$(echo "$1" | cut -d: -f2)

# Construct the manifest URL
MANIFEST_URL="https://registry.ollama.ai/v2/library/${IMAGE}/manifests/${TAG}"

# Fetch the manifest JSON
manifest_json=$(curl -s "$MANIFEST_URL")

# Save the manifest JSON to a file
echo "$manifest_json" > manifest

# Check if the manifest JSON is empty or contains an error
if [ -z "$manifest_json" ] || echo "$manifest_json" | grep -q '"errors":'; then
    echo "Failed to fetch the manifest for ${IMAGE}:${TAG}"
    exit 1
fi

# Extract the digest values from the JSON
digests=$(echo "$manifest_json" | jq -r '.layers[].digest')

# Download each file
for digest in $digests; do
    download_file "$digest"
done

# Download the config file
config_digest=$(echo "$manifest_json" | jq -r '.config.digest')
download_file "$config_digest"