from fastapi import (
    FastAPI,
    Request,
    File,
    UploadFile,
    Form,
    Depends
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from pydantic import BaseModel
from urllib.parse import urlencode

from app.proxy import proxy_request


app = FastAPI(
    title="KnowledgeBot API Gateway",
    version="1.0.0"
)


security = HTTPBearer()


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "KnowledgeBot API Gateway is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# AUTH SERVICE
# ============================================================

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


@app.post("/auth/register")
async def register(
    data: RegisterRequest,
    request: Request
):
    return await proxy_request(
        request=request,
        service_url="http://auth-service:8000",
        path="/auth/register",
        method="POST",
        body=data.model_dump_json().encode(),
        content_type="application/json"
    )


@app.post("/auth/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):

    body = urlencode({
        "username": username,
        "password": password
    }).encode()

    return await proxy_request(
        request=None,
        service_url="http://auth-service:8000",
        path="/auth/login",
        method="POST",
        body=body,
        content_type="application/x-www-form-urlencoded"
    )


@app.get("/auth/me")
async def auth_me(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    return await proxy_request(
        request=None,
        service_url="http://auth-service:8000",
        path="/auth/me",
        method="GET",
        authorization=token
    )


# ============================================================
# USER SERVICE
# ============================================================

class UserProfileRequest(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    profile_image: str | None = None


@app.post("/users/me")
async def create_user_profile(
    data: UserProfileRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    return await proxy_request(
        request=None,
        service_url="http://user-service:8001",
        path="/users/me",
        method="POST",
        body=data.model_dump_json().encode(),
        content_type="application/json",
        authorization=token
    )


@app.get("/users/me")
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    return await proxy_request(
        request=None,
        service_url="http://user-service:8001",
        path="/users/me",
        method="GET",
        authorization=token
    )


@app.put("/users/me")
async def update_user_profile(
    data: UserProfileRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    return await proxy_request(
        request=None,
        service_url="http://user-service:8001",
        path="/users/me",
        method="PUT",
        body=data.model_dump_json().encode(),
        content_type="application/json",
        authorization=token
    )


@app.get("/users/admin/test")
async def admin_test(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    return await proxy_request(
        request=None,
        service_url="http://user-service:8001",
        path="/users/admin/test",
        method="GET",
        authorization=token
    )


# ============================================================
# DOCUMENT SERVICE
# ============================================================

class DocumentSearchRequest(BaseModel):
    query: str
    n_results: int = 5


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    file_content = await file.read()

    return await proxy_request(
        request=None,
        service_url="http://document-service:8003",
        path="/documents/upload",
        method="POST",
        files={
            "file": (
                file.filename,
                file_content,
                file.content_type or "application/octet-stream"
            )
        },
        authorization=token
    )


@app.get("/documents/")
async def get_documents(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    return await proxy_request(
        request=None,
        service_url="http://document-service:8003",
        path="/documents/",
        method="GET",
        authorization=token
    )


@app.post("/documents/search")
async def search_documents(
    data: DocumentSearchRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    return await proxy_request(
        request=None,
        service_url="http://document-service:8003",
        path="/documents/search",
        method="POST",
        body=data.model_dump_json().encode(),
        content_type="application/json",
        authorization=token
    )


@app.get("/documents/{document_id}")
async def get_document(
    document_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    return await proxy_request(
        request=None,
        service_url="http://document-service:8003",
        path=f"/documents/{document_id}",
        method="GET",
        authorization=token
    )


@app.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    return await proxy_request(
        request=None,
        service_url="http://document-service:8003",
        path=f"/documents/{document_id}",
        method="DELETE",
        authorization=token
    )


# ============================================================
# CHAT SERVICE
# ============================================================

class ConversationRequest(BaseModel):
    title: str | None = None


class MessageRequest(BaseModel):
    content: str


@app.get("/chat/conversations")
async def get_conversations(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    return await proxy_request(
        request=None,
        service_url="http://chat-service:8002",
        path="/chat/conversations",
        method="GET",
        authorization=token
    )


@app.post("/chat/conversations")
async def create_conversation(
    data: ConversationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    return await proxy_request(
        request=None,
        service_url="http://chat-service:8002",
        path="/chat/conversations",
        method="POST",
        body=data.model_dump_json().encode(),
        content_type="application/json",
        authorization=token
    )


@app.post("/chat/conversations/{conversation_id}/messages")
async def create_message(
    conversation_id: int,
    data: MessageRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    return await proxy_request(
        request=None,
        service_url="http://chat-service:8002",
        path=f"/chat/conversations/{conversation_id}/messages",
        method="POST",
        body=data.model_dump_json().encode(),
        content_type="application/json",
        authorization=token
    )


@app.get("/chat/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    return await proxy_request(
        request=None,
        service_url="http://chat-service:8002",
        path=f"/chat/conversations/{conversation_id}/messages",
        method="GET",
        authorization=token
    )