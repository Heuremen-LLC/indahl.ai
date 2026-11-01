#!/bin/bash
# set_pypi_token.sh: swap the PyPI token. Copy a new token to the clipboard, run this. It validates the prefix, writes ~/.pypirc (mode 600), updates the GitHub secret PYPI_API_TOKEN, and clears the clipboard. Nothing is printed.
set -euo pipefail; umask 077
T=$(pbpaste); [[ "$T" == pypi-* ]] || { echo "clipboard is not a PyPI token"; exit 1; }
printf '[distutils]\nindex-servers =\n    pypi\n\n[pypi]\nusername = __token__\npassword = %s\n' "$T" > ~/.pypirc; chmod 600 ~/.pypirc
gh secret set PYPI_API_TOKEN --repo Heuremen-LLC/faultsguards --body "$T" >/dev/null
unset T; printf '' | pbcopy; echo "token stored in ~/.pypirc and the GitHub secret; clipboard cleared"
