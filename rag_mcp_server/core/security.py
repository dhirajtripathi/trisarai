from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import uuid

logger = logging.getLogger("rag_mcp_server.security")

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # 1. Audit Log: Request Start
        logger.info(f"REQ_START [{request_id}] {request.method} {request.url.path}")
        
        # 2. Mock RBAC / Auth Hook
        # In a real system, we would validate Bearer token or mTLS cert here
        auth_header = request.headers.get("Authorization")
        # For this POC, we just log presence of auth, but don't block unless strict mode
        if auth_header:
            logger.info(f"REQ_AUTH [{request_id}] User authenticated")
        else:
             logger.info(f"REQ_AUTH [{request_id}] Anonymous request")

        response = await call_next(request)
        
        # 3. Audit Log: Request End
        process_time = time.time() - start_time
        logger.info(f"REQ_END [{request_id}] Status: {response.status_code} Duration: {process_time:.4f}s")
        
        return response
