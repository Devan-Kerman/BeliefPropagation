import beliefprop as bp

true_false = [True, False]

graph = bp.FactorGraph()
A = graph.const("A", true_false, [.9, .1])
B = graph.const("B", true_false, [.9, .1])

C = graph.variable("C", true_false)

graph.factor("A_AND_B", [A, B, C], lambda a, b, c: float((a or b) == c))

for i in range(10):  # You can adjust the number of iterations
    print(f"Epoch {i}")
    print(A)
    print(B)
    print(C)
    graph.update_all()

print("Result:")
print(A)
print(B)
print(C)
