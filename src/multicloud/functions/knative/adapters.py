"""
Adapters to normalize event data from Knative to the multi-cloud
event format.
"""

import asyncio
import logging
from multicloud.functions.common.multicloud_event import MultiCloudEvent


async def adapt_asgi_request(scope, receive) -> MultiCloudEvent:
    """
    Parse a Knative HTTP Request into a normalized MultiCloudEvent.

    Args:
        scope: ASGI scope dictionary containing request metadata
        receive: ASGI receive callable for getting request body

    Returns:
        MultiCloudEvent: Normalized event object
    """
    try:
        # Receive the request body
        message = await receive()
        body = b""

        if message["type"] == "http.request":
            body = message.get("body", b"")

            # Continue receiving if there's more body content
            while message.get("more_body", False):
                message = await receive()
                body += message.get("body", b"")

        # Convert headers from bytes to strings
        headers = {}
        for header_name, header_value in scope.get("headers", []):
            headers[header_name.decode("utf-8")] = header_value.decode("utf-8")

        # Simple body conversion: decode text-based content, keep binary as bytes
        parsed_body = _convert_body(body, headers.get("content-type", ""))

        return MultiCloudEvent(
            method=scope.get("method", "GET"),
            path=scope.get("path", "/"),
            headers=headers,
            query_string=scope.get("query_string", b"").decode(),
            body=parsed_body,
            source="knative",
        )

    except (ConnectionError, asyncio.TimeoutError) as e:
        # Network/connection issues with receive()
        logging.error("Connection error while receiving ASGI request: %s", e)
        return MultiCloudEvent(
            method=scope.get("method", "GET"),
            path=scope.get("path", "/"),
            headers={"x-error": f"Connection error: {str(e)}"},
            query_string="",
            source="knative",
        )
    except (UnicodeDecodeError, UnicodeError) as e:
        # Encoding issues with headers or query string
        logging.error("Encoding error in ASGI request: %s", e)
        return MultiCloudEvent(
            method=scope.get("method", "GET"),
            path=scope.get("path", "/"),
            headers={"x-error": f"Encoding error: {str(e)}"},
            query_string="",
            source="knative",
        )
    except KeyError as e:
        # Missing required keys in scope or message
        logging.error("Missing required key in ASGI request: %s", e)
        return MultiCloudEvent(
            method="GET",
            path="/",
            headers={"x-error": f"Missing key: {str(e)}"},
            query_string="",
            source="knative",
        )


async def adapt_cloud_event_request(scope, receive) -> MultiCloudEvent:
    """
    Parse a Knative Cloud Event into a normalized MultiCloudEvent.

    Args:
        scope: ASGI scope dictionary containing request metadata
        receive: ASGI receive callable for getting request body

    Returns:
        MultiCloudEvent: Normalized event object
    """
    # TODO: Implement Cloud Event parsing
    # For now, delegate to ASGI adapter
    return await adapt_asgi_request(scope, receive)


def _convert_body(body: bytes, content_type: str):
    """
    Simple body conversion: decode text-based content types to string,
    keep binary content as bytes.
    """
    if not body:
        return None

    content_type = content_type.lower()

    # Text-based content types that should be decoded to strings
    text_types = [
        "text/",
        "application/json",
        "application/xml",
        "application/x-www-form-urlencoded",
        "multipart/",
    ]

    if any(content_type.startswith(t) for t in text_types):
        try:
            return body.decode("utf-8")
        except UnicodeDecodeError:
            logging.warning("Failed to decode text content as UTF-8, keeping as bytes")
            return body

    # Keep binary content as bytes
    return body
