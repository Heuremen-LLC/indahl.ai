"""upload_manual.py: pushes ONE folder from hf_indahl/manual/ (never stage/, which the mirror rider rewipes) to huggingface.co/indahl as a dataset repo.
Usage: python3 upload_manual.py iris-house-training. Needs the indahl write login (hf auth login); never prints the token."""
import os, sys
from huggingface_hub import HfApi
M = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manual'); r = sys.argv[1]; src = os.path.join(M, r)
assert os.path.isdir(src) and '/manual/' in src, 'upload source must be under hf_indahl/manual/'
api = HfApi(); print('logged in as', api.whoami()['name'])
api.create_repo(f'indahl/{r}', repo_type='dataset', exist_ok=True)
api.upload_folder(folder_path=src, repo_id=f'indahl/{r}', repo_type='dataset', commit_message='Heuremen LLC: ' + r)
print('uploaded', f'indahl/{r}')
