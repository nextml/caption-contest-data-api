
## Directory structure
* `info`: The info on all the contests.
    * This contains subdirectories {passive, adaptive+passive, adaptive} which
      notes the type of algorithm(s) run.
    * In each folder it's possible to see the comic, an example query, the
        histogram of response times and the basic info (number of participants
        and number of responses)
* `responses`: The response data. One response is recorded every click a button
  clicked on the New Yorker site
* `summaries`: The final summary of each contest. How funny was each caption
  and how many votes did it receive for unfunny, somewhat funny and funny?

## Unzipping the data
After downloading this repo (either via zip or with `git clone`),

1. `cd caption-contest-data/contests`
2. `python zip_tools.py unzip`. This assumes that the directory
   `responses-unzipped` exists.

## Tests
Test have been run to ensure that

* all CSVs have the same columns (in both the response files and summary files)
* for every zipped JSON file there is a unique response experiment UID
