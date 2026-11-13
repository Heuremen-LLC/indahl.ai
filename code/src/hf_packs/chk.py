import os,urllib.request
from huggingface_hub import HfApi
api=HfApi(token=open(os.path.expanduser('~/.cache/huggingface/token')).read().strip())
for n in ['atlas-data-pack','oy-data-pack','model-data-pack']:
    r='indahl/'+n
    c=urllib.request.urlopen('https://huggingface.co/datasets/'+r).status
    i=api.dataset_info(r)
    print(r,c,len(i.siblings),'files, configs:',[x['config_name'] for x in i.card_data.configs], 'license',i.card_data.license)
    try:
        import json
        v=urllib.request.urlopen('https://datasets-server.huggingface.co/is-valid?dataset='+r,timeout=20).read().decode();print(' valid',v)
    except Exception as e: print(' valid err',e)
