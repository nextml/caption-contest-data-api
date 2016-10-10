## Description
In this experiment, users were presented with a cartoon and asked to choose the
funniest caption when presented with two captions.

## Numerics
(as of 2015-12-09 4:22pm CST)

* **Number of responses:** 23,611
* **Number of participants:** (may not be unique partcipants) 1,163
* **Start date:** 2015-11-11 20:25

## Datasets provided
* **[participant-responses.csv]:** This includes all the responses collected.
  This data had been collected via two algorithms to choose which set of
  captions to present the user. Two algorithms (BR_lilUCB and BR_Thompson) are
  "adaptive" meaning they made decisions from data collected to determine.

[Lil_UCB algorithm]:http://arxiv.org/abs/1312.7308
[participant-responses_LilUCB.csv]:individual_algorithm_responses/participant-responses_LilUCB.csv
[participant-responses_RandomSampling.csv]:individual_algorithm_responses/participant-responses_RandomSampling.csv
[participant-responses.csv]:participant-responses.csv

## CSV headers
* **Partipipant ID:** The ID assigned to each participant. Note this is
  assigned when the page is visited; if the same user visits the page twice,
  they will get two participant IDs.
* **Response Time (s):** How long the participant took to respond to the
  question. Network delay is accounted for
* **Network delay (s):** How long the question took to load.
* **Timestamp:** When the query was generated (and not when the query was
  answered)
* **Rating:** What the user rated the caption as. This can be either 1, 2 or 3
  depending on if the joke was unfunny, somewhat funny or funny respectively.
* **Alg label:** The algorithm responsible for showing the query. The random
  sampling is unbiased while "Lil_UCB" adaptively chooses the funniest caption.
* **Target:** The caption the user is asked to rate.

### Example query
The cartoon shown is from cartoon contest #497.

![](query.png)

All possible captions are in captions.txt. From these captions, the algorithms
tried to find the funniest captions by user ratings.

