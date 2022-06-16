"""
From https://github.com/stsievert/salmon-experiments/blob/8daa4e23ca9960bc585a83828ff6ab71f1b90584/response-rate-next2/stats_next.py

This file is a collection of various stat functions.
Input: embedding filenames.
Output: stats for each embedding.
The following stats are collected:
* Accuracy
* Distance from ground truth embedding
* Nearest neighbor accuracy
"""

from time import time
from typing import Tuple, Union, Dict, List, Tuple
from numbers import Number as NumberType
import msgpack
import pandas as pd
from pprint import pprint

import numpy as np
from scipy.spatial import procrustes
from scipy.spatial.distance import pdist, squareform
from sklearn.manifold import SpectralEmbedding
import numpy.linalg as LA

ArrayLike = Union[list, np.ndarray]
Number = Union[NumberType, int, float, np.integer, np.floating]


def collect(
    embedding: ArrayLike, targets: List[int], X_test: ArrayLike
) -> Dict[str, float]:
    embedding = np.asarray(embedding)
    X_test = np.asarray(X_test)

    accuracy = _get_acc(embedding, X_test)
    nn_acc, nn_diffs = _get_nn_diffs(embedding, targets)

    diff_stats = {
        f"nn_diff_p{k}": np.percentile(nn_diffs, k)
        for k in [99, 98, 95, 90, 80, 70, 60, 50, 40, 30, 20, 10, 5, 2, 1]
    }
    nn_dists = {f"nn_acc_radius_{k}": (nn_diffs <= k).mean() for k in range(30)}

    n, d = embedding.shape
    stats = {}
    if d > 1:
        reduce = SpectralEmbedding(n_components=1, affinity="nearest_neighbors")
        embedding = reduce.fit_transform(embedding)
    norm = np.linalg.norm
    if targets:
        ground_truth = np.array(targets)
        assert (np.diff(ground_truth) > 0).all()
        ground_truth = ground_truth.reshape(-1, 1)
    else:
        ground_truth = np.arange(n).reshape(-1, 1)
    Y1, Y2, disparity = procrustes(ground_truth, embedding)
    stats = {
        "embedding_error": norm(Y1 - Y2),
        "embedding_rel_error": norm(Y1 - Y2) / norm(Y1),
        "procrustes_disparity": disparity,
    }

    return {
        "accuracy": accuracy,
        "nn_diff_median": np.median(nn_diffs),
        "nn_diff_mean": nn_diffs.mean(),
        "nn_acc": nn_acc,
        "avg_items_closer_than_NN": np.mean(items_closer_than_true_NN(embedding, targets)),
        **diff_stats,
        **stats,
        **nn_dists,
        **_dist_stats(ground_truth, embedding),
    }


def _dist_stats(ground_truth: np.ndarray, em: np.ndarray) -> Dict[str, Number]:
    D_star = pdist(ground_truth)
    D_hat = pdist(em)
    D_star /= D_star.max()
    D_hat /= D_hat.max()
    return {"dist_rel_error": LA.norm(D_hat - D_star) / LA.norm(D_star)}


def _get_acc(embedding: np.ndarray, X: np.ndarray) -> float:
    assert isinstance(embedding, np.ndarray)
    n, d = embedding.shape
    # X[i] is always [h, w, l] so zero is the right choice.
    y = np.zeros(len(X)).astype("int")
    assert X.ndim == 2 and X.shape[1] == 3, f"{type(X)}, {X.shape}"
    y_hat = TSTE_predict(X, embedding=embedding)
    assert all(_.dtype.kind in ["u", "i"] for _ in [y, y_hat])
    acc = (y == y_hat).mean()
    return acc


def nn_accs(em: np.ndarray, targets: List[int]):
    nn_acc, nn_diffs = _get_nn_diffs(embedding, targets)

    diff_stats = {
        f"nn_diff_p{k}": np.percentile(nn_diffs, k)
        for k in [99, 98, 95, 90, 80, 70, 60, 50, 40, 30, 20, 10, 5, 2, 1]
    }
    nn_dists = {f"nn_acc_radius_{k}": (nn_diffs <= k).mean() for k in range(30)}
    return nn_dists

