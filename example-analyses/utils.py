import os
from zipfile import ZipFile
import pandas as pd

dir_ = os.path.realpath(__file__)
dir_ = '/'.join(dir_.split('/')[:-1])


def read_response(contest):
    filename = f'{dir_}/../contests/responses/{contest}'
    with ZipFile(f'{filename}') as myzip:
        csv_file = contest.strip('.zip')
        with myzip.open(csv_file) as f:
            df = pd.read_csv(f, index_col=0)
    return df


def read_summary(contest):
    filename = f'{dir_}/../contests/summaries/{contest}'
    return pd.read_csv(filename, index_col=0)


if __name__ == "__main__":
    df = read_response('513-responses.csv.zip')
    df = read_summary('513_summary_RoundRobin.csv')
