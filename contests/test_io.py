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
        df = utils.read_responses(file)
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


def test_calculate_stats():
    df = utils.read_summary('513_summary_RoundRobin.csv')
    for key in ['precision', 'rank']:
        del df[key]
    summary = utils.calculate_stats(df)

    for key in ['rank', 'score', 'precision']:
        assert all(summary[key] == df[key])


def test_summary_rank():
    responses = utils.read_responses('513-responses.csv.zip')
    summary = utils.init_summary(responses)
    summary = utils.read_summary('559_summary_LilUCB.csv')

    df = utils.calculate_stats(summary)

    mapping = {rank: mean for rank, mean in zip(df['rank'], df['score'])}
    for i in range(len(mapping) - 1):
        assert mapping[i + 1] >= mapping[i + 2]


def test_init_summary():
    responses = utils.read_responses('514-responses.csv.zip')
    global summary
    global key
    summary = utils.init_summary(responses)

    df = utils.read_summary('514_summary_LilUCB.csv')

    for key in ['score', 'funny', 'unfunny', 'somewhat_funny', 'precision']:
        assert key in df.columns
        assert key in summary.columns


def test_add_target_ids_to_summary():
    truth = utils.read_summary('513_summary_LilUCB.csv')
    responses = utils.read_responses('513-responses.csv.zip')

    truth = utils.add_target_ids(truth, responses)
    for target_id in truth['target_id'].unique():
        df1 = truth[truth['target_id'] == target_id]
        df2 = responses[responses['target_id'] == target_id]

        assert all(df1['target_id'].values[0] == df2['target_id'])

if __name__ == "__main__":
    # test_responses()
    test_summaries()
    # test_calculate_stats()
    # test_summary_rank()
    # test_init_summary()
    # test_add_target_ids_to_summary()
