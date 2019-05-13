import requests
import sys
import pandas as pd
import os
from selenium import webdriver
from subprocess import call
from time import sleep


def get_summary(exp_uid, contest):
    url = "https://s3-us-west-2.amazonaws.com/mlnow-newyorker/"

    ranks = requests.get(url + exp_uid + "/ranks.json").json()
    targets = requests.get(url + exp_uid + "/targets.json").json()
    votes = requests.get(url + exp_uid + "/votes.json").json()

    captions = [
        {
            "target_id": r[0],
            "score": r[1],
            "precision": r[2],
            "count": r[3],
            "rank": k + 1,
        }
        for k, r in enumerate(ranks)
    ]

    descriptions = {t["target_id"]: t["primary_description"] for t in targets}

    for cap in captions:
        key = str(cap["target_id"])
        cap["caption"] = descriptions[key]
        cap["funny"] = votes[key]["funny"]
        cap["unfunny"] = votes[key]["not"]
        cap["somewhat_funny"] = votes[key]["somewhat"]

    assert all(a["score"] >= b["score"] for a, b in zip(captions, captions[1:]))
    for cap in captions:
        assert (
            abs(cap["funny"] + cap["unfunny"] + cap["somewhat_funny"] - cap["count"])
            < 4
        )
        assert set(cap.keys()) == {
            "target_id",
            "score",
            "precision",
            "count",
            "rank",
            "caption",
            "funny",
            "unfunny",
            "somewhat_funny",
        }

    df = pd.DataFrame(captions)
    df["contest"] = contest
    df["exp_uid"] = exp_uid

    df.to_csv(f"{contest}_summary_private.csv", index=False)
    del df["exp_uid"]
    df.to_csv(f"{contest}_summary_KLUCB.csv", index=False)

    caption_counts = df["caption"].value_counts()
    repeat_captions = caption_counts[caption_counts > 1]
    files = {
        f"{contest}": df["caption"].values.astype("str"),
        f"{contest}_repeat": list(repeat_captions.index),
    }

    for prefix, captions in files.items():
        with open("{}_captions.csv".format(prefix), "w") as f:
            captions = "\n".join(captions)
            print(captions, file=f)
    files = os.listdir(".")
    assert f"{contest}_summary_KLUCB.csv" in files
    assert f"{contest}_summary_private.csv" in files
    assert f"{contest}_captions.csv" in files
    assert f"{contest}_repeat_captions.csv" in files
    return True


def write_screenshot():
    driver = webdriver.Firefox()
    driver.get("http://www.nextml.org/captioncontest")
    sleep(5)
    driver.save_screenshot("example_query.png")
    driver.quit()
    return True


def move(file, dir, check=True):
    if check and file in os.listdir(dir):
        raise ValueError(f"file {file} is already in {dir}")
    call(["mv", file, dir])
    return True


if __name__ == "__main__":
    base = "https://s3-us-west-2.amazonaws.com/mlnow-newyorker"
    r = requests.get(base + "/current_contest.json")
    meta = r.json()
    #  contest = meta["contest_number"] + 2  # github issue #16
    DIR = "../contests/info/adaptive/"
    contests = [int(x) for x in os.listdir(DIR) if os.path.isdir(DIR + x)]
    contest = max(contests) + 1
    exp_uid = meta["exp_uid"]

    ## Write data files to local dir
    get_summary(exp_uid, contest)

    call(f"wget {base}/{exp_uid}/cartoon.jpg -O {contest}.jpg".split(" "))
    write_screenshot()

    ## Create new folder
    contests = os.listdir("../contests/info/adaptive/")
    if str(contest) in contests:
        raise ValueError(
            f"contest {contest} is already in ../contests/summaries/info/adaptive"
        )
    summary_dir = f"../contests/info/adaptive/{contest}"
    call(f"mkdir {summary_dir}".split())

    ## Move data files
    check = True
    move(
        f"{contest}_summary_KLUCB.csv",
        "../contests/summaries/_raw-dashboards/",
        check=check,
    )
    move(f"{contest}_summary_private.csv", "_private/", check=check)
    move(f"{contest}_captions.csv", summary_dir, check=check)
    move(f"{contest}_repeat_captions.csv", summary_dir, check=check)
    move(f"example_query.png", summary_dir, check=check)
    move(f"{contest}.jpg", summary_dir, check=check)

    README = """
Cardinal bandits (aka "how funny is this caption?")

Example query:

![](example_query.png)
"""
    with open(f"{summary_dir}/README.md", "w") as f:
        print(README, file=f)

    ## Process raw dashboards
    ## Call pytest
