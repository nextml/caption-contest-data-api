from zipfile import ZipFile
import pandas as pd
from scipy.io import savemat


def read_filename(filename):
    with ZipFile(f'../contests/responses/{filename}') as myzip:
        csv_file = filename.replace('.zip', '')
        with myzip.open(csv_file) as f:
            df = pd.read_csv(f, index_col=0)
    print(df.columns)
    return df[['left_target_id', 'right_target_id', 'winner_target_id']].values

filename = '497-responses.csv.zip'
for filename in ['497-responses.csv.zip',
                 '508-round2-dueling-responses.csv.zip',
                 '509-round2-dueling-responses.csv.zip']:
    contest = filename[:3]
    left_right_winner = read_filename(filename)
    print(len(left_right_winner))
    savemat(f'{contest}_responses.mat', {'left_right_winner': left_right_winner})
    if '497' in filename: break
