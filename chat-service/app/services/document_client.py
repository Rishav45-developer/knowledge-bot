import httpx


DOCUMENT_SERVICE_URL = "http://127.0.0.1:8003"

def search_documents(
        query: str,
        token: str,
        n_results: int = 5
):
    url = f"{DOCUMENT_SERVICE_URL}/documents/search"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "query": query,
        "n_results": n_results
    }

    response = httpx.post(
        url,
        json=payload,
        headers=headers,
        timeout=60.0
    )

    response.raise_for_status()

    return response.json()