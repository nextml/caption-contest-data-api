import fsspec
import requests
from typing import Dict, Union
import pandas as pd
from pathlib import Path
import sys
import json


def _get_contests_web() -> Dict[str, str]:
    base = "https://raw.githubusercontent.com/nextml/caption-contest-data/master/contests/summaries/"
    base = "https://api.github.com"
    url = base + "/repos/nextml/caption-contest-data/contents/contests/summaries"
    r = requests.get(url)
    filenames = {
        datum["name"]: datum["download_url"]
        for datum in r.json()
        if datum["download_url"]
    }
    return filenames


def _get_contests(get=True) -> Dict[str, str]:
    p = Path(__file__).parent / ".contests.csv"
    if get:
        fnames = _get_contests_web()
    else:
        with open(str(p), "r") as f:
            fnames = json.load(f)
    with open(str(p), "w") as f:
        json.dump(fnames, f)
    return fnames


def summary(contest: Union[str, int], get: bool = True) -> pd.DataFrame:
    """
    Parameters
    ----------
    contest : str, int
        Which contest data to retrieve
    get : bool, optional
        Whether to make a request to refresh the contests available.

    Returns
    -------
    data : pd.DataFrame
        A DataFrame with the results of the the contest. This dataframe has columns
        ``target_id``, ``rank``, ``funny``, ``somewhat_funny``, ``unfunny``,
        ``count``, ``score``, ``precision``, ``contest``, and ``caption``.

    """
    try:
        fnames = _get_contests(get=get)
    except requests.ConnectionError:
        fnames = _get_contests(get=False)

    keys = [k for k in fnames.keys() if str(contest) in k]
    if not len(keys):
        msg = "contest={} is not valid. Valid choices that contain contest are {}"
        raise ValueError(msg.format(contest, keys))
    if len(keys) > 1:
        msg = (
            "Correct values for `contest` are {}, got {}. "
            "To resolve this issue, pass in one of the correct values"
        )
        raise ValueError(msg.format(keys, contest))

    key = keys[0]
    data = fsspec.open(fnames[key])
    with data as f:
        df = pd.read_csv(f)
    return df
