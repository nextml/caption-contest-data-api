import numpy as np
import pandas as pd


def button_clicks(mu_hat, prec, T):
    # Formulas for calculating quantities given raw statistics
    # mu_hat = sumX/float(T)
    # prec = np.sqrt( float( max(1.,sumX2 - T*mu_hat*mu_hat) ) / ( T - 1. ) / T )
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
    assert np.allclose(mu_hat_est, mu_hat)
    assert np.allclose(prec_est, prec)
    assert np.allclose(T, T_est)
    assert np.allclose(sumX_est, sumX)
    # Commented out for edge case when caption receives nothing but "unfunnies"
    #  assert np.allclose(sumX2_est, sumX2)
    return {
        "unfunny": int(notfunny),
        "somewhat_funny": int(somewhat),
        "funny": int(funny),
    }


def get_counts(datum):
    clicks = button_clicks(datum["score"], datum["precision"], datum["count"])
    if "funny" in datum.keys():
        assert clicks["funny"] == datum["funny"]
        assert clicks["somewhat_funny"] == datum["somewhat_funny"]
        assert clicks["unfunny"] == datum["unfunny"]
    return clicks


if __name__ == "__main__":
    df = pd.read_csv("./summaries/596_summary_KLUCB.csv")
    df = pd.read_csv("./summaries/526_summary_LilUCB.csv")

    scores = df.apply(get_counts, axis=1)

    failed = [s is None for s in scores]
    failed = sum(failed)
    print(f"Failed at {failed} locations, {100*failed/len(scores)}%")
