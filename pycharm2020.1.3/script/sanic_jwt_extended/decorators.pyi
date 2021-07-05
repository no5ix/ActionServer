from typing import Any, Callable, List, Optional, Tuple

from sanic.request import Request

def _get_request(args: Tuple[Any]) -> Request: ...
def _get_raw_jwt_from_request(
    request: Request, is_access: bool = ...
) -> Tuple[str, Optional[str]]: ...
def _get_raw_jwt_from_headers(
    request: Request, is_access: bool
) -> Tuple[str, None]: ...
def _get_raw_jwt_from_query_params(request: Request, _: Any) -> Tuple[str, None]: ...
def _get_raw_jwt_from_cookies(
    request: Request, is_access: bool
) -> Tuple[str, Optional[str]]: ...
def jwt_required(
    function: Callable = ...,
    *,
    allow: List[str] = ...,
    deny: List[str] = ...,
    fresh_required: bool = ...
) -> Any: ...
def jwt_optional(function: Callable) -> Any: ...
def refresh_jwt_required(
    function: Callable = ..., *, allow: List[str] = ..., deny: List[str] = ...
) -> Any: ...