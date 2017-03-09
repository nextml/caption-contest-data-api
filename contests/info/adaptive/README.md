These experiments only have an adaptive algorithm choosing queries. This means
that it makes a choice to show which captions to show based on previous
captions.

These contests don't have any comparison to the random approach-- we don't know
how much better the adaptive approach is.

This data is not suitable for any scientific process that relies on independence
of each trial -- participant 1 can influence what participant 1000 sees.

The adaptive algorithm used, LilUCB, is designed to select the "best" element
from a collection of items (in this case the funniest caption from all
captions). This means that there are no guarantees about ranking -- the 100th
highest ranked caption may not be the 100th funniest caption.

More detail on this algorithm can be found at "[lil’ UCB : An Optimal
Exploration Algorithm for Multi-Armed Bandits"][1]" by [Kevin Jamieson], [Matt
Malloy], [Robert Nowak] and [Sébastien Bubeck].

[Kevin Jamieson]:http://people.eecs.berkeley.edu/~kjamieson/about.html
[Matt Malloy]:https://sites.google.com/site/mmalloy/
[Robert Nowak]:http://nowak.ece.wisc.edu
[Sébastien Bubeck]:http://research.microsoft.com/en-us/um/people/sebubeck/

[1]:http://people.eecs.berkeley.edu/~kjamieson/resources/jamieson14_LilUCB.pdf
