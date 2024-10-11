from flask import Flask, redirect, request, Response
import requests

app = Flask(__name__)

@app.route('/v2/<namespace>/<name>/blobs/<sha>', methods=['GET', "HEAD"])
def blobs(namespace, name, sha):
    oid = sha.split(':')[1]
    r = requests.get(f'https://huggingface.co/api/models/{namespace}/{name}/tree/main')
    result = r.json()

    resp = Response()
    for r in result:
        if oid == r['oid'] or ('lfs' in r and oid == r['lfs']['oid']):
            print(f'https://huggingface.co/{namespace}/{name}/resolve/main/{r["path"]}')
            resp.status_code = 307
            resp.headers['Location'] = f'https://huggingface.co/{namespace}/{name}/resolve/main/{r["path"]}'
            resp.headers['Content-Type'] = 'application/octet-stream'
    return resp

@app.route('/v2/<namespace>/<name>/manifests/<tag>', methods=['GET'])
def manifest(namespace, name, tag):
    r = requests.get(f'https://huggingface.co/api/models/{namespace}/{name}/tree/main')
    result = r.json()

    model = None
    model_size = 0
    config = None
    config_size = 0
    system = None
    system_size = 0
    template = None
    template_size = 0
    license = None
    license_size = 0

    for r in result:
        if r['path'] == 'config.json':
            config = r['oid']
            config_size = r['size']
        if r['path'] == 'system':
            system = r['oid']
            system_size = r['size']
        if r['path'].endswith('.gguf'):
            if 'lfs' in r:
                model = 'sha256:' + r['lfs']['oid']
                model_size = r['lfs']['size']
            else:
                model = 'sha1:' + r['oid']
                model_size = r['size']
        if r['path'] == 'template':
            template = r['oid']
            template_size = r['size']
        if r['path'] == 'license':
            license = r['oid']
            license_size = r['size']

    manifest = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "config": {
            "digest": f"sha1:{config}",
            "mediaType": "application/vnd.docker.container.image.v1+json",
            "size": config_size
        } if config else None,
        "layers": []
    }

    if model:
        manifest["layers"].append({
            "digest": model,
            "mediaType": "application/vnd.ollama.image.model",
            "size": model_size
        })

    if system:
        manifest["layers"].append({
            "digest": f"sha1:{system}",
            "mediaType": "application/vnd.ollama.image.system",
            "size": system_size
        })

    if template:
        manifest["layers"].append({
            "digest": f"sha1:{template}",
            "mediaType": "application/vnd.ollama.image.template",
            "size": template_size
        })

    if license:
        manifest["layers"].append({
            "digest": f"sha1:{license}",
            "mediaType": "application/vnd.ollama.image.license",
            "size": license_size
        })
    print(manifest)
    return manifest

app.run(debug=True, host='0.0.0.0', port=4242)