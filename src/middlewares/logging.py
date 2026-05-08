import json
import time

from fastapi import Request
from starlette.concurrency import iterate_in_threadpool

from src.utils.logger import app_logger


async def logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        error_detail = "N/A"
        if response.status_code >= 400:
            response_body = [chunk async for chunk in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(response_body))
            try:
                data = json.loads(b"".join(response_body).decode())
                detail = data.get("detail")
                if isinstance(detail, list):
                    error_detail = "; ".join(
                        [f"{err.get('msg')} (loc: {err.get('loc')})" for err in detail]
                    )
                else:
                    error_detail = str(detail)
            except Exception:
                error_detail = "Could not decode error body"
        log_data = {
            "tags": {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": f"{process_time:.4f}s",
                "detail": error_detail,
            }
        }
        if 400 <= response.status_code < 500:
            app_logger.warning(
                f"Client Error: {request.method} {request.url.path} "
                f"returned {response.status_code}",
                extra=log_data,
            )
        elif response.status_code >= 500:
            app_logger.error(
                f"Server Error: {request.method} {request.url.path} failed", extra=log_data
            )
        else:
            app_logger.info(
                f"Request: {request.method} {request.url.path} - {response.status_code}",
                extra=log_data,
            )
        return response
    except Exception as e:
        process_time = time.perf_counter() - start_time
        app_logger.exception(
            f"Unhandled exception during {request.method} {request.url.path}",
            extra={
                "tags": {
                    "method": request.method,
                    "path": request.url.path,
                    "duration": f"{process_time:.4f}s",
                }
            },
        )
        raise e
