import os
import pandas as pd
import utils

def get_stats(filename):
    print(filename)
    df = utils.read_responses(filename)
    n_captions = len(df['target'].unique())
    n_responses = len(df)
    n_participants = len(df['participant_uid'].unique())

    return {'n_captions': n_captions,
            'n_responses': n_responses,
            'n_participants': n_participants,
            'contest': filename.split('-')[0]}

if False:
    data = [get_stats(filename)
            for filename in os.listdir('../contests/responses')
            if 'zip' in filename and all([s not in filename
                                         for s in ['dueling', '499', '497']])]
    df = pd.DataFrame(data)
    df.to_csv('basic-stats.csv')
else:
    df = pd.read_csv('basic-stats.csv')

total_contests = len(df['contest'].unique())
total_ratings = df['n_responses'].sum()

avg_ratings = df['n_responses'].mean()
avg_users = df['n_participants'].mean()
max_ratings = df['n_responses'].max()
max_users = df['n_participants'].max()

print(f"total_contests = {total_contests}")
print(f"total_ratings = {total_ratings}")
print(f"avg_ratings = {avg_ratings}")
print(f"avg_ussrk = {avg_users}")
print(f"max_ratings = {max_ratings}")
print(f"max_ussrk = {max_users}")

recent = (df.contest >= 555) & (df.n_responses >= 100e3)
recent_avg_responses = df[recent]['n_responses'].mean()
recent_avg_users = df[recent]['n_participants'].mean()

print(recent_avg_responses)
print(recent_avg_users)
