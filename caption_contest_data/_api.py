import fsspec
import requests
from typing import Dict, Union, Set, List
import pandas as pd
from pathlib import Path
import sys
import json
from zipfile import ZipFile
from subprocess import call, DEVNULL
from functools import lru_cache


def _get_contests_web() -> Dict[str, str]:
    base = "https://api.github.com"
    url = base + "/repos/nextml/caption-contest-data/contents/contests/summaries"
    r = requests.get(url)
    data = r.json()
    if r.status_code == 403:
        raise requests.RequestException(data["message"])
    filenames = {
        datum["name"]: datum["download_url"]
        for datum in data
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


def all_contests(get=False) -> Set[Union[str, int]]:
    urls = _get_contests(get=get)
    contests = list(urls.values())
    fnames = [c.split("/")[-1] for c in contests]
    _ints = [c.split("_")[0] for c in fnames]
    ints = [int(c) if c.isnumeric() else c.split("-")[0] for c in _ints]
    ret = {x if ints.count(x) == 1 else x_str for x, x_str in zip(ints, fnames)}
    return ret


def summary(
    contest: Union[str, int], get: bool = True, path: Union[str, Path, None] = None
) -> pd.DataFrame:
    """
    Get the contest summary from a particular contest.

    Parameters
    ----------
    contest : str, int
        Which contest data to retrieve
    get : bool, optional
        Whether to get the contest names from the internet. If
        ``get is False``, the summaries are read from disk.
    path : str, optional
        Path of the

    Returns
    -------
    summary : pd.DataFrame
       A DataFrame with the results of the the contest. This dataframe has columns
       ``target_id``, ``rank``, ``funny``, ``somewhat_funny``, ``unfunny``,
       ``count``, ``score``, ``precision``, ``contest``, and ``caption``.

    Notes
    -----
    This summary has ratings for the funniness of each caption. Specifically,
    there's a 95% confidence that the mean score of the caption lies within
    ``score ± prec``.

    This function will cache all summaries on disk, and use the summary online
    if the cache does not exist.

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
    if not path:
        path = Path(__file__).parent / ".caption-contest-data"
    if isinstance(path, str):
        path = Path(path)
    if not get:
        fname = fnames[key].split("/")[-1]
        return pd.read_csv(path / fname)

    url = "filecache:" + ":".join(fnames[key].split(":")[1:])
    data = fsspec.open(url, cache_storage="/tmp/cache", target_protocol="https")
    with data as f:
        df = pd.read_csv(f)
    return df


def _get_response_fnames() -> Dict[str, str]:
    base = "https://api.github.com"
    url = base + "/repos/nextml/caption-contest-data/contents/contests/responses"
    r = requests.get(url)
    filenames = {
        datum["name"]: datum["download_url"]
        for datum in r.json()
        if datum["download_url"]
    }
    return filenames


def get_responses() -> bool:
    path = Path(__file__).parent / ".caption-contest-data"
    if path.exists():
        return True
    call(["git", "clone", "https://github.com/nextml/caption-contest-data", str(path)])
    return True


def _format_responses(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    for col in ["Unnamed: 0"]:
        if col in df:
            df.drop(columns=[col], inplace=True)
    if "target_reward" in df:
        df["target_reward"] = df["target_reward"].astype(int)
        labels = {1: "unfunny", 2: "somewhat_funny", 3: "funny"}
        df["label"] = df.target_reward.apply(labels.get)
    for k, v in kwargs.items():
        df[k] = v
    df["timestamp_query_generated"] = pd.to_datetime(df["timestamp_query_generated"])
    return df


def responses(
    contest: Union[int, str], path: Union[None, Path, str] = None
) -> pd.DataFrame:
    """
    Get the individual responses from a particular contest.

    Arguments
    ---------
    contest : int, str
        Which contest to download. A list of possible filenames is at
        https://github.com/nextml/caption-contest-data/tree/master/contests/responses.
        These can be the integer in the filename or the string. If not unique, it has to be the string.

    Returns
    -------
    responses : pd.DataFrame
        These responses are individual button clicks by humans. Some columns
        in the dataframe are
        ``network_delay``, ``response_time``, ``participant_uid``,
        ``timestamp_query_generated``, ``target``, ``target_id``, and
        ``target_reward``.

    Notes
    -----
    Using this function requires that all individual responses files are
    downloaded. In total, this is about 1.4 GB. The files are cached after the
    first download.

    """
    if not path:
        root = Path(__file__).parent / ".caption-contest-data"
        path = root / "contests" / "responses"
    if isinstance(path, str):
        path = Path(path)
    if not path.exists():
        msg = "path={} not found. Is it possible get_responses needs to be called?"
        raise ValueError(msg.format(responses))

    fnames = list(path.glob("*.csv.zip"))
    keys = [k for k in fnames if str(contest) in str(k)]
    if not keys:
        msg = (
            "contest={} is not valid. There are no responses with the given "
            "contest. Available filenames are at "
            "https://github.com/nextml/caption-contest-data/tree/master/contests/responses"
        )
        raise ValueError(msg.format(contest), fnames)
    if len(keys) > 1:
        msg = "contest={} yields multiple contests ({})."
        raise ValueError(msg.format(contest, keys))

    with ZipFile(str(keys[0])) as myzip:
        filelist = [f for f in myzip.filelist if "__MACOSX/" not in f.filename]
        assert len(filelist) == 1
        with myzip.open(filelist[0].filename) as f:
            df = pd.read_csv(f)
    c = contest if isinstance(contest, int) else contest.split("-")[0]
    return _format_responses(df, contest=c, filename=filelist[0].filename)


def meta(contest: Union[int, str], get:bool=True) -> Dict[str, Union[str, int]]:
    """
    Arguments
    ---------
    contest : int, str
        Argument to :func:`summary`

    Returns
    -------
    info : dict
        Dictionary with keys

        * ``comic``: A URL to the comi
        * ``num_responses``, ``num_captions``: an integer with the number of
          responses and captions respectively
        * ``funniest_caption``: the funniest caption, as rated by users.
        * ``example_query``: an example query. For certain contest
          (519, 550, 587 and 588) this key is not present.

    """
    c = contest if isinstance(contest, int) else int(contest.split("_")[0])
    df = summary(contest, get=get)
    base = "https://github.com/nextml/caption-contest-data/raw/master/contests/info"
    top = df["rank"].idxmin()

    d = {
        "comic": base + f"/{c}/{c}.jpg",
        "num_responses": df["count"].sum(),
        "num_captions": len(df["caption"]),
        "funniest_caption": df.loc[top, "caption"],
    }
    if c not in {519, 550, 587, 588}:
        d.update({"example_query": base + f"/{c}/example_query.png"})
    return d
