import requests
import sys
import pandas as pd

def _get_json(url):
    r = requests.get(url)
    return r.json()

def get_target(targets, id):
    for target in targets:
        print(target, type(target))
        if int(target['target_id']) == int(id):
            return target
    raise ValueError('Target not found in targets')

if len(sys.argv) < 3:
    raise ValueError('Usage: get_summary_csv.py [exp_uid] [contest]')

exp_uid = sys.argv[1]
contest = sys.argv[2]

url = f'https://s3-us-west-2.amazonaws.com/next2-cardinalbandits/{exp_uid}/'

targets = _get_json(url + 'targets.json')
ranks = _get_json(url + 'ranks.json')

df = pd.DataFrame(ranks, columns=['target_id', 'mean', 'precision', 'count'])
targets = pd.DataFrame(targets)
targets['target_id'] = pd.to_numeric(targets['target_id'])
df = df.merge(targets, on='target_id')

df['score'] = df['mean']
df['caption'] = df['primary_description']
for key in ['alt_description', 'alt_type', 'primary_type', 'primary_description']:
    del df[key]

df['contest'] = contest
df['exp_uid'] = exp_uid

df.to_csv(f'_private/{contest}_summary.csv')
del df['email']
del df['exp_uid']
df.to_csv(f'{contest}_summary_KLUCB.csv')

caption_counts = df['caption'].value_counts()
repeat_captions = caption_counts[caption_counts > 1]
files = {f'{contest}': df['caption'].values.astype('str'),
         f'{contest}_repeat': list(repeat_captions.index)}

for prefix, captions in files.items():
    with open('{}_captions.csv'.format(prefix), 'w') as f:
        captions = "\n".join(captions)
        print(captions, file=f)
