import os
import numpy as np
import pandas as pd
import utils


def test_read_summary():
    df = utils.read_summary('513')


def test_read_responses():
    df = utils.read_responses('513')


def test_responses():
    dir = 'responses-unzipped/'
    exp_ids = []
    last_header = None
    for file in os.listdir(dir):
        if 'DS_Store' in file or '.md' in file or os.path.isdir(dir + file):
            continue
        df = pd.read_csv(f'{dir}/{file}')
        exp_ids += [df.iloc[0]['participant_uid'].split('_')[0]]

        if last_header is not None:
            if all([s not in file for s in ['dueling', '499', '497']]):
                assert all(last_header == df.columns)
                last_header = df.columns

    assert len(exp_ids) == len(set(exp_ids))


def test_summaries():
    dir = 'summaries/'
    last_header = None
    global file
    for file in os.listdir(dir):
        if 'DS_Store' in file or os.path.isdir(dir + file):
            continue
        df = pd.read_csv(f'{dir}/{file}')

        if last_header is not None:
            if all([s not in file for s in ['dueling', '499', '497']]):
                assert all(last_header == df.columns)
                last_header = df.columns

if __name__ == "__main__":
    test_summaries()
