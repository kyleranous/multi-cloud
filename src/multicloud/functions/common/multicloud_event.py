"""
Core Event Classes for Multi-Cloud Functions
"""
from urllib.parse import parse_qs
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class MultiCloudEvent:
    """
    A normalized event structure for multi-cloud serverless functions.
    """
    method: str
    path: str
    headers: Dict[str, str]
    query_string: str = ""
    body: Optional[Union[bytes, str, dict, list]] = None
    source: str = "unknown" # knative, aws-lambda, azure-functions, etc.

    def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get header value case-insensitively.
        """
        name_lower = name.lower()
        for key, value in self.headers.items():
            if key.lower() == name_lower:
                return value
        return default

    def get_query_param(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Extract query parameter by name.
        """
        params = parse_qs(self.query_string)
        return params.get(name, [default])[0]

    def is_json(self) -> bool:
        """Check if request has JSON content type."""
        content_type = self.get_header('content-type', '')
        return ('application/json' in content_type.lower() or 'text/json' in content_type.lower())

    def get_json(self) -> Optional[Dict[str, Any]]:
        """Get body as JSON dict if it's a dict, None otherwise."""
        if isinstance(self.body, dict):
            return self.body
        return None

    def is_binary(self) -> bool:
        """
        Check if the body is binary data.
        """
        return isinstance(self.body, bytes)

    def get_binary(self) -> Optional[bytes]:
        """
        Get body as binary data if it's bytes, None otherwise.
        """
        if isinstance(self.body, bytes):
            return self.body
        return None

    def get_text(self, encoding: str = 'utf-8') -> Optional[str]:
        """Get body as text, decoding from bytes if necessary."""
        if isinstance(self.body, str):
            return self.body
        if isinstance(self.body, bytes):
            try:
                return self.body.decode(encoding)
            except UnicodeDecodeError:
                return None
        return None

    def is_form_data(self) -> bool:
        """Check if request is form data."""
        content_type = self.get_header('content-type', '')
        return 'application/x-www-form-urlencoded' in content_type.lower()

    def is_multipart(self) -> bool:
        """Check if request is multipart form data."""
        content_type = self.get_header('content-type', '')
        return 'multipart/form-data' in content_type.lower()
