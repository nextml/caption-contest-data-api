import json
import os
import sys
import zipfile
from functools import lru_cache
from pathlib import Path
from subprocess import DEVNULL, call
from typing import Dict, List, Set, Union

import pandas as pd
import requests

from caption_contest_data import _web

_root = Path(__file__).absolute().parent


def _get_cache():
    _cache = _root / ".ccd-cache"
    if not _cache.exists():
        _cache.mkdir()
    if not (_cache / "summaries").exists():
        (_cache / "summaries").mkdir()
    return _cache


@lru_cache()
def _get_response_fnames(cache=True) -> Dict[str, str]:
    """
    Returns {filename: download_url}
    """
    _cache = _get_cache()
    p = _cache / "responses.json"
    if not p.exists():
        fnames = _web._get_response_fnames_web()
        with open(str(p), "w") as f:
            json.dump(fnames, f)
    else:
        with open(str(p), "r") as f:
            fnames = json.load(f)
    return fnames


@lru_cache()
def _get_summary_fnames(cache=True) -> Dict[str, str]:
    """
    Returns {filename: download_url}
    """
    _cache = _get_cache()
    p = _cache / "summaries.json"
    if not p.exists():
        fnames = _web._get_summary_fnames_web()
        with open(str(p), "w") as f:
            json.dump(fnames, f)
    else:
        with open(str(p), "r") as f:
            fnames = json.load(f)
    return fnames


def refresh():
    """
    Refresh the list of available summary filenames.
    This function is useful if new contests summaries are desired.

    """
    _cache = _get_cache()
    if (_cache / "summaries.json").exists():
        os.remove(str(_cache / "summaries.json"))
    if (_cache / "responses.json").exists():
        os.remove(str(_cache / "responses.json"))
    _get_summary_fnames(cache=False)
    _get_response_fnames(cache=False)
    return True


def summary_ids() -> Set[Union[str, int]]:
    """
    Get the contest IDs.

    Returns
    -------
    IDs : Set[Union[str, int]]
        A list of IDs are accepted by :py:func:`summary`.
    """
    urls = _get_summary_fnames()
    contests = list(urls.values())
    fnames = [c.split("/")[-1] for c in contests]
    _ints = [c.split("_")[0] for c in fnames]
    ints: List[Union[str, int]] = [
        int(c) if c.isnumeric() else c.split("-")[0] for c in _ints
    ]
    ret = {x if ints.count(x) == 1 else x_str for x, x_str in zip(ints, fnames)}
    return ret


def summary(contest: Union[str, int]) -> pd.DataFrame:
    """
    Get the contest summary from a particular contest.

    Parameters
    ----------
    contest : str, int
        Which contest data to retrieve. This can be an element of
        :py:func:`summary_ids`.

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
    fnames = _get_summary_fnames()

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
    url = fnames[key]
    _cache = _get_cache()
    local_fname = _web._get_local_file_path(fnames[key], cache=_cache / "summaries")
    return pd.read_csv(local_fname)


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


def responses(contest: Union[int, str]) -> pd.DataFrame:
    """
    Get the individual responses from a particular contest.

    Parameters
    ----------
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
    downloaded through :py:func:`get_responses`.

    """
    _cache = _get_cache()
    if not (_cache / "responses").exists():
        raise ValueError(
            "The responses need to be download first through the function `get_responses`"
        )
    fnames = list((_cache / "responses").glob("*.csv.zip"))
    keys = [k for k in fnames if str(contest) in str(k)]
    if not keys:
        msg = (
            "contest={} is not valid. There are no responses with the given "
            "contest. Available filenames are {}"
        )
        raise ValueError(msg.format(contest), fnames)
    if len(keys) > 1:
        msg = "contest={} yields multiple contests ({})."
        raise ValueError(msg.format(contest, keys))

    with zipfile.ZipFile(str(keys[0])) as myzip:
        filelist = [f for f in myzip.filelist if "__MACOSX/" not in f.filename]
        assert len(filelist) == 1
        with myzip.open(filelist[0].filename) as f:
            df = pd.read_csv(f)
    c = contest if isinstance(contest, int) else contest.split("-")[0]
    return _format_responses(df, contest=c, filename=filelist[0].filename)


def metadata(contest: Union[int, str]) -> Dict[str, Union[str, int]]:
    """
    Parameters
    ----------
    contest : int, str
        Argument to :py:func:`summary`. See :py:func:`summary_ids`.

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
    df = summary(contest)
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
