from __future__ import print_function
import csv
import os
import pandas as pd
import xlwt


for filename in os.listdir('summary-wo-email'):
    print(filename)
    if 'csv' not in filename or 'py' in filename:
        continue
    df = pd.read_csv('summary-wo-email/' + filename)
    df.to_excel('excels/' + filename.replace('csv', 'xls'))


for filename in os.listdir():
    print(filename)
    if 'csv' not in filename or 'py' in filename:
        continue
    df = pd.read_csv(filename)
    df.to_excel('excels/' + filename.replace('csv', 'xls'))


# def make_single_list(filename):
    # doc = xlwt.Workbook()
    # with open(filename) as f:
        # ratings = f.readlines()
        # ratings = [rating.strip('\n').split(',', maxsplit=3) for rating in ratings]
    # sheet = doc.add_sheet(filename)
    # for row, rating in enumerate(ratings):
        # for col, entry in enumerate(rating):
            # sheet.write(row, col, entry.strip('\\').strip(','))
    # filename = filename.strip('.csv') + '.xls'
    # return doc, filename


# def make_comphrensive_list():
    # doc = xlwt.Workbook()

    # for file in os.listdir('stats/'):
        # if '522' in file:
            # continue
        # with open('stats/' + file) as f:
            # ratings = f.readlines()
            # ratings = [rating.strip('\n').split(',', maxsplit=3) for rating in ratings]
        # sheet = doc.add_sheet(file_)

        # for row, rating in enumerate(ratings):
            # for col, entry in enumerate(rating):
                # sheet.write(row, col, entry.strip('\\').strip(','))

        # doc.save('all-contests-ratings.xls')



# doc, filename = make_single_list('525_summary_LilUCB.csv')
# doc.save(filename)
