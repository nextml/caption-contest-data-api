import pandas as pd
import pytest
from pathlib import Path

import caption_contest_data as ccd

@pytest.mark.parametrize("contest", [532, 632, "560_summary_KLUCB_original"])
def test_df(contest):
    df = ccd.summary(contest)
    assert isinstance(df, pd.DataFrame)

def test_all_contests():
    contests = ccd.all_contests(get=False)
    summaries = Path(__file__).absolute().parent.parent / "contests" / "summaries"
    for c in contests:
        df = ccd.summary(c, path=summaries)
        assert isinstance(df, pd.DataFrame)
