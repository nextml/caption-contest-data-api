"""
This script saves a .mat file for different contests.

The rows of the table are the participant ID indices and the columns are the
caption indices. The value in X_ij is the rating for participant i on
caption j.

It saves several of these matrices X for different contests. For example, the X
matrix for contest 535 is named "X_535".

"""

import pandas as pd
import numpy as np
from scipy.io import savemat, loadmat


def get_responses(contest, dir_='../contests/adaptive/'):
    responses = pd.read_csv(dir_ + contest + '/participant_responses_LilUCB.csv')
    matrix = responses.pivot_table(index='Partipipant ID', columns='Target',
                                   values='Rating')
    matrix = matrix.fillna(0)
    return matrix.values

responses = {'X_' + contest: get_responses(contest).astype('int')
             for contest in ['535', '536']}

savemat('responses_535_536.mat', responses, do_compression=True)
np.savez('responses', **responses)
data = loadmat('responses_535_536.mat')
print(data.keys())
