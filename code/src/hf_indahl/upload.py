"""upload.py: pushes hf_indahl/stage/* to huggingface.co/indahl as dataset repos. Needs a write login for the indahl account (hf auth login). Never prints the token."""
import os
from huggingface_hub import HfApi
api = HfApi(); S = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stage'); me = api.whoami()['name']; print('logged in as', me)
for r in sorted(os.listdir(S)):
    rid = f'indahl/{r}'
    api.create_repo(rid, repo_type='dataset', exist_ok=True)
    api.upload_folder(folder_path=os.path.join(S, r), repo_id=rid, repo_type='dataset', commit_message='Heuremen LLC: ' + r)
    print('uploaded', rid)
