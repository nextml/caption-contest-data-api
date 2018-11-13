import os

import numpy as np
import pandas as pd
import scipy.stats


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


def get_counts(datum):
    try:
        count = datum["count"]
    except KeyError:
        count = datum["funny"] + datum["unfunny"] + datum["somewhat funny"]
    clicks = button_clicks(datum["score"], datum["precision"], count)
    return clicks


def recover_counts(df, name=""):
    scores = df.apply(get_counts, axis=1)
    scores = pd.DataFrame(list(scores))
    if "somewhat funny" in df.columns:
        df["somewhat_funny"] = df["somewhat funny"]
    new_df = df.copy()
    assert set(scores.columns) == {"funny", "somewhat_funny", "unfunny"}
    if "roundrobin" not in name.lower():
        if all(x in df.columns for x in ["funny", "somewhat_funny", "unfunny"]):
            old_scores = df[["funny", "somewhat_funny", "unfunny"]]
            #  assert np.allclose(scores, old_scores)
        new_df["funny"] = scores["funny"]
        new_df["somewhat_funny"] = scores["somewhat_funny"]
        new_df["unfunny"] = scores["unfunny"]
    if "counts" not in new_df.columns:
        new_df["counts"] = (
            new_df["funny"] + new_df["somewhat_funny"] + new_df["unfunny"]
        )
    return new_df


def _assert_cols_same(df1, df2):
    assert set(df1.columns) == set(df2.columns)
    for col in df1.columns:
        if df1[col].dtype == object:
            assert list(df1[col]) == list(df2[col])
        else:
            i = (df1[col].isnull()) | (df2[col].isnull())
            assert np.allclose(df1[col][~i], df2[col][~i])
            assert i.sum() / len(i) < 0.01


if __name__ == "__main__":
    old_dfs = {
        filename: pd.read_csv("./summaries/" + filename)
        for filename in os.listdir("summaries/")
        if "csv" in filename
        and all(x not in filename.lower() for x in ["munging", ".DS"])
        and filename[0] != "_"
    }
    old_dfs = {k: df for k, df in old_dfs.items() if "funny" not in df.columns}
    new_dfs = {
        filename: recover_counts(df, name=filename) for filename, df in old_dfs.items()
    }

    for filename, new_df in new_dfs.items():
        if "rank" not in new_df.columns:
            new_df["rank"] = scipy.stats.rankdata(
                -new_df["score"], method="min"
            ).astype(int)
        if "contest" not in new_df.columns:
            new_df["contest"] = filename.split("_")[0]
        new_df.to_csv("summaries/_fill-in-button-click-backup/" + filename)
