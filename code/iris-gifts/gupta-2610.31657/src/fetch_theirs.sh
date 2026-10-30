#!/bin/sh
# Downloads the author's Zenodo supplement (record 22654013) into ../theirs, checks its hash, and unpacks it to theirs/unz.
set -e
cd "$(dirname "$0")/.."; mkdir -p theirs; cd theirs
curl -sL -o supplement.zip https://zenodo.org/api/records/22654013/files/routeguard_camera_ready_supplementary.zip/content
echo "22535c8389b0bcaaf08a8aed140e7c60651042b64a5ff2137798e2cc243d7471  supplement.zip" | shasum -a 256 -c -
python3 -I -c "import zipfile; zipfile.ZipFile('supplement.zip').extractall('unz')"
