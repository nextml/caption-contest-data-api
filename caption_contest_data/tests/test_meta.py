from pathlib import Path

import pytest
import requests

import caption_contest_data as ccd

root = Path(__file__).absolute().parent.parent.parent
exps = root / "contests" / "info"

contests_dual = [
    f"{p.name}_summary_{alg}.csv"
    for alg in ["LilUCB", "RoundRobin"]
    for p in (exps).glob("*")
    if p.is_dir() and 508 <= int(p.name) <= 519
] + ["559_summary_KLUCB", "559_summary_LilUCB", "559_summary_RandomSampling"]

contests_single = [
    int(p.name)
    for p in (exps).glob("*")
    if p.is_dir() if int(p.name) >= 520 and int(p.name) != 559
]
contests = contests_dual + sorted(contests_single)
print(contests)


@pytest.mark.parametrize("contest", contests)
def test_meta(contest):
    d = ccd.meta(contest)
    r = requests.get(d["comic"])
    assert r.status_code == 200
