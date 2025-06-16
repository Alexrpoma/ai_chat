import httpx
from mcp.server.fastmcp import FastMCP
from ..core.config import settings


def register_business_tools(mcp: FastMCP):

    @mcp.tool(description="Fetches pending bills for a customer...")
    async def check_pending_bills(service_identifier: str, party_id: str, session_id: str) -> dict:
        print(f"\n[tool] Checking pending bills for service: {service_identifier}")

        external_service_url = settings.bills_api_url
        request_payload = {
            "partyId": party_id,
            "sessionId": session_id,
            "serviceIdentifier": service_identifier
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(external_service_url, json=request_payload, timeout=4.0)
                response.raise_for_status()
                response_data = response.json()

                api_data = response_data.get("data", {})
                transaction_id = api_data.get("transactionId")
                nested_data = api_data.get("data", {})
                html_content = nested_data.get("billDetails")

                if html_content:
                    return {
                        "html": html_content,
                        "transactionId": transaction_id
                    }
                else:
                    return {"html": "<div class='error'>Error: Bill details not found in the response.</div>"}
        except httpx.RequestError as e:
            print(f"[tool_error] Network error: {e}")
            return {"html": "<div class='error'>Error: Network problem with the billing service.</div>"}
        except Exception as e:
            print(f"[tool_error] Unexpected error: {e}")
            return {"html": "<div class='error'>An unexpected error occurred.</div>"}