#!/bin/sh
# Downloads the authors' OSF release zip into ../theirs, checks its hash, and unpacks the two files this recount reads into theirs/release.
set -e
cd "$(dirname "$0")/.."; mkdir -p theirs/release; cd theirs
curl -sL -o release.zip https://osf.io/download/tjec3/
echo "366d7acfff7edeeefdd9a7f7991a376af911eb5723003cc7188693e50c9b6821  release.zip" | shasum -a 256 -c -
python3 -I -c "import zipfile; z = zipfile.ZipFile('release.zip'); [open('release/' + n, 'wb').write(z.read(n)) for n in ('per_side_outcomes.csv', 'rerun_cells_release.csv')]"
shasum -a 256 release/per_side_outcomes.csv release/rerun_cells_release.csv
