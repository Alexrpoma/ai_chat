from mcp.server.fastmcp import FastMCP


def register_text_tools(mcp: FastMCP):

    @mcp.tool(description="Counts the number of words in a given text.")
    def count_words(text: str) -> dict:
        count = len(text.split()) if text.strip() else 0
        return {"html": f"<div>The text has <strong>{count}</strong> words.</div>"}

    @mcp.tool(description="Reverses the order of characters in the given text.")
    def reverse_text(text: str) -> dict:
        return {"html": f"<div>Reversed text: <pre><code>{text[::-1]}</code></pre></div>"}

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