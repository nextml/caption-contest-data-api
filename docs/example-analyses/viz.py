"""
From https://github.com/stsievert/salmon-experiments/blob/8daa4e23ca9960bc585a83828ff6ab71f1b90584/response-rate-next2/viz.py
"""

import stats_next as stats
import pandas as pd
import msgpack
import warnings

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

def lineplot(
    data, x, y, hue, style="-", hue_order=None, ci=0.25, ax=None, estimator="median", palette="copper"
):
    if ax is None:
        fig, ax = plt.subplots()
    if hue_order is None:
        hue_order = sorted(data[hue].unique())
    if isinstance(palette, list):
        colors = palette
    else:
        cmap = mpl.cm.get_cmap(palette)
        colors = [cmap(x) for x in np.linspace(0, 1, num=len(hue_order))]
    for k, (h, color) in enumerate(zip(hue_order, colors)):
        show = data[data[hue] == h]
        kwargs = dict(index=x, values=y)
        middle = show.pivot_table(aggfunc=estimator, **kwargs)
        if not len(middle):
            continue
        _style = style if "C" not in style else style.format(k=k)
        if isinstance(style, list):
            _style = style[k]
        
        ax.plot(middle, _style, label=h, color=color)
        if ci > 0:
            lower = show.pivot_table(aggfunc=lambda x: x.quantile(q=ci), **kwargs)
            upper = show.pivot_table(aggfunc=lambda x: x.quantile(q=1 - ci), **kwargs)
            assert (lower.index == upper.index).all()
            ax.fill_between(
                lower.index.values,
                y1=lower.values.flatten(),
                y2=upper.values.flatten(),
                color=color,
                alpha=0.2,
            )
    ax.legend(loc="best")
    return ax
