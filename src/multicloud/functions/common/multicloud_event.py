"""
Core Event Classes for Multi-Cloud Functions
"""

from urllib.parse import parse_qs
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
import json
import base64
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError


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
    source: str = "unknown"

    def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get header value case-insensitively.
        """
        name_lower = name.lower()
        for key, value in self.headers.items():
            if key.lower() == name_lower:
                return value
        return default

    def get_query_param(
        self, name: str, default: Optional[str] = None
    ) -> Optional[str]:
        """
        Extract query parameter by name.
        """
        params = parse_qs(self.query_string)
        return params.get(name, [default])[0]

    def is_json(self) -> bool:
        """
        Check if request has JSON content type.
        """
        content_type = self.get_header("content-type", "")
        return (
            "application/json" in content_type.lower()
            or "text/json" in content_type.lower()
        )

    def is_xml(self) -> bool:
        """
        Check if request has XML content type.
        """
        content_type = self.get_header("content-type", "")
        return (
            "application/xml" in content_type.lower()
            or "text/xml" in content_type.lower()
        )

    def is_form_data(self) -> bool:
        """
        Check if request is form data.
        """
        content_type = self.get_header("content-type", "")
        return "application/x-www-form-urlencoded" in content_type.lower()

    def is_multipart(self) -> bool:
        """
        Check if request is multipart form data.
        """
        content_type = self.get_header("content-type", "")
        return "multipart/form-data" in content_type.lower()

    def is_binary(self) -> bool:
        """
        Check if the request body is binary data.
        """
        return isinstance(self.body, bytes)

    def get_json(self) -> Optional[Dict[str, Any]]:
        """
        Get body as JSON dict, parsing if necessary.
        """
        # If already parsed as dict, return it
        if isinstance(self.body, dict):
            return self.body

        # If it's a string and content-type indicates JSON, try to parse
        if isinstance(self.body, str) and self.is_json():
            try:
                return json.loads(self.body)
            except json.JSONDecodeError:
                return None

        return None

    def get_xml(self) -> Optional[Dict[str, Any]]:
        """
        Get body as parsed XML dict.
        """
        if isinstance(self.body, str) and self.is_xml():
            try:
                root = ET.fromstring(self.body)
                return self._xml_to_dict(root)
            except ParseError:
                return None
        return None

    def get_binary(self) -> Optional[bytes]:
        """
        Get body as binary data.
        """
        if isinstance(self.body, bytes):
            return self.body
        return None

    def get_text(self, encoding: str = "utf-8") -> Optional[str]:
        """
        Get body as text, decoding from bytes if necessary.
        """
        if isinstance(self.body, str):
            return self.body
        if isinstance(self.body, bytes):
            try:
                return self.body.decode(encoding)
            except UnicodeDecodeError:
                return None
        return None

    def get_base64(self) -> Optional[str]:
        """
        Get binary body as base64 encoded string.
        """
        if isinstance(self.body, bytes):
            return base64.b64encode(self.body).decode("ascii")
        return None

    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """
        Convert XML element to dictionary.
        """
        result = {}

        # Add attributes
        if element.attrib:
            result["@attributes"] = element.attrib

        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:  # No children
                return element.text.strip()
            result["text"] = element.text.strip()

        # Add children
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                # Multiple children with same tag -> make it a list
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data

        return result
