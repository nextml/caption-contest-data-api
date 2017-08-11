import os
from zipfile import ZipFile
import numpy as np
import pandas as pd

dir_ = os.path.realpath(__file__)
dir_ = '/'.join(dir_.split('/')[:-1])


def read_responses(contest, duplicates=None):
    """
    Read an experiment response.

    Parameters
    ----------
    contest : str
        The filename of a *.csv.zip file in the directory responses
    duplicates : str, optional
        * 'keep': keep duplicate caption information
        * 'ignore': treat duplicate captions as the same caption.

    Returns
    -------
    df : pd.DataFrame
        pd.DataFrame with each row describing a response.

       participant_uid
          The ID of each participant, refreshed every time page refreshed (but
          not after each caption)
       timestamp_query_generated
          The timestamp the query was generated
       target_reward
          The target_reward. For most contests, this maps to
          {1: 'unfunny', 2: 'somewhat funny', 3: 'funny'}
       alg_label
          The algorithm that generated this query. LilUCB and KLUCB are
          active, RoundRobin and RandomSampling are passive
       target
          The caption the user saw. They give this algorithm target_reward.

    """

    filename = '{dir_}/../contests/responses/{contest}'.format(dir_=dir_,
            contest=contest)
    with ZipFile('{filename}'.format(filename=filename)) as myzip:
        csv_file = contest.strip('.zip')
        with myzip.open(csv_file) as f:
            df = pd.read_csv(f, index_col=0)
        df['timestamp_query_generated'] = pd.to_datetime(df['timestamp_query_generated'])

    if duplicates not in {None, 'keep', 'ignore'}:
        raise ValueError('duplicates not recognized')

    if duplicates == 'keep' and all(np.isnan(df['target_id'].unique())):
        raise ValueError('Duplicate informatino can not be preserved for this contest')

    if duplicates == 'ignore' or any(np.isnan(df['target_id'].unique())):
        captions = {caption: k
                    for k, caption in enumerate(df['target'].unique())}
        target_ids = df.apply(lambda row: captions[row['target']], axis=1)

        df['target_id'] = target_ids

    return df


def calculate_stats(df, truth=None):
    """
    Calculate the mean, precision of the current ratings

    Parameters
    ----------
    df : pd.DataFrame
	DataFrame with columns ['funny', 'somewhat_funny', 'unfunny']
    truth : pd.DataFrame
        Assumed to be truth

    Returns
    -------
    df : pd.DataFrame
        Modified dataframe with columns ['mean', 'precision', 'rank'] added

    """
    df['count'] = df['unfunny'] + df['somewhat_funny'] + df['funny']
    n = df['count']
    df['score'] = df['unfunny'] + 2*df['somewhat_funny'] + 3*df['funny']
    df['score'] /= n

    reward =  df['unfunny'] + 2*df['somewhat_funny'] + 3*df['funny']
    reward2 = df['unfunny'] + 4*df['somewhat_funny'] + 9*df['funny']

    top = np.maximum(1, reward2 - reward**2 / n)
    bottom = (n - 1) * n

    frac = top / bottom
    df['precision'] = np.sqrt(np.array(frac, dtype=float))

    df = df.sort_values(by='score', ascending=False)
    df['rank'] = np.arange(len(df)) + 1
    # df['rank'] = (-df['score']).argsort() + 1
    return df


def init_summary(df):
    """
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of responses from :func:`read_responses`

    Returns
    -------
    pd.DataFrame
        df.columns == ['count', 'funny', 'somewhat_funny', 'unfunny', 'target_id']
    """
    target_ids = df['target_id'].unique()

    data = []
    for target_id in target_ids:
        data += [{'unfunny': 0, 'somewhat_funny': 0, 'funny': 0, 'count': 0,
                  'target_id': target_id, 'score': np.nan, 'precision': np.nan}]

    return pd.DataFrame(data)


def add_target_ids(summary, responses):
    mapping = {target: k for target, k in zip(responses['target'],
                                              responses['target_id'])}

    target_label = 'caption' if 'caption' in summary.columns else 'target'
    target_ids = summary.apply(lambda row: mapping[row[target_label]], axis=1)
    summary['target_id'] = target_ids

    return summary

def add_captions(summary, responses):
    mapping = {k: target for target, k in zip(responses['target'],
                                              responses['target_id'])}
    target_ids = summary.apply(lambda row: mapping[row['target_id']], axis=1)
    summary['target'] = target_ids

    return summary


def read_summary(contest):
    filename = '{dir_}/../contests/summaries/{contest}'.format(
                                                dir_=dir_, contest=contest)
    df = pd.read_csv(filename, index_col=0)
    df['caption'] = df.apply(lambda row: str(row['caption']).strip('\n'), axis=1)
    df['contest'] = contest

    return df


def add_response(summary, response,
                 mapping={1.0: 'unfunny', 2.0: 'somewhat_funny', 3.0: 'funny'}):
    i = np.argwhere(summary['target_id'] == response['target_id']).flat[0]
    reward = mapping[response['target_reward']]
    summary.loc[i, reward] += 1
    summary.loc[i, 'count'] += 1
    return summary


def summary_from_responses(responses, alg=None,
                           mapping={1: 'unfunny', 2:'somewhat_funny', 3:'funny'}):
    if alg:
        responses = responses[responses['alg_label'] == alg]
    summary = init_summary(responses)
    summary = add_captions(summary, responses)
    summary = add_target_ids(summary, responses)
    summary = summary.T.to_dict()

    for target_id, reward in zip(responses['target_id'], responses['target_reward']):
        summary[target_id][mapping[reward]] += 1

    summary = pd.DataFrame(summary).T
    summary = calculate_stats(summary)

    return summary


def read_all_responses():
    data = []
    for filename in os.listdir(dir_ + '/../contests/responses/'):
        if 'Store' in filename or any([d in filename for d in ['497', '499', 'dueling']]):
            continue
        df = read_responses(filename)
        name = filename.strip('-responses.csv.zip')
        df['contest-name'] = name
        data += [df]
    return pd.concat(data)


def read_all_summaries():
    """
    Read all summaries.

    Returns
    -------
    df : pd.DataFrame
        Dataframe with all summaries from all algorithms and all contests.

    Notes
    -----
    - Some contests have more than one
    - Contests 527, 528, 529, 530 and 531 are missing the rank column. These
      missing values castered to `np.nan`.

    """
    data = []
    for filename in os.listdir(dir_ + '/../contests/summaries/'):
        if any([d in filename for d in ['497', '499', 'dueling', 'munging', 'Store']]):
            continue
        df = read_summary(filename)
        print(filename)
        print(df.columns)
        contest = int(filename.split('_')[0])
        alg = filename.replace('.csv', '').strip('_')[-1]
        df['contest'] = contest
        df['alg'] = alg
        data += [df]
    return pd.concat(data)


if __name__ == "__main__":
    df = read_all_summaries()

    if False:
        # read_summary('520_summary_LilUCB.csv')
        contest = '559-active'
        responses = read_responses('{contest}-responses.csv.zip'.format(contest=contest))
        # print(responses.head())
        summary_hat = {}
        for alg in ['LilUCB', 'KLUCB']:
            summary_hat = summary_from_responses(responses, alg=alg)

            ranks = {rank: score for rank, score in zip(summary_hat['rank'],
                                                        summary_hat['score'])}
            for i in np.arange(1, len(ranks) - 1):
                assert ranks[i] >= ranks[i+1]
