import os, sys
import numpy as np
import pandas as pd
contest_dir = '/'.join(__file__.split('/')[:-1])
sys.path.append('{contest_dir}/../example-analyses'.format(contest_dir=contest_dir))
import utils


def test_responses():
    dir = '{contest_dir}/responses/'.format(contest_dir=contest_dir)
    exp_ids = []
    last_header = None
    for file in os.listdir(dir):
        if 'DS_Store' in file or '.md' in file or os.path.isdir(dir + file):
            continue
        if any([s in file for s in ['dueling', '499', '497']]):
            continue
        df = utils.read_response(file)
        exp_ids += [df.iloc[0]['participant_uid'].split('_')[0]]

        if last_header is not None:
            assert all(last_header == df.columns)
            last_header = df.columns

    assert len(exp_ids) == len(set(exp_ids))


def test_summaries():
    dir = '{contest_dir}/summaries/'.format(contest_dir=contest_dir)
    last_header = None
    for file in os.listdir(dir):
        if 'DS_Store' in file or os.path.isdir(dir + file):
            continue
        df = utils.read_summary(file)

        if last_header is not None:
            if all([s not in file for s in ['dueling', '499', '497']]):
                assert all(last_header == df.columns)
                last_header = df.columns

if __name__ == "__main__":
    test_summaries()
    test_responses()
