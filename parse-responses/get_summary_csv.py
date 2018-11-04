import requests
import sys
import pandas as pd

if len(sys.argv) < 3:
    raise ValueError("Usage: get_summary_csv.py [exp_uid] [contest]")

exp_uid = sys.argv[1]
contest = sys.argv[2]

url = "https://s3-us-west-2.amazonaws.com/next2newyorker/"

html = requests.get(url + exp_uid)
ranks = requests.get(url + exp_uid + "/ranks.json").json()
targets = requests.get(url + exp_uid + "/targets.json").json()
votes = requests.get(url + exp_uid + "/votes.json").json()

captions = [
    {"target_id": r[0], "score": r[1], "precision": r[2], "count": r[3], "rank": k + 1}
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
    assert cap["funny"] + cap["unfunny"] + cap["somewhat_funny"] == cap["count"]
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

df.to_csv(f"{contest}_summary_private.csv")
del df["exp_uid"]
df.to_csv(f"{contest}_summary_KLUCB.csv")

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
