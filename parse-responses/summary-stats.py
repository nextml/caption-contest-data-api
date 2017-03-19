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


if True:
    contest = '560'
    csv = pd.read_csv('./_private/{}_summary.csv'.format(contest))
    del csv['email']
    #  csv.to_excel('./531_summary.xlsx')
    csv.to_csv('{}_summary_KLUCB.csv'.format(contest))
    captions = "\n".join(csv['caption'].values.astype('str'))

    with open('{}_captions.csv'.format(contest), 'w') as f:
        print(captions, file=f)
else:
    # Read in the summary file (downloaded from dashboard then copy pasted into
    # file)
    # s == summary (but s is quicker to type than summary)
    filename = './531_summary.csv'
    contest = '527'
    for contest in ['527', '528', '529', '530']:
        filename = '../adaptive-only-contests/{0}/{0}_summary_LilUCB.csv'.format(contest)

        s = pd.read_csv(filename)
        score, prec = find_score_prec(s)
        s['Score'] = score
        s['Precision'] = prec

        s.sort_values(by='Score', ascending=False, inplace=True)

        s.to_csv('{0}_summary_LilUCB-more.csv'.format(contest))
        s.to_excel('{0}_summary.xlsx'.format(contest))
