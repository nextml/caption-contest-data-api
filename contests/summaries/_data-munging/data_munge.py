import os
import pandas as pd

def format_csv(file, dir='summaries-raw'):
    """
    Used to convert to uniform CSV interface (pandas w/ unfirom columns)
    """
    with open(dir + file) as f:
        lines = [line[:-1] for line in f.readlines()]
    header = lines[0].split(',')
    complete = 'score' in header or 'Score' in header

    if complete:
        df = pd.read_csv(dir + file)
        df.columns = [label.lower() for label in df.columns]
        del df['unnamed: 0']
    if not complete:
        data = [line.split(',', maxsplit=3) for line in lines]
        data = [{label.lower().replace(' ', '_'): datum[i]
                 for i, label in enumerate(header)}
                for datum in data[1:]]
        data = [{key: float(value) if 'funny' in key else value
                 for key, value in datum.items()} for datum in data]

        df = pd.DataFrame(data)
        n = df['funny'] + df['somewhat_funny'] + df['unfunny']
        reward = df['funny']*3 + df['somewhat_funny']*2 + df['unfunny']
        reward_squared = df['funny']*9 + df['somewhat_funny']*4 + df['unfunny']

        # computing the precision/standard deviation
        top = np.maximum(1, reward_squared - reward**2 / n)
        bottom = (n - 1) * n
        prec = np.sqrt(top / bottom)

        df['count'] = n
        df['score'] = reward / n  # average score
        df['precision'] = prec
        df['rank'] = df['score'].argsort()

    return df

def format_all_csv():
    dir = 'summaries-raw/'

    for file in os.listdir(dir):
        df = format_csv(file, dir=dir)
        df.to_csv(f'summaries/{file}')

