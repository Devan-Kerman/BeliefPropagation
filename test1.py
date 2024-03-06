import numpy as np

import beliefprop as bp

true_false = [True, False]

graph = bp.FactorGraph()

A = graph.const("A", true_false, [.6, .4])
A_C = graph.const("A->C", true_false, [1, 0])

B = graph.const("B", true_false, [.75, .25])
B_C = graph.const("B->C", true_false, [1, 0])

C = graph.variable("C", true_false)

graph.factor("A->C", [A, A_C, C], lambda a, a_c, c: float((a == c) and a_c))
graph.factor("B->C", [B, B_C, C], lambda b, b_c, c: float((b == c) and b_c))


print("Initial conditions")
print(A)
print(B)
print(C)

for i in range(100):
	graph.update_all()
	print(f"Epoch {i}")
	print(A)
	print(B)
	print(C)

