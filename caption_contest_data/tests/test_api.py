import pandas as pd
import pytest

import caption_contest_data as ccd

@pytest.mark.parametrize("contest", [532, 632, "560_summary_KLUCB_original"])
def test_df(contest):
    df = ccd.summary(contest)
    assert isinstance(df, pd.DataFrame)
