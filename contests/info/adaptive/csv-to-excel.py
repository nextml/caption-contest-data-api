import pandas as pd

def print_excel_for_contest(contest):
    summary_file = '{0}/{0}_summary_LilUCB.csv'.format(contest)

    csv = pd.read_csv(summary_file)
    csv.to_excel('{0}_summary.xlsx'.format(contest))


contests = ['531', '530', '529', '528']

for contest in contests:
    print_excel_for_contest(contest)

