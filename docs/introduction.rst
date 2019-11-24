Getting started
===============
Installation
------------

This package will be on PyPI.

.. code-block:: bash

   pip install caption-contest-data-api

This will download the scripts only, **not any data.** The, the API can be
imported into Python:

.. code-block:: python

   import caption_contest_data as ccd
   df = ccd.summary(630)

Brief demo
----------

Let's read in the data from contest 553:

.. code-block:: python

   >>> import caption_contest_data as ccd
   >>> df = ccd.summary(553)
   >>> df.head()
      rank  funny  ...  contest                                            caption
   0     1     87  ...      553                      I'd like to see other people.
   1     2     74  ...      553  I know that look, you're not going to let this...
   2     3     63  ...      553                      I'd like to see other people.
   3     4     54  ...      553  What a delightful coincidence. I'm also recent...
   4     5     61  ...      553              Maybe his second week will go better.

   [5 rows x 9 columns]

Let's look at the funniest caption:

.. code-block:: python

   >>> df.iloc[0]
   rank                                          1
   funny                                        87
   somewhat_funny                               84
   unfunny                                     157
   count                                       328
   score                                   1.78659
   precision                             0.0462131
   contest                                     553
   caption           I'd like to see other people.
   Name: 0, dtype: object

What are the funniest captions?

.. code-block:: python

   >>> pprint(df.caption[:5].tolist())
   ["I'd like to see other people.",
    "I know that look, you're not going to let this go.",
    "I'd like to see other people.",
    "What a delightful coincidence. I'm also recently single.",
    'Maybe his second week will go better.']

These are all captions for this comic:

.. raw:: html

   <img src="https://github.com/nextml/caption-contest-data/raw/master/contests/info/553/553.jpg" width="400px" />

This URL is available through the ``meta`` function:

.. code-block:: python

    >>> ccd.metadata(553)
    {'comic': 'https://github.com/nextml/caption-contest-data/raw/master/contests/info/553/553.jpg',
     'num_responses': 547090,
     'num_captions': 6996,
     'funniest_caption': "I'd like to see other people.",
     'example_query': 'https://github.com/nextml/caption-contest-data/raw/master/contests/info/553/example_query.png'}