def _get_nn_diffs(embedding, targets: List[int]) -> Tuple[float, np.ndarray]:
    """
    Get the NN accuracy and the number of objects that are closer than the
    true NN.
    """
    true_nns = []
    t = np.array(targets)
    for ti in targets:
        true_dist = np.abs(t - ti).astype("float32")
        true_dist[true_dist <= 0] = np.inf
        true_nns.append(true_dist.argmin())
    true_nns = np.array(true_nns).astype("int")

    dists = distances(gram_matrix(embedding))
    dists[dists <= 0] = np.inf

    neighbors = dists.argmin(axis=1)
    neighbor_dists = np.abs(neighbors - true_nns)
    nn_acc = (neighbor_dists == 0).mean()
    return nn_acc, neighbor_dists

def items_closer_than_true_NN(embedding, targets) -> List[int]:
    # find true nearest neighbors
    true_nns = []
    t = np.array(targets)
    for ti in targets:
        true_dist = np.abs(t - ti).astype("float32")
        true_dist[np.abs(true_dist) < 1e-3] = np.inf
        true_nns.append(true_dist.argmin())

    # for each item in the embedding, how many items are between
    # it and the true NN?

    ## so, get distance matrix
    dists = distances(gram_matrix(embedding))
    dists[dists <= 0] = np.inf

    items_closer_than_NNs = []
    for dist, true_nn in zip(dists, true_nns):
        true_nn_dist = dist[true_nn]
        items_closer_than_NN = (dist < true_nn_dist).sum()
        items_closer_than_NNs.append(items_closer_than_NN)
    return items_closer_than_NNs


#################################################################
## everything from here down copied from Salmon
# salmon/triplets/samplers/_adaptive_runners.py#Adaptive.predict
# salmon/triplets/samplers/adaptive/search/gram_utils.py
#################################################################
Array = np.ndarray
def gram_matrix(X: Array) -> Array:
    """
    Get Gram matrix from embedding
    Arguments
    ---------
    X : Array
        Embedding. X.shape == (num_items, item_dim)
    Returns
    -------
    G : Array
        Gram matrix. G.shape == (n, n)
    """
#     if isinstance(X, torch.Tensor):
#         return X @ X.transpose(0, 1)
    return X @ X.T


def distances(G: Array) -> Array:
    """
    Get distance matrix from gram matrix
    Arguments
    ---------
    G : Array
        Gram matrix. G.shape == (n, n) for n objects
    Returns
    -------
    D : Array
        Distance matrix. D.shape == (n, n)
    """
    G1 = np.diag(G).reshape(1, -1)
    G2 = np.diag(G).reshape(-1, 1)

    D = -2 * G + G1 + G2
    return D

def TSTE_predict(X, embedding=None):
    """
    Predict the answers of queries from the current embedding.
    Parameters
    ----------
    X : array-like
        Each row is ``[head, left, right]``. Each element in ``X`` or
        ``X[i, j]`` is an index of the current embedding.
    Returns
    -------
    y : array-like
        The winner of each query. An element of ``y`` is 0 if the left
        item is the predicted winner, and 1 if the right element is the
        predicted winner.
    """
    head_idx = X[:, 0].flatten()
    left_idx = X[:, 1].flatten()
    right_idx = X[:, 2].flatten()

    head = embedding[head_idx]
    left = embedding[left_idx]
    right = embedding[right_idx]

    ldiff = LA.norm(head - left, axis=1)
    rdiff = LA.norm(head - right, axis=1)

    # 1 if right closer; 0 if left closer
    # (which matches the labeling scheme)
    right_closer = rdiff < ldiff
    return right_closer.astype("uint8")

if __name__ == "__main__":
    file = "salmon/io/2021-05-18/ARR-1_history.msgpack"
    file = "next/io/2021-05-18/rate=1_history.msgpack"
    with open(file, "rb") as f:
        history = msgpack.load(f)
    datum = history[-1]
    em = datum["embedding"]
    n_responses = datum["meta"]["n_responses"]
    fnames = pd.read_csv("targets.csv.zip", header=None)[0].tolist()
    targets = [int(f.strip("i.png")) for f in fnames]
    targets = list(sorted(targets))

    X_test = [
        [i_h, i_l, i_r] if abs(h - l) < abs(h - r) else [i_h, i_r, i_l]
        for i_h, h in enumerate(targets)
        for i_l, l in enumerate(targets)
        for i_r, r in enumerate(targets)
        if h not in [l, r] and l != r
    ]

    s = collect(em, targets, X_test)
    print(len(history))
    print(n_responses, s["accuracy"])
