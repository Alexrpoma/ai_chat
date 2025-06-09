import math
import random
import string

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Echo Server with Tools")


@mcp.tool(description="Get the current weather for a specified city.")
def get_weather(city: str):
    print(f"\n[tool] Getting weather for {city}...")
    if city.lower() == "miami":
        return f"The weather in {city} is sunny with a chance of afternoon showers."
    elif city.lower() == "london":
        return f"The weather in {city} is cloudy with a high of 15°C."
    else:
        return f"The weather in {city} is currently pleasant."


@mcp.tool(description="Adds two numbers, 'a' and 'b'.")
def add(a: float, b: float) -> float:
    print(f"\n[tool] Calculating sum: {a} + {b}")
    return a + b


@mcp.tool(description="Subtracts the second number ('b') from the first number ('a').")
def subtract(a: float, b: float) -> float:
    print(f"\n[tool] Calculating subtraction: {a} - {b}")
    return a - b


@mcp.tool(description="Multiplies two numbers, 'a' and 'b'.")
def multiply(a: float, b: float) -> float:
    print(f"\n[tool] Calculating multiplication: {a} × {b}")
    return a * b


@mcp.tool(description="Divides the first number ('a') by the second number ('b').")
def divide(a: float, b: float) -> str | float:
    print(f"\n[tool] Calculating division: {a} ÷ {b}")
    if b == 0:
        return "Error: Cannot divide by zero."
    return a / b


@mcp.tool(description="Raises a base number to the power of an exponent.")
def power(base: float, exponent: float) -> float:
    print(f"\n[tool] Calculating power: {base} ^ {exponent}")
    return base ** exponent


@mcp.tool(description="Calculates the square root of a non-negative number.")
def square_root(n: float) -> str | float:
    print(f"\n[tool] Calculating square root of {n}")
    if n < 0:
        return "Error: Cannot calculate square root of a negative number."
    return math.sqrt(n)


@mcp.tool(description="Calculates the factorial of a non-negative integer 'n'.")
def factorial(n: int) -> str | int:
    print(f"\n[tool] Calculating factorial of {n}")
    if not isinstance(n, int):
        return "Error: Factorial input must be an integer."
    if n < 0:
        return "Error: Factorial is not defined for negative numbers."
    if n > 170:
        return "Error: Number too large for standard factorial calculation, result would be infinity or overflow."
    return math.factorial(n)


@mcp.tool(description="Calculates a given percentage of a specific value.")
def percentage(value: float, percent: float) -> float:
    print(f"\n[tool] Calculating {percent}% of {value}")
    if percent < 0:
        print(f"[tool_warn] Calculating percentage with a negative percent value: {percent}%")
    return (value * percent) / 100


@mcp.tool(description="Counts the number of words in a given text. Words are separated by spaces.")
def count_words(text: str) -> int:
    print(f"\n[tool] Counting words in text...")
    if not text.strip():
        return 0
    return len(text.split())


@mcp.tool(description="Counts the number of characters in a given text. Optionally includes or excludes spaces (default is to include spaces).")
def count_characters(text: str, include_spaces: bool = True) -> int:
    print(f"\n[tool] Counting characters (spaces {'included' if include_spaces else 'excluded'})")
    if include_spaces:
        return len(text)
    else:
        return len(text.replace(" ", ""))


@mcp.tool(description="Reverses the order of characters in the given text.")
def reverse_text(text: str) -> str:
    print(f"\n[tool] Reversing text...")
    return text[::-1]


@mcp.tool(description="Converts a temperature from Celsius to Fahrenheit.")
def celsius_to_fahrenheit(celsius: float) -> float:
    print(f"\n[tool] Converting {celsius}°C to Fahrenheit...")
    return (celsius * 9 / 5) + 32


@mcp.tool(description="Converts a temperature from Fahrenheit to Celsius.")
def fahrenheit_to_celsius(fahrenheit: float) -> float:
    print(f"\n[tool] Converting {fahrenheit}°F to Celsius...")
    return (fahrenheit - 32) * 5 / 9


@mcp.tool(description="Generates a random integer between a minimum value ('min_val') and a maximum value ('max_val'), inclusive. Defaults to a range between 1 and 100 if not specified.")  # CORREGIDO y ampliado
def generate_random_number(min_val: int = 1, max_val: int = 100) -> int | str:
    print(f"\n[tool] Generating random number between {min_val} and {max_val}...")
    if min_val > max_val:
        return f"Error: Minimum value ({min_val}) cannot be greater than maximum value ({max_val})."
    return random.randint(min_val, max_val)


@mcp.tool(description="Generates a random password of a specified length. Optionally includes symbols. Default length is 12 characters, and symbols are included by default.")
def generate_password(length: int = 12, include_symbols: bool = True) -> str:
    print(
        f"\n[tool] Generating password of length {length} (symbols {'included' if include_symbols else 'excluded'})...")

    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += "!@#$%^&*"

    if not isinstance(length, int) or length < 4:
        return "Error: Password length must be an integer of at least 4 characters."
    if length > 128:
        return "Error: Password length is too large (max 128 recommended)."

    return ''.join(random.choice(characters) for _ in range(length))


@mcp.tool(description="Registers a new user with a username and email. Returns a JSON response with registration status.")
def register_user(username: str, email: str) -> dict:
    print(f"\n[tool] Registering user with username: {username}, email: {email}")
    if not username or not email:
        return {
            "status": "error",
            "message": "Username and email cannot be empty."
        }
    if "@" not in email or "." not in email.split('@')[-1]:
        return {
            "status": "error",
            "message": f"Invalid email format for {email}."
        }
    return {
        "status": "success",
        "message": f"User {username} registered successfully.",
        "user_details": {
            "username": username,
            "email": email,
            "user_id": f"usr_{random.randint(1000, 9999)}"
        }
    }


if __name__ == "__main__":
    print("Starting FastMCP server with various tools...")
    mcp.run(transport="streamable-http")