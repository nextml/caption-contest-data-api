import pandas as pd
import numpy as np


def find_score_prec(s):
    # The user submits "funny" which we map to "3"
    n = s['Funny'] + s['Somewhat funny'] + s['Unfunny']
    reward = (s['Funny']*3 + s['Somewhat funny']*2 + s['Unfunny'])
    reward_squared = s['Funny']*9 + s['Somewhat funny']*4 + s['Unfunny']

    # computing the average score the users gave
    score = reward / n

    # computing the precision/standard deviation
    top = np.maximum(1, reward_squared - reward**2 / n)
    bottom = (n - 1) * n
    prec = np.sqrt(top / bottom)

    return score, prec

if __name__ == "__main__":
    contest = '576'
    csv = pd.read_csv('./_private/{}_summary.csv'.format(contest))
    del csv['email']
    #  csv.to_excel('./531_summary.xlsx')
    csv.to_csv('{}_summary_KLUCB.csv'.format(contest))

    caption_counts =  csv['caption'].value_counts()
    repeat_captions = caption_counts[caption_counts > 1]

    files = {f'{contest}': csv['caption'].values.astype('str'),
             f'{contest}_repeat': list(repeat_captions.index)}

    for prefix, captions in files.items():
        with open('{}_captions.csv'.format(prefix), 'w') as f:
            captions = "\n".join(captions)
            print(captions, file=f)
