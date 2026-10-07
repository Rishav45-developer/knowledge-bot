import httpx

from fastapi import Request
from fastapi.responses import Response


async def proxy_request(
    request: Request | None,
    service_url: str,
    path: str,
    method: str | None = None,
    body: bytes | None = None,
    content_type: str | None = None,
    files: dict | None = None,
    authorization: str | None = None
):
    url = f"{service_url}{path}"

    # Preserve query parameters if an incoming request exists
    if request is not None and request.url.query:
        url += f"?{request.url.query}"

    headers = {}

    # Forward authorization header
    if authorization:
        headers["authorization"] = f"Bearer {authorization}"

    elif request is not None:
        incoming_authorization = request.headers.get("authorization")

        if incoming_authorization:
            headers["authorization"] = incoming_authorization

    # Forward content type for JSON/form requests
    if content_type:
        headers["content-type"] = content_type

    # Determine HTTP method
    if method is not None:
        request_method = method.upper()

    elif request is not None:
        request_method = request.method

    else:
        request_method = "POST"

    async with httpx.AsyncClient(timeout=120.0) as client:

        # File upload
        if files is not None:

            response = await client.request(
                method=request_method,
                url=url,
                headers=headers,
                files=files
            )

        else:

            response = await client.request(
                method=request_method,
                url=url,
                headers=headers,
                content=body
            )

    # Remove headers that should not be forwarded
    response_headers = dict(response.headers)

    response_headers.pop("content-length", None)
    response_headers.pop("transfer-encoding", None)
    response_headers.pop("connection", None)

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=response_headers,
        media_type=response.headers.get("content-type")
    )