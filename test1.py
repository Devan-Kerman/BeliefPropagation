import beliefprop as bp

true_false = [True, False]

graph = bp.FactorGraph()
A = graph.const("A", true_false, [.9, .1])
B = graph.const("B", true_false, [.9, .1])

C = graph.variable("C", true_false)
D = graph.variable("D", true_false)

E = graph.variable("E", true_false)

graph.factor("C = A & B", [A, B, C], lambda a, b, c: float((a and b) == c))
graph.factor("C = A | B", [A, B, D], lambda a, b, d: float((a or b) == d))

for i in range(10):
    print(f"Epoch {i}")
    print(A)
    print(B)
    print(C)
    print(D)
    print(E)
    graph.update_all()

print("Result:")
print(A)
print(B)
print(C)
print(D)
print(E)
