from pathlib import Path
from time import time

import pandas as pd
import pytest

import caption_contest_data as ccd


@pytest.mark.parametrize("contest", ccd.summary_ids())
def test_all_summaries(contest):
    start = time()
    df = ccd.summary(contest)
    print("{:0.1f}ms".format(1000 * (time() - start)))
    assert isinstance(df, pd.DataFrame)
