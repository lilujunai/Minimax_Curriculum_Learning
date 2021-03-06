from __future__ import division
# from __future__ import print_function
from numpy import *
# from matplotlib.pyplot import *
from sklearn import *
import sklearn.metrics.pairwise as simi
import scipy.spatial.distance as scd
from scipy.sparse import csr_matrix
from scipy.sparse import coo_matrix
import time
from facloc_graph import facloc_graph
#from satcoverage import satcoverage
from concavefeature import concavefeature
from copy import deepcopy
#from setcover import setcover 
#from submodular_coreset import submodular_coreset
#from videofeaturefunc import videofeaturefunc

class submdl_teach_welfare:

	def __init__(self, X, rewardMat, FF='facloc', F_parameter=['euclidean_gaussian', 15]):

		self.num_learner = rewardMat.shape[0]
		self.num_sample = rewardMat.shape[1]
		self.rewardMat = rewardMat
		# self.wt = wt

		if FF == 'facloc':
			self.F = facloc_graph(X, F_parameter[0], F_parameter[1])
		elif FF == 'satcoverage':
			self.F = satcoverage(X, F_parameter[0], F_parameter[1])
		elif FF == 'concavefeature':
			self.F = concavefeature(X, F_parameter)
		elif FF == 'setcover':
			self.F = setcover(X, F_parameter[0], F_parameter[1])
		elif FF == 'videofeaturefunc':
			self.F = videofeaturefunc(X)
			X = X[1]
		else:
			print 'Function can only be facloc, satcoverage, concavefeature, setcover or videofeaturefunc'

	# def update_wt(wt):
		# self.wt = wt

	def update_reward(self, rewardMat):
		self.rewardMat = rewardMat

	def compute_min_sin_gain_F(self):

		V = range(self.num_sample)
		nn, Vobj = self.F.evaluateV()
		minGain = Vobj - asarray([self.F.evaluate_decremental(nn, x, V)[1] for x in V])
		sinGain = asarray([self.F.evaluate([x])[1] for x in V])

		return minGain, sinGain

	def evaluate_incremental(self, nn, Lobj, Fobj, A, a):

		nn1 = deepcopy(nn)
		Lobj1 = list(Lobj)
		Fobj1 = list(Fobj)

		if a[1] not in A[a[0]]:
			nn1[a[0]], Fobj_a = self.F.evaluate_incremental(nn1[a[0]], a[1])
			Fobj1[a[0]] = Fobj_a
			Lobj1[a[0]] += self.rewardMat[a[0], a[1]]

		obj = sum(Lobj1) + sum(Fobj1)

		return nn1, Lobj1, Fobj1, obj

	def evaluate_incremental_fast(self, nn, Fobj_old, A, a):

		if a[1] not in A:
			nn1, Fobj = self.F.evaluate_incremental(nn, a[1])
			Lobj = self.rewardMat[a[0], a[1]]

		return nn1, Lobj, Fobj, Fobj_old - Lobj - Fobj

	def evaluate(self, A):

		nn = []
		Lobj = []
		Fobj = []
		for i in range(self.num_learner):
			Lobj.append(sum(self.rewardMat[i, A[i]]))
			nn_i, Fobj_i = self.F.evaluate(A[i])
			Fobj.append(Fobj_i)
			nn.append(nn_i)

		obj = sum(Lobj) + sum(Fobj)

		return nn, Lobj, Fobj, obj

	def evaluate_decremental(self, nn, Lobj, Fobj, a, A):

		nn1 = deepcopy(nn)
		Lobj1 = list(Lobj)
		Fobj1 = list(Fobj)

		if a[1] in A[a[0]]:
			nn1[a[0]], Fobj_a = self.F.evaluate_decremental(nn1[a[0]], a[1], A[a[0]])
			Fobj1[a[0]] = Fobj_a
			Lobj1[a[0]] -= self.rewardMat[a[0], a[1]]

		obj = sum(Lobj1) + sum(Fobj1)

		return nn1, Lobj1, Fobj1, obj

	def evaluateV(self):

		nn, Fobj = self.F.evaluateV()
		nn = [nn] * self.num_learner
		Fobj = [Fobj] * self.num_learner
		Lobj = sum(self.rewardMat, axis = 1)

		obj = sum(Lobj) + sum(Fobj)

		return nn, Lobj, Fobj, obj