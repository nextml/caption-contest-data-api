import os
import pandas as pd

dir_ = os.path.realpath(__file__)
dir_ = '/'.join(dir_.split('/')[:-1]) + '/'


def read_responses(contest):
    return pd.read_csv(dir_ + 'responses-unzipped/' + contest + '-responses.csv')


def read_summary(contest, alg='LilUCB'):
    return pd.read_csv(f'{dir_}summaries/{contest}_summary_{alg}.csv')



if __name__ == "__main__":
    df = read_responses('513')
    df = read_summary('513')
