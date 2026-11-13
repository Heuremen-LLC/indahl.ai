import os,shutil,sys
from huggingface_hub import HfApi
B='/Users/heuremen/bones-forge/'
tok=open(os.path.expanduser('~/.cache/huggingface/token')).read().strip()
api=HfApi(token=tok)
existing={d.id for d in api.list_datasets(author='indahl')}
P={
 'atlas-data-pack':dict(src=B+'atlas_package/dist/atlas-data-pack',title='ATLAS Data Pack',page='https://indahl.ai/atlas',
  tags=['energy','electricity','data-centers','power-plants','geospatial','openstreetmap','eia','egrid'],
  lic='ATLAS',
  cfg={'plants':'csv/plants.csv','planned':'csv/planned.csv','planned_generators':'csv/planned_generators.csv','datacenters_osm':'csv/datacenters_osm.csv','datacenters_epoch':'csv/datacenters_epoch.csv','electricity_states':'csv/electricity_states.csv','utilities':'csv/utilities.csv','carbon_states':'csv/carbon_states.csv','carbon_subregions':'csv/carbon_subregions.csv','scale_sites':'csv/scale_sites.csv','scale_states':'csv/scale_states.csv'},
  default='plants'),
 'oy-data-pack':dict(src=B+'oy_package/dist/oy-data-pack',title='OY Data Pack',page='https://indahl.ai/oy',
  tags=['education','higher-education','ai-policy','reproducibility'],lic='',
  cfg={'schools':'csv/oy_schools.csv','school_sentences':'csv/oy_school_sentences.csv','school_course_titles':'csv/oy_school_course_titles.csv','findings':'csv/oy_findings.csv','finding_institutions':'csv/oy_finding_institutions.csv','chatbot_citations':'csv/oy_chatbot_citations.csv','list':'csv/oy_list.csv'},default='schools'),
 'model-data-pack':dict(src=B+'model_package/dist/model-data-pack',title='MODEL Data Pack',page='https://indahl.ai/hermes/model',
  tags=['mlperf','mlcommons','hardware','benchmarks','reproducibility'],lic='',
  cfg={'claims':'csv/claims.csv','claims_sources':'csv/claims_sources.csv','claims_tally':'csv/claims_tally.csv','accelerators':'csv/accelerators.csv','accelerators_summary':'csv/accelerators_summary.csv','storage_v30_rows':'csv/storage_v30_rows.csv'},default='claims'),
}
for name,p in P.items():
    rid='indahl/'+name
    if rid in existing: print('SKIP exists',rid); continue
    st='/tmp/hfstage_'+name
    shutil.rmtree(st,ignore_errors=True); os.makedirs(st)
    for root,_,fs in os.walk(p['src']):
        for f in fs:
            if f in('verify.py','START_HERE.html'):continue
            s=os.path.join(root,f); r=os.path.relpath(s,p['src'])
            os.makedirs(os.path.dirname(os.path.join(st,r)) or st,exist_ok=True); shutil.copy(s,os.path.join(st,r))
    base='https://huggingface.co/datasets/'+rid+'/blob/main/'
    if p['lic']=='ATLAS':
        lic_name='odbl-1.0-and-cc-by-4.0-by-file'
        licline='Licences differ by file. OpenStreetMap-derived files are under the ODbL 1.0 and Epoch AI-derived files are under CC BY 4.0, as the pack LICENSE.txt says. Files that hold both carry both. EIA, EPA and US Census data are public domain.'
    elif name=='model-data-pack':
        lic_name='apache-2.0-for-mlcommons-results-see-license-txt'
        licline='Licences differ by file. MLCommons-derived files are under the Apache License 2.0 and the rest follow the pack LICENSE.txt.'
    else:
        lic_name='heuremen-and-source-terms-see-license-txt'
        licline='Each part keeps the terms of its source and Heuremen LLC adds no restriction. See LICENSE.txt.'
    readme=open(os.path.join(st,'README.md'),encoding='utf-8').read()
    body=readme.split('\n',1)[1] if readme.startswith('# ') else readme
    fm=['---','pretty_name: "%s"'%p['title'],'license: other','license_name: %s'%lic_name,'license_link: %sLICENSE.txt'%base,'tags:']+['- '+t for t in p['tags']]+['configs:']
    for c,f in p['cfg'].items():
        fm+=['- config_name: '+c,'  '+('default: true' if c==p['default'] else 'data_files: %s'%f)] if False else []
        fm+=['- config_name: '+c]+(['  default: true'] if c==p['default'] else [])+['  data_files: '+f]
    fm+=['---','']
    intro=('# %s\n\nThis is the same data as the download on indahl.ai, published here for the Hugging Face viewer and the datasets library. The page is %s . The files were tested before release, and what was opened and compared is in [TESTED.md](%sTESTED.md). The checking script `verify.py` and the guide page `START_HERE.html` are in the download from indahl.ai and are not copied here. %s Full terms: [LICENSE.txt](%sLICENSE.txt).\n')%(p['title'],p['page'],base,licline,base)
    open(os.path.join(st,'README.md'),'w',encoding='utf-8').write('\n'.join(fm)+intro+body)
    api.create_repo(rid,repo_type='dataset',exist_ok=False)
    api.upload_folder(folder_path=st,repo_id=rid,repo_type='dataset',commit_message='Add data pack')
    print('CREATED',rid)
