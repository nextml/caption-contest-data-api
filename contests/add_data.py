import numpy as np
import pandas as pd
import os


def button_clicks(mu_hat, prec, T):
    # Formulas for calculating quantities given raw statistics
    # mu_hat = sumX/float(T)
    # prec = np.sqrt( float( max(1.,sumX2 - T*mu_hat*mu_hat) ) / ( T - 1. ) / T )

    # We need at least 3 responses to recover 3 hidden variables
    if T in {0, 1, 2}:
        scores = {1: "unfunny", 2: "somewhat_funny", 3: "funny"}
        x = {k: 0 for k in scores.values()}
        if T == 0:
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

    rel_error = lambda truth, est: np.abs(truth - est) / truth
    assert rel_error(mu_hat, mu_hat_est) < 1e-4
    assert rel_error(prec, prec_est) < 1e-4
    assert np.abs(T - T_est) < 0.5
    assert rel_error(sumX_est, sumX) < 1e-4
    # Commented out for edge case when caption receives nothing but "unfunnies"
    #  assert np.allclose(sumX2_est, sumX2)
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


def get_counts_recovers(df):
    scores = df.apply(get_counts, axis=1)
    scores = pd.DataFrame(list(scores))
    if "somewhat funny" in df.columns:
        df["somewhat_funny"] = df["somewhat funny"]
    assert np.all(scores == df[["funny", "somewhat_funny", "unfunny"]])
    return True


def _write_click_present_txt(dir="summaries/"):
    filenames = [x for x in os.listdir(dir) if "munging" not in x and ".DS" not in x]
    dfs = {filename: pd.read_csv(dir + filename) for filename in filenames}
    dfs = {filename: df for filename, df in dfs.items() if "funny" in df.columns}
    filenames = list(dfs.keys())
    with open("./clicks_present.txt", "w") as f:
        print("\n".join(filenames), file=f)


if __name__ == "__main__":
    df = pd.read_csv("./summaries/596_summary_KLUCB.csv")
    df = pd.read_csv("./summaries/526_summary_LilUCB.csv")

    #  _write_click_present_txt()

    dir = "summaries/"
    with open("./clicks_present.txt", "r") as f:
        filenames = [x for x in f.read().split("\n") if len(x) > 0]
    dfs = {filename: pd.read_csv(dir + filename) for filename in filenames}
    assert all("funny" in df.columns for df in dfs.values())
    for k, (filename, df) in enumerate(dfs.items()):
        if "roundrobin" in filename.lower():
            continue
        get_counts_recovers(df)
