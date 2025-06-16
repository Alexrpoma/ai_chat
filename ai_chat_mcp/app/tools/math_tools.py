import math
from mcp.server.fastmcp import FastMCP

def register_math_tools(mcp: FastMCP):

    @mcp.tool(description="Adds two numbers, 'a' and 'b'.")
    def add(a: float, b: float) -> dict:
        result = a + b
        return {"html": f"<div>The result of {a} + {b} is <strong>{result}</strong></div>"}

    @mcp.tool(description="Subtracts the second number ('b') from the first number ('a').")
    def subtract(a: float, b: float) -> dict:
        result = a - b
        return {"html": f"<div>The result of {a} - {b} is <strong>{result}</strong></div>"}

    @mcp.tool(description="Multiplies two numbers, 'a' and 'b'.")
    def multiply(a: float, b: float) -> dict:
        """Multiplica dos números y devuelve el resultado en formato HTML."""
        print(f"\n[tool] Calculating multiplication: {a} × {b}")
        result = a * b
        return {"html": f"<div>The result of {a} × {b} is <strong>{result}</strong></div>"}

    @mcp.tool(description="Divides the first number ('a') by the second number ('b').")
    def divide(a: float, b: float) -> dict:
        """Divide dos números y devuelve el resultado o un error en formato HTML."""
        print(f"\n[tool] Calculating division: {a} ÷ {b}")
        if b == 0:
            return {"html": "<div class='error'>Error: Cannot divide by zero.</div>"}
        result = a / b
        return {"html": f"<div>The result of {a} ÷ {b} is <strong>{result}</strong></div>"}

    @mcp.tool(description="Raises a base number to the power of an exponent.")
    def power(base: float, exponent: float) -> dict:
        """Eleva un número a una potencia y devuelve el resultado en formato HTML."""
        print(f"\n[tool] Calculating power: {base} ^ {exponent}")
        result = base ** exponent
        return {"html": f"<div>The result of {base} ^ {exponent} is <strong>{result}</strong></div>"}

    @mcp.tool(description="Calculates the square root of a non-negative number.")
    def square_root(n: float) -> dict:
        """Calcula la raíz cuadrada y devuelve el resultado o un error en formato HTML."""
        print(f"\n[tool] Calculating square root of {n}")
        if n < 0:
            return {"html": "<div class='error'>Error: Cannot calculate square root of a negative number.</div>"}
        result = math.sqrt(n)
        return {"html": f"<div>The square root of {n} is <strong>{result}</strong></div>"}

    @mcp.tool(description="Calculates the factorial of a non-negative integer 'n'.")
    def factorial(n: int) -> dict:
        """Calcula el factorial y devuelve el resultado o un error en formato HTML."""
        print(f"\n[tool] Calculating factorial of {n}")
        if not isinstance(n, int):
            return {"html": "<div class='error'>Error: Factorial input must be an integer.</div>"}
        if n < 0:
            return {"html": "<div class='error'>Error: Factorial is not defined for negative numbers.</div>"}
        if n > 170:
            return {"html": "<div class='error'>Error: Number too large for standard factorial calculation.</div>"}
        result = math.factorial(n)
        return {"html": f"<div>The factorial of {n} is <strong>{result}</strong></div>"}

    @mcp.tool(description="Calculates a given percentage of a specific value.")
    def percentage(value: float, percent: float) -> dict:
        """Calcula un porcentaje y devuelve el resultado en formato HTML."""
        print(f"\n[tool] Calculating {percent}% of {value}")
        if percent < 0:
            print(f"[tool_warn] Calculating percentage with a negative percent value: {percent}%")
        result = (value * percent) / 100
        return {"html": f"<div>{percent}% of {value} is <strong>{result}</strong></div>"}