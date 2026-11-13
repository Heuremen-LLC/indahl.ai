import os
from huggingface_hub import HfApi
api = HfApi(); rid = 'indahl/readout-run-data'; S = os.path.expanduser('~/bones-forge/hf_indahl/stage/readout-run-data'); Z = os.path.expanduser('~/Desktop/ZENODO_v5_UPLOAD/A_Readout_Is_Not_an_Idle_raw_v5.zip')
api.create_repo(rid, repo_type='dataset', exist_ok=True)
api.upload_folder(folder_path=S, repo_id=rid, repo_type='dataset', commit_message='Heuremen LLC: readout paper data card and code bundle')
print('card and code bundle uploaded', flush=True)
api.upload_file(path_or_fileobj=Z, path_in_repo='A_Readout_Is_Not_an_Idle_raw_v5.zip', repo_id=rid, repo_type='dataset', commit_message='Heuremen LLC: raw bundle (2.95 GB)')
print('raw bundle uploaded', 'https://huggingface.co/datasets/' + rid, flush=True)
