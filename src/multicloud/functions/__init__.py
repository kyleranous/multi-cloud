"""
Knative serverless function adapters for multi-cloud compatibility.

This module provides adapters to normalize Knative requests into standardized
MultiCloudEvent objects, enabling serverless functions to work consistently
across different cloud providers.

Exports:
    adapt_asgi_request: Converts Knative ASGI HTTP requests to MultiCloudEvent
    adapt_cloud_event_request: Converts Knative Cloud Events to MultiCloudEvent

Example:
    Basic usage with Knative serving:

    >>> from multicloud.functions.knative import adapt_asgi_request
    >>> async def my_handler(scope, receive, send):
    ...     event = await adapt_asgi_request(scope, receive)
    ...     # Process the normalized event
    ...     return {"message": f"Received {event.method} request to {event.path}"}
"""

from . import knative

__all__ = ["knative"]
