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

    filename = f'{dir_}/../contests/responses/{contest}'
    with ZipFile(f'{filename}') as myzip:
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
	DataFrame with columns ['count', 'funny', 'somewhat_funny', 'unfunny']
    truth : pd.DataFrame
        Assumed to be truth

    Returns
    -------
    df : pd.DataFrame
        Modified dataframe with columns ['mean', 'precision', 'rank'] added

    """
    n = df['count']
    df['score'] = df['unfunny'] + 2*df['somewhat_funny'] + 3*df['funny']
    df['score'] /= n

    df['rank'] = (-df['score']).argsort() + 1

    reward =  df['unfunny'] + 2*df['somewhat_funny'] + 3*df['funny']
    reward2 = df['unfunny'] + 4*df['somewhat_funny'] + 9*df['funny']

    top = np.maximum(1, reward2 - reward**2 / n)
    bottom = (n - 1) * n

    df['precision'] = np.sqrt(top / bottom)
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
    target_ids = summary.apply(lambda row: mapping[row['caption']], axis=1)
    summary['target_id'] = target_ids

    return summary


def read_summary(contest):
    filename = f'{dir_}/../contests/summaries/{contest}'
    df = pd.read_csv(filename, index_col=0)
    df['caption'] = df.apply(lambda row: str(row['caption']).strip('\n'), axis=1)

    return df


if __name__ == "__main__":
    read_summary('520_summary_LilUCB.csv')
