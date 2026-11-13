"""upload_darkwave_hf.py -- at the release: the Darkwave bundles to huggingface.co/datasets/indahl/darkwave-run-data, beside readout-run-data
(one place: every dataset on the site lives on the indahl account). Signs in with the stored token named oauth-indahl, never printed."""
import os, hashlib
from huggingface_hub import HfApi
try: from huggingface_hub import get_stored_tokens
except ImportError: from huggingface_hub.utils import get_stored_tokens
A = os.path.dirname(os.path.abspath(__file__)); Z = os.path.join(A, 'zenodo'); rid = 'indahl/darkwave-run-data'
code = os.path.join(Z, 'A_Readouts_Kick_Is_a_Turn_code_and_results.zip')
assert hashlib.sha256(open(code, 'rb').read()).hexdigest() in open(os.path.join(A, 'hf_stage', 'README.md')).read(), 'the card hash does not match the bundle'
api = HfApi(token=get_stored_tokens()['oauth-indahl'])
api.create_repo(rid, repo_type='dataset', exist_ok=True)
api.upload_file(path_or_fileobj=os.path.join(A, 'hf_stage', 'README.md'), path_in_repo='README.md', repo_id=rid, repo_type='dataset', commit_message='Heuremen LLC: Darkwave data card')
for f in ('A_Readouts_Kick_Is_a_Turn_code_and_results.zip', 'A_Readouts_Kick_Is_a_Turn_raw.zip'):
    api.upload_file(path_or_fileobj=os.path.join(Z, f), path_in_repo=f, repo_id=rid, repo_type='dataset', commit_message='Heuremen LLC: ' + f)
print('Darkwave data on Hugging Face: https://huggingface.co/datasets/' + rid)
