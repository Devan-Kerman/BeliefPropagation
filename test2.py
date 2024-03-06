import numpy as np

import beliefprop as bp

true_false = [True, False]

graph = bp.FactorGraph()

A = graph.variable("A", true_false)
B = graph.variable("B", true_false)
C = graph.variable("C", [1, 2, 3])
D = graph.variable("D", true_false)

graph.factor_table("f_1", [A, B], [[2, 3], [6, 4]])
graph.factor_table("f_2", [B, D, C], [[[7, 2, 3], [1, 5, 2]], [[8, 3, 9], [6, 4, 2]]])
graph.factor_table("f3", [C], [5, 1, 9])

print("Initial conditions")
print(A)
print(B)
print(C)
print(D)

for i in range(100):
	graph.update_all()
	print(f"Epoch {i}")
	print(A)
	print(B)
	print(C)
	print(D)
