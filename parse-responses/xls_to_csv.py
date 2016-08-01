import sys
import pandas as pd

doc = sys.argv[1]
out = sys.argv[2]

df = pd.read_excel(doc)
df['CaptionText'].to_csv(out)
