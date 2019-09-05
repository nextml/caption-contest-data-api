
## How did you obtain data from The New Yorker?
We currently run The New Yorker's Caption Contest. Their caption contest page says

> Help us pick three finalists from last week’s contest by rating submissions. [Vote now »][1]

where "Vote now »" points to http://nextml.org/captioncontest

[1]:http://nextml.org/captioncontest

## What are the algorithm differences?

The different algorithms choose which caption to display. The biggest
difference between algorithms is "adaptive" vs "passive":

* passive: these algorithms don't use any history or prior responses to choose
  which caption to display.
* adaptive: these algorirthm choose which caption to display based on
  historyr/prior responses. They are designed with the goal of finding the
  funniest caption (meaning they have accurate estimates of the scores for
  funnier captions).

Adaptive algorithms include "LilUCB" and "KL-UCB". Passive algorithms include
"RandomSampling" and "RoundRobin".

## What questions do you ask?

* How funny is this caption? (all contest)
* Which of these two captions is funnier? (contest 508 and 509)
* How original is this caption? (contest 560)

## Columns in summary CSVs?

* `caption`: The text that was displayed to the participant
* `funny`, `somewhat_funny` and `unfunny`: The number of users that clicked that button
* `score`: That caption's score. Calculated with `1*unfunny + 2*somewhat_funny + 3*funny`
* `rank`: That caption's rank. Captions with the same score have the same rank
* `count`: The total number of times that caption has been rated by participants
* `contest`: What's the contest where this caption has been displayed? The contest number increases by one every week
* `precision`: The 95% confidence interval that the "true" score of that caption falls in `score - precision` and `score + precision`
