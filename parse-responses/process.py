from pathlib import Path
import sys
from pprint import pprint

sys.path.append("..")
import caption_contest_data
from caption_contest_data.tests import test_process_raw_dashboards as tst_prd
from caption_contest_data._raw import process


if __name__ == "__main__":
    root = Path(__file__).absolute().parent.parent
    raw = root / "contests" / "summaries" / "_raw-dashboards"

    filenames = sorted([str(f) for f in raw.glob("*.csv")])
    contest = filenames[-1]

    print(contest)
    df = process(contest)
    print("Sample captions:")
    pprint(list(df.caption.head()))
    print("\n")
    print("num answers: {}k".format(df["count"].sum() // 1000))
    print("num captions: ", len(df.caption.unique()))
    print("\nInput file: " + contest)
    ans = input("Correct contest? y/n\n")
    if ans.lower() == "n":
        raise Exception()

    tst_prd.test_correct_order(df)
    tst_prd.test_score(df)
    tst_prd.test_counts(df)
    tst_prd.test_columns(df)
    tst_prd.test_ranks(df)

    out_file = root / "contests" / "summaries" / contest.split("/")[-1]
    print(f"Writing to {out_file}")
    df.to_csv(out_file, index=False)
