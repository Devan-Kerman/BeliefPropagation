from __future__ import annotations
import itertools
import numpy as np
from typing import Any, Callable, Dict, List

epsilon = 1e-11

class BeliefPropNode(object):
	name: str

	def __init__(self, name: str):
		self.name = name

	def update(self):
		pass

	def post_update(self):
		pass

vfilter = np.vectorize(lambda msg, prod: (msg if (msg > epsilon) or (prod <= epsilon) else 1.))
vfilter_rev = np.vectorize(lambda msg, prod, nz_prod: (prod / msg if msg > epsilon else nz_prod))

class ConstOrVarNode(BeliefPropNode):
	domain: List[Any]

	def __init__(self, name: str, domain: List[Any]):
		super().__init__(name)
		self.domain = domain

	def set_initial_outbound(self, factor: 'FactorNode'):
		pass

	def rem_initial(self, factor: 'FactorNode'):
		pass

	def outbound_to(self, factor: 'FactorNode') -> np.ndarray:
		pass

	def uniform(self) -> np.ndarray:
		return np.ones(shape=len(self.domain)) / len(self.domain)

class ConstNode(ConstOrVarNode):
	prob: np.ndarray

	def __init__(self, name: str, domain: List[Any], prob: np.ndarray):
		super().__init__(name, domain)
		z = prob.sum()
		self.prob = prob/z if z > epsilon else self.uniform()

	def outbound_to(self, factor: 'FactorNode') -> np.ndarray:
		return self.prob

	def __str__(self):
		return f"P({self.name})={np.round(self.prob, 3)}"

class VariableNode(ConstOrVarNode):
	domain: List[Any]

	outbound: Dict['FactorNode', np.ndarray]
	outbound_new: Dict['FactorNode', np.ndarray]

	def __init__(self, name: str, domain: List[Any]):
		super().__init__(name, domain)
		self.outbound = dict()
		self.outbound_new = dict()

	def initial(self) -> np.ndarray:
		return self.uniform()

	def set_initial_outbound(self, factor: 'FactorNode'):
		self.outbound[factor] = self.initial()
		self.outbound_new[factor] = self.initial()

	def rem_initial(self, factor: 'FactorNode'):
		del self.outbound[factor]
		del self.outbound_new[factor]

	def outbound_to(self, factor: 'FactorNode') -> np.ndarray:
		return self.outbound[factor]

	def update(self):
		prod = np.ones(shape=len(self.domain))
		nz_prod = np.ones_like(prod)

		for a, msg in self.outbound.items():
			inbound = a.outbound[self]

			prod *= inbound
			nz_prod *= vfilter(inbound, prod)

		for a, msg in self.outbound_new.items():
			inbound = a.outbound[self]
			msg[:] = vfilter_rev(inbound, prod, nz_prod)

	def post_update(self):
		self.outbound, self.outbound_new = {k: v/v.sum() for k, v in self.outbound_new.items()}, self.outbound

	def __str__(self):
		inbound = np.prod([f.outbound[self] for f in self.outbound.keys()] + [np.ones(len(self.domain))], axis=0)
		return f"P({self.name})={np.round(inbound / inbound.sum(), 3)}"

class FactorNode(BeliefPropNode):
	arguments: List[ConstOrVarNode]
	function: Callable[[List[Any]], float]

	outbound: Dict[VariableNode, np.ndarray]
	outbound_new: Dict[VariableNode, np.ndarray]

	def __init__(self, name: str, arguments: List[ConstOrVarNode], fn: Callable[[List[Any]], float]):
		super().__init__(name)
		self.outbound = {arg: arg.initial() for arg in arguments if isinstance(arg, VariableNode)}
		self.outbound_new = {arg: arg.initial() * 0 for arg in arguments if isinstance(arg, VariableNode)}
		self.arguments = arguments
		self.function = fn

		for arg in arguments:
			arg.set_initial_outbound(self)

	def update(self):
		for x in itertools.product(*(enumerate(v.domain) for v in self.arguments)):
			args = [v for _, v in x]
			f_prob = self.function(*args)
			if f_prob > 0:
				prod, nz_prod = 1., 1.
				for v, (i, _) in zip(self.arguments, x):
					inbound = v.outbound_to(self)[i]
					prod *= inbound
					nz_prod *= vfilter(inbound, prod)

				for v, (i, _) in zip(self.arguments, x):
					if v in self.outbound_new:
						inbound = v.outbound_to(self)[i]
						incr = f_prob * vfilter_rev(inbound, prod, nz_prod)
						self.outbound_new[v][i] += incr

	def post_update(self):
		self.outbound, self.outbound_new = self.outbound_new, {k: k.initial() * 0 for k in self.outbound.keys()}

	def __del__(self):
		for arg in self.arguments:
			arg.rem_initial(self)

class FactorGraph(object):
	nodes: List[BeliefPropNode]

	def __init__(self):
		self.nodes = []

	def variable(self, name: str, domain: List[Any]):
		var = VariableNode(name, domain)
		self.nodes.append(var)
		return var

	def factor(self, name: str, args: List[VariableNode], fn: Callable[[List[Any]], float]):
		factor = FactorNode(name, args, fn)
		self.nodes.append(factor)
		return factor

	def factor_table(self, name: str, args: List[VariableNode], table: List):
		def search_table(*values):
			indices = [arg.domain.index(v) for arg, v in zip(args, values)]
			curr = table
			for i in indices:
				curr = curr[i]
			return float(curr)

		return self.factor(name, args, search_table)

	def const(self, name: str, domain: List[Any], prob: List[float]):
		const = ConstNode(name, domain, np.array(prob, dtype=np.float32))
		self.nodes.append(const)
		return const

	def update_all(self):
		for node in self.nodes:
			node.update()

		for node in self.nodes:
			node.post_update()
