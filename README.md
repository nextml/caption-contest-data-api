This repository will contain data gathered on the [NEXT] active machine
learning system. NEXT can *adaptively* sample a set of captions to determine
the funniest caption or determine how similar objects are.

The NEXT system also collects *random* samples instead of adaptive samples. We
can think of these samples as being "unbiased" -- they make no decisions
about which queries to display.

The data is in the form of individual responses to queries. The dataset
consists of individual responses to questions (like the ones shown below in
[example queries](#example-queries)).

## Datasets
* [New Yorker dataset](new_yorker). This dataset is part of the "cartoon
  caption contest" where given a cartoon users are supposed to write a funny
  caption. Our algorithms help determine the funniest algorithms (and we also
  provide *unbiased* data; see each folder for detail).
    * [497]: Roughly 23k responses.
    * [499]: 103,306 responses, 4,851 participants. This
      dataset was collected through the [New Yorker Caption Contest] through
      a video/blog post titled [Cartoon Lounge: Show Me the Funny].

We have also asked more datasets that contain anywhere from 15-25k responses.
We plan to put these online in the near future.

More detail is given in each folder. Each folder's name corresponds to
which caption contest it appeared in.

[499]:499/
[497]:497/
[New Yorker Caption Contest]:http://contest.newyorker.com
[Cartoon Lounge: Show Me the Funny]:http://www.newyorker.com/cartoons/bob-mankoff/cartoon-lounge-show-me-the-funny

## Example queries
An example query:

![](new_yorker/497/query.png)

The user is given a URL and after visiting the URL, the user is presented with
a series of queries similar to the one above. There may be variations on the
query, described in detail on each experiment.

For example, in the Lewis queries we see queries similar to this:

![](lewis/lewis_query.png)


[NEXT]:http://nextml.org/
