import math
import random
import string

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Echo Server with Tools")


@mcp.tool(description="Get the current weather for a specified city.")
def get_weather(city: str) -> dict:
    """Devuelve el clima actual para una ciudad en formato HTML."""
    print(f"\n[tool] Getting weather for {city}...")
    if city.lower() == "miami":
        weather_report = f"The weather in {city} is sunny with a chance of afternoon showers."
    elif city.lower() == "london":
        weather_report = f"The weather in {city} is cloudy with a high of 15°C."
    else:
        weather_report = f"The weather in {city} is currently pleasant."
    return {"html": f"<div>{weather_report}</div>"}


@mcp.tool(description="Adds two numbers, 'a' and 'b'.")
def add(a: float, b: float) -> dict:
    """Suma dos números y devuelve el resultado en formato HTML."""
    print(f"\n[tool] Calculating sum: {a} + {b}")
    result = a + b
    return {"html": f"<div>The result of {a} + {b} is <strong>{result}</strong></div>"}


@mcp.tool(description="Subtracts the second number ('b') from the first number ('a').")
def subtract(a: float, b: float) -> dict:
    """Resta dos números y devuelve el resultado en formato HTML."""
    print(f"\n[tool] Calculating subtraction: {a} - {b}")
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


@mcp.tool(description="Counts the number of words in a given text. Words are separated by spaces.")
def count_words(text: str) -> dict:
    """Cuenta las palabras en un texto y devuelve el resultado en formato HTML."""
    print(f"\n[tool] Counting words in text...")
    if not text.strip():
        count = 0
    else:
        count = len(text.split())
    return {"html": f"<div>The text has <strong>{count}</strong> words.</div>"}


@mcp.tool(description="Counts the number of characters in a given text. Optionally includes or excludes spaces.")
def count_characters(text: str, include_spaces: bool = True) -> dict:
    """Cuenta los caracteres en un texto y devuelve el resultado en formato HTML."""
    print(f"\n[tool] Counting characters (spaces {'included' if include_spaces else 'excluded'})")
    if include_spaces:
        count = len(text)
    else:
        count = len(text.replace(" ", ""))
    return {
        "html": f"<div>The text has <strong>{count}</strong> characters (spaces {'included' if include_spaces else 'excluded'}).</div>"}


@mcp.tool(description="Reverses the order of characters in the given text.")
def reverse_text(text: str) -> dict:
    """Invierte un texto y lo devuelve en formato HTML."""
    print(f"\n[tool] Reversing text...")
    reversed_str = text[::-1]
    return {"html": f"<div>Reversed text: <pre><code>{reversed_str}</code></pre></div>"}


@mcp.tool(description="Converts a temperature from Celsius to Fahrenheit.")
def celsius_to_fahrenheit(celsius: float) -> dict:
    """Convierte Celsius a Fahrenheit y devuelve el resultado en formato HTML."""
    print(f"\n[tool] Converting {celsius}°C to Fahrenheit...")
    fahrenheit = (celsius * 9 / 5) + 32
    return {"html": f"<div>{celsius}°C is equal to <strong>{fahrenheit:.2f}°F</strong>.</div>"}


@mcp.tool(description="Converts a temperature from Fahrenheit to Celsius.")
def fahrenheit_to_celsius(fahrenheit: float) -> dict:
    """Convierte Fahrenheit a Celsius y devuelve el resultado en formato HTML."""
    print(f"\n[tool] Converting {fahrenheit}°F to Celsius...")
    celsius = (fahrenheit - 32) * 5 / 9
    return {"html": f"<div>{fahrenheit}°F is equal to <strong>{celsius:.2f}°C</strong>.</div>"}


@mcp.tool(description="Generates a random integer between a minimum and maximum value.")
def generate_random_number(min_val: int = 1, max_val: int = 100) -> dict:
    """Genera un número aleatorio y lo devuelve en formato HTML."""
    print(f"\n[tool] Generating random number between {min_val} and {max_val}...")
    if min_val > max_val:
        return {
            "html": f"<div class='error'>Error: Minimum value ({min_val}) cannot be greater than maximum value ({max_val}).</div>"}
    random_num = random.randint(min_val, max_val)
    return {"html": f"<div>Random number between {min_val} and {max_val}: <strong>{random_num}</strong></div>"}


@mcp.tool(description="Generates a random password of a specified length.")
def generate_password(length: int = 12, include_symbols: bool = True) -> dict:
    """Genera una contraseña aleatoria y la devuelve en formato HTML."""
    print(
        f"\n[tool] Generating password of length {length} (symbols {'included' if include_symbols else 'excluded'})...")

    if not isinstance(length, int) or length < 4:
        return {"html": "<div class='error'>Error: Password length must be an integer of at least 4.</div>"}
    if length > 128:
        return {"html": "<div class='error'>Error: Password length is too large (max 128 recommended).</div>"}

    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += "!@#$%^&*"

    password = ''.join(random.choice(characters) for _ in range(length))
    return {"html": f"<div>Generated Password: <pre><code>{password}</code></pre></div>"}


@mcp.tool(description="Registers a new user with a username and email.")
def register_user(username: str, email: str) -> dict:
    """Registra un usuario y devuelve el estado en formato HTML."""
    print(f"\n[tool] Registering user with username: {username}, email: {email}")

    if not username or not email:
        return {"html": "<div class='error'><strong>Error:</strong> Username and email cannot be empty.</div>"}
    if "@" not in email or "." not in email.split('@')[-1]:
        return {"html": f"<div class='error'><strong>Error:</strong> Invalid email format for {email}.</div>"}

    user_id = f"usr_{random.randint(1000, 9999)}"
    html_response = f"""
    <div class='success'>
      <p>User <strong>{username}</strong> registered successfully.</p>
      <h4>User Details:</h4>
      <ul>
        <li><strong>Username:</strong> {username}</li>
        <li><strong>Email:</strong> {email}</li>
        <li><strong>User ID:</strong> {user_id}</li>
      </ul>
    </div>
    """
    return {"html": html_response}


@mcp.tool(description="Return offers to client")
def ofertas_html() -> dict:
    """Devuelve una lista HTML de ofertas."""
    print("Ofertas . . .")
    html = "<ul><li>Oferta 1</li><li>Oferta 2</li><li>Oferta 3</li></ul>"
    return {"html": html}

if __name__ == "__main__":
    print("Starting FastMCP server with various tools...")
    mcp.run(transport="streamable-http")