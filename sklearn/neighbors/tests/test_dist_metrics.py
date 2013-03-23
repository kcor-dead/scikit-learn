import itertools

import numpy as np
from numpy.testing import assert_allclose

import scipy
from scipy.spatial.distance import cdist, pdist, squareform
from sklearn.neighbors.dist_metrics import DistanceMetric
from nose import SkipTest


def cmp_version(version1, version2):
    version1 = tuple(map(int, version1.split('.')[:2]))
    version2 = tuple(map(int, version2.split('.')[:2]))

    if version1 < version2:
        return -1
    elif version1 > version2:
        return 1
    else:
        return 0


class TestMetrics:
    def __init__(self, n1=20, n2=25, d=4, zero_frac=0.5,
                 rseed=0, dtype=np.float64):
        np.random.seed(rseed)
        self.X1 = np.random.random((n1, d)).astype(dtype)
        self.X2 = np.random.random((n2, d)).astype(dtype)

        # make boolean arrays: ones and zeros
        self.X1_bool = self.X1.round(0)
        self.X2_bool = self.X2.round(0)

        V = np.random.random((d, d))
        VI = np.dot(V, V.T)

        self.metrics = {'euclidean':{},
                        'cityblock':{},
                        'minkowski':dict(p=(1, 1.5, 2, 3)),
                        'chebyshev':{},
                        'seuclidean':dict(V=(np.random.random(d),)),
                        'wminkowski':dict(p=(1, 1.5, 3),
                                          w=(np.random.random(d),)),
                        'mahalanobis':dict(VI=(VI,)),
                        'hamming':{},
                        'canberra':{},
                        'braycurtis':{}}

        self.bool_metrics = ['matching', 'jaccard', 'dice',
                             'kulsinski', 'rogerstanimoto', 'russellrao',
                             'sokalmichener', 'sokalsneath']

    def test_cdist(self):
        for metric, argdict in self.metrics.iteritems():
            keys = argdict.keys()
            for vals in itertools.product(*argdict.values()):
                kwargs = dict(zip(keys, vals))
                D_true = cdist(self.X1, self.X2, metric, **kwargs)
                yield self.check_cdist, metric, kwargs, D_true

        for metric in self.bool_metrics:
            D_true = cdist(self.X1_bool, self.X2_bool, metric)
            yield self.check_cdist_bool, metric, D_true
            
    def check_cdist(self, metric, kwargs, D_true):
        if metric == 'canberra' and cmp_version(scipy.__version__, '0.9') <= 0:
            raise SkipTest("Canberra distance incorrect in scipy < 0.9")
        dm = DistanceMetric.get_metric(metric, **kwargs)
        D12 = dm.pairwise(self.X1, self.X2)
        assert_allclose(D12, D_true)

    def check_cdist_bool(self, metric, D_true):
        dm = DistanceMetric.get_metric(metric)
        D12 = dm.pairwise(self.X1_bool, self.X2_bool)
        assert_allclose(D12, D_true)

    def test_pdist(self):
        for metric, argdict in self.metrics.iteritems():
            keys = argdict.keys()
            for vals in itertools.product(*argdict.values()):
                kwargs = dict(zip(keys, vals))
                D_true = cdist(self.X1, self.X1, metric, **kwargs)
                yield self.check_pdist, metric, kwargs, D_true

        for metric in self.bool_metrics:
            D_true = cdist(self.X1_bool, self.X1_bool, metric)
            yield self.check_pdist_bool, metric, D_true

    def check_pdist(self, metric, kwargs, D_true):
        if metric == 'canberra' and cmp_version(scipy.__version__, '0.9') <= 0:
            raise SkipTest("Canberra distance incorrect in scipy < 0.9")
        dm = DistanceMetric.get_metric(metric, **kwargs)
        D12 = dm.pairwise(self.X1)
        assert_allclose(D12, D_true)

    def check_pdist_bool(self, metric, D_true):
        dm = DistanceMetric.get_metric(metric)
        D12 = dm.pairwise(self.X1_bool)
        assert_allclose(D12, D_true)


def test_haversine_metric():
    def haversine_slow(x1, x2):
        return 2 * np.arcsin(np.sqrt(np.sin(0.5 * (x1[0] - x2[0])) ** 2
                                     + np.cos(x1[0]) * np.cos(x2[0]) *
                                     np.sin(0.5 * (x1[1] - x2[1])) ** 2))

    X = np.random.random((10, 2))

    haversine = DistanceMetric.get_metric("haversine")

    D1 = haversine.pairwise(X)
    D2 = np.zeros_like(D1)
    for i, x1 in enumerate(X):
        for j, x2 in enumerate(X):
            D2[i, j] = haversine_slow(x1, x2)

    assert_allclose(D1, D2)
    assert_allclose(haversine.dist_to_rdist_arr(D1),
                    np.sin(0.5 * D2) ** 2)


def test_pyfunc_metric():
    def dist_func(x1, x2):
        return np.sqrt(np.sum((x1 - x2) ** 2))

    X = np.random.random((10, 3))

    euclidean = DistanceMetric.get_metric("euclidean")
    pyfunc = DistanceMetric.get_metric("pyfunc", func=dist_func)

    D1 = euclidean.pairwise(X)
    D2 = pyfunc.pairwise(X)

    assert_allclose(D1, D2)

        
if __name__ == '__main__':
    import nose
    nose.runmodule()
