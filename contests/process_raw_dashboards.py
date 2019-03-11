import os

import scipy.stats
import pandas as pd
import numpy as np
import pytest


def button_clicks(mu_hat, prec, T):
    # Formulas for calculating quantities given raw statistics
    # mu_hat = sumX/float(T)
    # prec = np.sqrt( float( max(1.,sumX2 - T*mu_hat*mu_hat) ) / ( T - 1. ) / T )

    # We need at least 3 responses to recover 3 hidden variables
    if T in {0, 1, 2}:
        scores = {1: "unfunny", 2: "somewhat_funny", 3: "funny"}
        x = {k: 0 for k in scores.values()}
        if T == 0 or np.isnan(T):
            return x
        if T == 1:
            x[scores[int(mu_hat)]] = 1
        if T == 2:
            if np.ceil(mu_hat) == np.floor(mu_hat):
                x[scores[int(mu_hat)]] = 2
            else:
                x[scores[int(np.ceil(mu_hat))]] = 1
                x[scores[int(np.floor(mu_hat))]] = 1
        return x
    sumX = T * mu_hat
    sumX2 = prec ** 2 * T * (T - 1.) + T * mu_hat ** 2

    # Inverting out raw statistics
    # T = funny + somewhat + notfunny
    # sumX = 3*funny + 2*somewhat + 1*notfunny
    # sumX2 = 9*funny + 4*somewhat + 1*notfunny
    A = np.array([[1, 1, 1], [3, 2, 1], [9, 4, 1]], dtype=float)
    b = np.array([T, sumX, sumX2])
    x = np.linalg.solve(A, b)

    if x.min() < -0.5:
        x = [0, 0, T]
    x = [np.round(_) for _ in x]
    assert min(x) >= 0
    funny, somewhat, notfunny = x

    # Double check
    b_est = np.dot(A, x)
    T_est, sumX_est, sumX2_est = b_est

    mu_hat_est = sumX_est / float(T_est)
    prec_est = max(1.0, sumX2_est - T_est * mu_hat_est ** 2) / (T_est - 1.0)
    prec_est /= T_est
    prec_est = np.sqrt(prec_est)

    #  rel_error = lambda truth, est: np.abs(truth - est) / truth
    #  assert rel_error(mu_hat, mu_hat_est) < 1e-4
    #  assert rel_error(prec, prec_est) < 1e-4
    #  assert np.abs(T - T_est) < 0.5
    #  assert rel_error(sumX_est, sumX) < 1e-4
    return {
        "unfunny": int(notfunny),
        "somewhat_funny": int(somewhat),
        "funny": int(funny),
    }


def read_csv(fname):
    try:
        return pd.read_csv(fname)
    except pd.errors.ParserError:
        with open(fname) as f:
            lines = [line[:-1] for line in f.readlines()]
        header = lines[0].split(",")
        data = [line.split(",", maxsplit=3) for line in lines]
        data = [
            {
                label.lower().replace(" ", "_"): datum[i]
                for i, label in enumerate(header)
            }
            for datum in data[1:]
        ]
        data = [
            {
                key: float(value) if "funny" in key else value
                for key, value in datum.items()
            }
            for datum in data
        ]

        df = pd.DataFrame(data)
        return df


def score_and_prec(unfunny, somewhat_funny, funny, count):
    n = funny + somewhat_funny + unfunny
    reward = funny * 3 + somewhat_funny * 2 + unfunny
    score = reward / n
    reward_squared = funny * 9 + somewhat_funny * 4 + unfunny

    # computing the precision/standard deviation
    top = np.maximum(1, reward_squared - reward ** 2 / n)
    bottom = (n - 1) * n
    prec = np.sqrt(top / bottom)
    return score, prec


def format_cols(df):
    unnamed_cols = [c for c in df.columns if "Unnamed" in c]
    cols = [c for c in df.columns if c not in unnamed_cols]
    out = df[cols].copy()
    out.filename = df.filename
    cols = [c.lower() for c in out.columns]
    if any("somewhat funny" in c for c in cols):
        cols = [c.replace("somewhat funny", "somewhat_funny") for c in cols]
    out.columns = cols
    if "mean" in out:
        if "score" in out:
            out.drop("mean", axis=1, inplace=True)
        else:
            out.columns = [c.replace("mean", "score") for c in out.columns]
    assert "mean" not in out

    cols = [c if "count" not in c else "count" for c in out.columns]
    out.columns = cols
    for col in ["unfunny", "somewhat_funny", "funny"]:
        if col in out:
            out[col] = out[col].astype(int)
    return out


def get_clicks(datum):
    score = datum["score"]
    prec = datum["precision"]
    count = datum["count"]
    clicks = button_clicks(score, prec, count)
    return clicks


def recover_counts(df, name=""):
    scores = df.apply(get_clicks, axis=1)
    scores = pd.DataFrame(list(scores))

    out = pd.concat((df, scores), axis=1)
    out.filename = df.filename
    return out


def ranks(scores):
    return scipy.stats.rankdata(-scores, method="min").astype(int)


def process(filename):
    df = read_csv(filename)
    df.filename = filename.split("/")[-1]

    df = format_cols(df)
    contest = int(df.filename[:3])

    if "count" not in df:
        df["count"] = (df.funny + df.somewhat_funny + df.unfunny).astype(int)

    if "contest" not in df:
        df["contest"] = contest

    if all(key not in df for key in ["funny", "somewhat_funny", "unfunny"]):
        df = recover_counts(df)

    count = df.unfunny + df.somewhat_funny + df.funny
    df["count"] = count.astype(int)
    assert (count == df["count"]).all()
    score, prec = score_and_prec(df.unfunny, df.somewhat_funny, df.funny, df["count"])
    df["score"] = score
    df["precision"] = prec
    df["rank"] = ranks(df["score"])

    pred_score = df.funny * 3 + df.somewhat_funny * 2 + df.unfunny
    pred_score /= df["count"]
    diff = np.abs(pred_score - score)
    assert diff.max() < 1e-6

    df.sort_values(by="rank", inplace=True)
    cols = [
        "rank",
        "funny",
        "somewhat_funny",
        "unfunny",
        "count",
        "score",
        "precision",
        "contest",
        "caption",
    ]
    if "target_id" in df:
        cols = ["target_id"] + cols
    out = df[cols]
    filename = df.filename
    if "520" in filename or "521" in filename:
        out = out.dropna(subset=["score", "precision"])
    out["caption"] = out["caption"].fillna("")
    out.filename = filename
    return out


if __name__ == "__main__":
    import test_process_raw_dashboards as tst_prd

    DIR = "summaries/_raw-dashboards/"
    filenames = sorted([f for f in os.listdir(DIR) if f[0] not in {".", "_"}])
    dfs = {f: process(DIR + f) for f in filenames}

    for f, df in dfs.items():
        print(f)
        tst_prd.test_correct_order(df)
        tst_prd.test_score(df)
        tst_prd.test_counts(df)
        tst_prd.test_columns(df)
        tst_prd.test_ranks(df)
    for f, df in dfs.items():
        df.to_csv("summaries/" + f, index=False)