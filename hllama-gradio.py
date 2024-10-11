import gradio as gr
import os
import requests
import json
from huggingface_hub import HfApi

def download_file(digest, image):
    url = f"https://registry.ollama.ai/v2/library/{image}/blobs/{digest}"
    file_name = f"blobs/{digest}"

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    # Download the file
    print(f"Downloading {url} to {file_name}")
    response = requests.get(url, allow_redirects=True)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download {url}")

def fetch_manifest(image, tag):
    manifest_url = f"https://registry.ollama.ai/v2/library/{image}/manifests/{tag}"
    response = requests.get(manifest_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def upload_to_huggingface(repo_id, folder_path):
    api = HfApi()
    try:
        api.upload_folder(
            folder_path=folder_path,
            repo_id=repo_id,
            repo_type="model",
        )
        return "Upload successful"
    except Exception as e:
        return f"Upload failed: {str(e)}"

def process_image_tag(image_tag, repo_id):
    # Extract image and tag from the input
    image, tag = image_tag.split(':')

    # Fetch the manifest JSON
    manifest_json = fetch_manifest(image, tag)
    if not manifest_json or 'errors' in manifest_json:
        return f"Failed to fetch the manifest for {image}:{tag}"

    # Save the manifest JSON to the blobs folder
    manifest_file_path = "blobs/manifest.json"
    os.makedirs(os.path.dirname(manifest_file_path), exist_ok=True)
    with open(manifest_file_path, 'w') as f:
        json.dump(manifest_json, f)

    # Extract the digest values from the JSON
    digests = [layer['digest'] for layer in manifest_json.get('layers', [])]

    # Download each file
    for digest in digests:
        download_file(digest, image)

    # Download the config file
    config_digest = manifest_json.get('config', {}).get('digest')
    if config_digest:
        download_file(config_digest, image)

    # Upload to Hugging Face Hub
    upload_result = upload_to_huggingface(repo_id, 'blobs')

    # Delete the blobs folder
    try:
        os.rmtree('blobs')
        return f"Successfully fetched and downloaded files for {image}:{tag}\n{upload_result}\nBlobs folder deleted"
    except Exception as e:
        return f"Failed to delete blobs folder: {str(e)}"

# Create the Gradio interface
iface = gr.Interface(
    fn=process_image_tag,
    inputs=[
        gr.Textbox(placeholder="Enter image:tag", label="Image and Tag"),
        gr.Textbox(placeholder="Enter Hugging Face repo ID", label="Hugging Face Repo ID")
    ],
    outputs=gr.Textbox(label="Result"),
    title="Registry File Downloader and Uploader",
    description="Enter the image and tag to download the corresponding files from the registry and upload them to the Hugging Face Hub."
)

# Launch the Gradio app
iface.launch()