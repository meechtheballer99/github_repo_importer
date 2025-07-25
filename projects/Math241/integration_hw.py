def integrate(f, a, b, steps=1000):
    dx = (b - a) / steps
    return sum(f(a + i*dx) * dx for i in range(steps))

print(integrate(lambda x: x**2, 0, 1))
