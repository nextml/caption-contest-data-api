## Description
In this experiment, users were presented with a cartoon and asked to rate the
caption. They had a choice between "unfunny", "somewhat funny" and "funny".

Participants were notified by an email from an email from Robert Mankoff (from
the New Yorker). These participants received this email (or told others...)
because they were on a mailing list of Robert Mankoff's.

## Numerics
* **Number of responses:** 123,887
* **Number of participants:** (may not be unique participants) 377
* **Start date:** 2016-01-11 20:29 CST to 2016-01-13 16:30 CST
* **Number of captions**: 4828

## Datasets provided
* **[participant-responses.csv]:** This includes all the responses collected.
  This data had been collected via two algorithms which asked participants to
  rate comics as "unfunny","somewhat funny" or "funny". In these responses, we
  did not limit the number of responses: people could answer questions as long
  as they desired.
* **[participant-responses_LilUCB.csv]:**  The response data that the algorithm
  [Lil_UCB] generated the query for. This algorithm is adaptive and makes
  choices based on previous received answers).
* **[particpant-responses_RoundRobin.csv]:** The other algorithm
  (RoundRobin) makes no choices based on previous answers about which query to
  present. It does this
* **[participant.json]:** This is the complete response data.
  `participant_responses.csv` was generated from this data.

[Lil_UCB]:http://arxiv.org/abs/1312.7308
[participant-responses.csv]:participant_responses.csv
[participant-responses_LilUCB.csv]:individiaul_algorithm_responses/participant_responses_LilUCB.csv
[particpant-responses_RoundRobin.csv]:individiaul_algorithm_responses/participant_responses_RoundRobin.csv
[participant.json]:participant.json

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
* **Alg label:** The algorithm responsible for showing the query. The
  RoundRobin sampling is unbiased while "Lil_UCB" adaptively chooses the
  funniest caption.
* **Target:** The caption the user is asked to rate.

### Example query
![](query.png)

All possible captions are in captions.txt. From these captions, the algorithms
tried to find the funniest captions by user ratings. These algorithms are
ranked from the funniest algorithm to the least funny algorithm, as determined
by some algorithm (further details may be requested).
