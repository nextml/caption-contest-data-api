
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

## Reading the data
We do provide a `example-analyses/utils.py` script which provides
`read_response` and `read_summary`. `read_response` can take in a ZIP filename
and unzip the result for you.

Otherwise, after downloading this repo (either via zip or with `git clone`),

1. `cd caption-contest-data/contests`
2. `python zip_tools.py unzip`. This assumes that the directory
   `responses-unzipped` exists.

## Backend system change
We switched from NEXT to a specialized system that more fully utilizes Amazon AWS for all contests after (and including) 587. Switching to this system means that

* the summaries are available
* there is no participants.json available
* histograms are not available

We switched because we wanted a specialized system that could run at scale at low cost.

## Tests
Test have been run to ensure that

* all CSVs have the same columns (in both the response files and summary files)
* for every zipped JSON file there is a unique response experiment UID

Tests are run with `py.test`

## Notes
* The number of responses/participants shown in `info.png` will not match the
    number of responses/participants generated from the response CSV data.
    * The number of responses shown are the responses generated, not the number
      of responses received.
    * The number of users shown are the number of users that have been shown
      query, not the number of users that have responded to a query
* `utils.calculate_stats` and the `{contest}_summary_{alg}.csv` will likely not
  have the same stats; some users may answer questions while I'm downloading.
* We have a bug in NEXT when calculating the `network_delay`. If a user takes
  longer than 24 hours to respond the network delay is negative. The victim
  line is `delta_datetime.seconds + delta_datetime.microseconds/1000000.` and
  is fixed by `delta_datetime.total_seconds()`. As of contest 560 this is still
  present.
