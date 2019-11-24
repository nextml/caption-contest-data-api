import shutil
from pathlib import Path
from subprocess import call
from typing import Dict

import requests

from caption_contest_data import _api


def _get_summary_fnames_web() -> Dict[str, str]:
    base = "https://api.github.com"
    url = base + "/repos/nextml/caption-contest-data/contents/contests/summaries"
    r = requests.get(url)
    data = r.json()
    if r.status_code == 403:
        raise requests.RequestException(data["message"])
    return {
        datum["name"]: datum["download_url"] for datum in data if datum["download_url"]
    }


def _get_response_fnames_web() -> Dict[str, str]:
    base = "https://api.github.com"
    url = base + "/repos/nextml/caption-contest-data/contents/contests/responses"
    r = requests.get(url)
    data = r.json()
    if r.status_code == 403:
        raise requests.RequestException(data["message"])
    return {
        datum["name"]: datum["download_url"] for datum in data if datum["download_url"]
    }


def _get_local_file_path(url: str, cache: Path) -> str:
    """ from https://github.com/intake/filesystem_spec/issues/167#issuecomment-548538263 """
    fname = url.split("/")[-1]
    local = cache / fname
    cached_files = [x.name for x in cache.glob("*")]
    if fname in cached_files:
        return str(local)
    r = requests.get(url)
    with open(str(local), "w") as f:
        print(r.text, file=f)
    return str(local)


def get_responses() -> bool:
    """
    Get all responses, about 290MB in total.

    Returns
    -------
    success : bool
        Wheter the responses files are present.

    Notes
    -----
    This function has the side effect of downloading all summaries too. They
    are cached after this function is called.

    This function requires that Git be installed.

    """
    _cache = _api._get_cache()
    if (_cache / "responses").exists():
        return True
    call(["git", "clone", "https://github.com/nextml/caption-contest-data.git"], cwd=str(_cache))

    repo = _cache / "caption-contest-data"
    (repo / "contests" / "responses").rename(_cache / "responses")
    (repo / "contests" / "summaries").rename(_cache / "summaries")
    shutil.rmtree(str(repo))
    return True
