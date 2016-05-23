from __future__ import print_function
import csv
import os
import pandas as pd

# dir = 'stats/'
# for csvfile in os.listdir(dir):
    # with open(dir + csvfile, 'r') as file_:
        # file_ = csv.reader(dir + csvfile)
        # tab = csv.excel(file_)

import xlwt

doc = xlwt.Workbook()

for file_ in os.listdir('stats/'):
    if '522' in file_:
        continue
    with open('stats/' + file_) as f:
        ratings = f.readlines()
        ratings = [rating.strip('\n').split(',', maxsplit=3) for rating in ratings]
    sheet = doc.add_sheet(file_)

    for row, rating in enumerate(ratings):
        for col, entry in enumerate(rating):
            sheet.write(row, col, entry.strip('\\').strip(','))

    doc.save('all-contests-ratings.xls')
