from pathlib import Path

import pytest
import requests

import caption_contest_data as ccd

root = Path(__file__).absolute().parent.parent.parent
exps = root / "contests" / "info"


@pytest.mark.parametrize("path", [str(x) for x in exps.glob("*") if x.is_dir()])
def test_dir(path):
    p = Path(path)
    files = [x.name for x in p.glob("*") if x.is_file()]
    if any(k in path for k in ["519", "550", "587", "588"]):
        pytest.xfail(reason="Mistake collecting responses")
    assert "example_query.png" in files
    assert "README.md" in files
    assert f"{p.name}.jpg" in files


@pytest.mark.parametrize(
    "contest", ["519_summary_RoundRobin.csv", 550, 587, 588, 532, 600, 661, 662]
)
def test_meta_request(contest):
    d = ccd.metadata(contest)
    c = contest if isinstance(contest, int) else int(contest.split("_")[0])
    base = "https://github.com/nextml/caption-contest-data/raw/master/contests/info"
    assert {
        "comic",
        "num_responses",
        "num_captions",
        "funniest_caption",
    }.issubset(set(d.keys()))
    if c not in {519, 550, 587, 588}:
        assert "example_query" in d.keys()
    assert d["comic"] == base + f"/{c}/{c}.jpg"
    r = requests.get(d["comic"])
    assert r.status_code == 200
