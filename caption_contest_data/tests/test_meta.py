from pathlib import Path

import pytest
import requests

import caption_contest_data as ccd

root = Path(__file__).absolute().parent.parent.parent
exps = root / "contests" / "info"
contests_dual = [
    f"{p.name}_summary_{alg}.csv"
    for alg in ["LilUCB", "RoundRobin"]
    for p in (exps / "passive+adaptive").glob("*")
    if p.is_dir() and int(p.name) >= 508 and int(p.name) != 559
]
contests_dual.append(
    ["559_summary_KLUCB", "559_summary_LilUCB", "559_summary_RandomSampling"]
)
contests = [
    int(p.name)
    for alg in ["adaptive", "passive"]
    for p in (exps / alg).glob("*")
    if p.is_dir()
]
contests = sorted(contests)


@pytest.mark.parametrize("contest", contests_dual + contests)
def test_meta(contest):
    d = ccd.meta(contest, get=contest == contests_dual[0])
    r = requests.get(d["comic"])
    assert r.status_code == 200
