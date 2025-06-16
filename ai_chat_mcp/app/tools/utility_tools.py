import random
import string
from mcp.server.fastmcp import FastMCP

def register_utility_tools(mcp: FastMCP):

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