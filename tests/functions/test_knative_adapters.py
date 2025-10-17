"""
Tests for Knative ASGI request adapter
"""

import json
import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from multicloud.functions.knative.adapters import adapt_asgi_request
from multicloud.functions.common.multicloud_event import MultiCloudEvent


class TestAdaptAsgiRequest:
    """
    Tests for Knative ASGI request adapter.
    """
    @pytest.mark.asyncio
    async def test_basic_get_request(self):
        """Test a basic GET request with no body."""
        scope = {
            'type': 'http',
            'method': 'GET',
            'path': '/api/users',
            'query_string': b'page=1&limit=10',
            'headers': [
                (b'accept', b'application/json'),
                (b'user-agent', b'test-client/1.0'),
                (b'host', b'localhost:8080'),
            ]
        }

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': b'',
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'GET'
        assert result.path == '/api/users'
        assert result.query_string == 'page=1&limit=10'
        assert result.headers['accept'] == 'application/json'
        assert result.headers['user-agent'] == 'test-client/1.0'
        assert result.headers['host'] == 'localhost:8080'
        assert result.body is None  # Empty body should be None
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_post_request_with_json_body(self):
        """Test POST request with JSON body."""
        test_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'age': 30,
            'active': True
        }
        json_string = json.dumps(test_data)
        body_bytes = json_string.encode('utf-8')

        scope = {
            'type': 'http',
            'method': 'POST',
            'path': '/api/users',
            'query_string': b'',
            'headers': [
                (b'content-type', b'application/json'),
                (b'content-length', str(len(body_bytes)).encode()),
                (b'authorization', b'Bearer token123'),
            ]
        }

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': body_bytes,
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'POST'
        assert result.path == '/api/users'
        assert result.headers['content-type'] == 'application/json'
        assert result.headers['authorization'] == 'Bearer token123'
        # Body should be string now, JSON parsing happens via get_json()
        assert result.body == json_string
        assert result.is_json() is True
        assert result.get_json() == test_data
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_url_encoded_form_data(self):
        """Test POST request with URL-encoded form data."""
        form_data = 'name=Jane+Smith&email=jane%40example.com&subscribe=true&age=25'
        body_bytes = form_data.encode('utf-8')

        scope = {
            'type': 'http',
            'method': 'POST',
            'path': '/api/contact',
            'query_string': b'',
            'headers': [
                (b'content-type', b'application/x-www-form-urlencoded'),
                (b'content-length', str(len(body_bytes)).encode()),
            ]
        }

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': body_bytes,
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'POST'
        assert result.path == '/api/contact'
        assert result.headers['content-type'] == 'application/x-www-form-urlencoded'
        assert result.body == form_data
        assert result.is_form_data() is True
        assert result.is_json() is False
        assert result.get_text() == form_data
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_multipart_form_data(self):
        """Test POST request with multipart form data."""
        boundary = 'boundary123456789'
        multipart_body = (
            f'--{boundary}\r\n'
            'Content-Disposition: form-data; name="username"\r\n'
            '\r\n'
            'testuser\r\n'
            f'--{boundary}\r\n'
            'Content-Disposition: form-data; name="avatar"; filename="profile.jpg"\r\n'
            'Content-Type: image/jpeg\r\n'
            '\r\n'
            'fake-image-data-here\r\n'
            f'--{boundary}--\r\n'
        )
        body_bytes = multipart_body.encode('utf-8')

        scope = {
            'type': 'http',
            'method': 'POST',
            'path': '/api/upload',
            'query_string': b'',
            'headers': [
                (b'content-type', f'multipart/form-data; boundary={boundary}'.encode()),
                (b'content-length', str(len(body_bytes)).encode()),
            ]
        }

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': body_bytes,
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'POST'
        assert result.path == '/api/upload'
        assert result.headers['content-type'].startswith('multipart/form-data')
        assert result.body == multipart_body
        assert result.is_multipart() is True
        assert result.is_json() is False
        assert result.get_text() == multipart_body
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_binary_file_upload(self):
        """Test POST request with binary file data."""
        # Simulate a small PNG file header
        png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10'
        binary_data = png_header + b'\x00' * 100  # Add some padding

        scope = {
            'type': 'http',
            'method': 'POST',
            'path': '/api/files',
            'query_string': b'filename=test.png',
            'headers': [
                (b'content-type', b'image/png'),
                (b'content-length', str(len(binary_data)).encode()),
                (b'x-file-name', b'test.png'),
            ]
        }

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': binary_data,
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'POST'
        assert result.path == '/api/files'
        assert result.query_string == 'filename=test.png'
        assert result.headers['content-type'] == 'image/png'
        assert result.headers['x-file-name'] == 'test.png'
        # Binary data should remain as bytes (not converted to string)
        assert result.body == binary_data
        assert result.is_binary() is True
        assert result.is_json() is False
        assert result.get_binary() == binary_data
        assert len(result.get_binary()) == len(binary_data)
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_chunked_body_reception(self):
        """Test receiving body in multiple chunks."""
        json_data = {'message': 'This is a longer message that might be chunked'}
        json_string = json.dumps(json_data)
        full_body = json_string.encode('utf-8')
        chunk_size = 20

        scope = {
            'type': 'http',
            'method': 'POST',
            'path': '/api/messages',
            'query_string': b'',
            'headers': [
                (b'content-type', b'application/json'),
                (b'transfer-encoding', b'chunked'),
            ]
        }

        # Split the body into chunks
        chunks = [full_body[i:i+chunk_size] for i in range(0, len(full_body), chunk_size)]

        # Mock receiving in chunks
        receive_calls = []
        for i, chunk in enumerate(chunks):
            is_last = i == len(chunks) - 1
            receive_calls.append({
                'type': 'http.request',
                'body': chunk,
                'more_body': not is_last
            })

        receive = AsyncMock(side_effect=receive_calls)

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'POST'
        assert result.path == '/api/messages'
        # Body should be the JSON string, get_json() parses it
        assert result.body == json_string
        assert result.is_json() is True
        assert result.get_json() == json_data
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_plain_text_body(self):
        """Test POST request with plain text body."""
        text_content = "This is plain text content for testing purposes."
        body_bytes = text_content.encode('utf-8')

        scope = {
            'type': 'http',
            'method': 'PUT',
            'path': '/api/notes/123',
            'query_string': b'',
            'headers': [
                (b'content-type', b'text/plain'),
                (b'content-length', str(len(body_bytes)).encode()),
            ]
        }

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': body_bytes,
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'PUT'
        assert result.path == '/api/notes/123'
        assert result.headers['content-type'] == 'text/plain'
        assert result.body == text_content
        assert result.is_json() is False
        assert result.is_binary() is False
        assert result.get_text() == text_content
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_malformed_json_fallback(self):
        """Test handling of malformed JSON (should fallback to string)."""
        malformed_json = '{"name": "test", "invalid": json, "missing": quote}'
        body_bytes = malformed_json.encode('utf-8')

        scope = {
            'type': 'http',
            'method': 'POST',
            'path': '/api/data',
            'query_string': b'',
            'headers': [
                (b'content-type', b'application/json'),
            ]
        }

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': body_bytes,
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'POST'
        assert result.path == '/api/data'
        assert result.body == malformed_json  # Should be string, not parsed JSON
        assert result.is_json() is True  # Content-type still indicates JSON
        assert result.get_json() is None  # But parsing returns None
        assert result.get_text() == malformed_json
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_empty_scope_handling(self):
        """Test adapter with minimal/missing scope data."""
        scope = {}  # Empty scope

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': b'',
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        # Check for default values from your adapter implementation
        assert result.method == 'GET'  # Default method
        assert result.path == '/'  # Default path
        assert result.headers == {}
        assert result.query_string == ''
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_unicode_content(self):
        """Test handling of unicode content in different encodings."""
        unicode_text = "Hello 世界! 🌍 Ñoño café"
        body_bytes = unicode_text.encode('utf-8')

        scope = {
            'type': 'http',
            'method': 'POST',
            'path': '/api/unicode',
            'query_string': b'',
            'headers': [
                (b'content-type', b'text/plain; charset=utf-8'),
            ]
        }

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': body_bytes,
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'POST'
        assert result.path == '/api/unicode'
        assert result.body == unicode_text
        assert result.get_text() == unicode_text
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_xml_content_handling(self):
        """Test handling of XML content."""
        xml_content = '<user><name>John</name><age>30</age></user>'
        body_bytes = xml_content.encode('utf-8')

        scope = {
            'type': 'http',
            'method': 'POST',
            'path': '/api/xml',
            'query_string': b'',
            'headers': [
                (b'content-type', b'application/xml'),
            ]
        }

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': body_bytes,
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'POST'
        assert result.path == '/api/xml'
        assert result.body == xml_content
        assert result.is_xml() is True
        assert result.is_json() is False
        assert result.get_text() == xml_content
        # Test XML parsing
        xml_data = result.get_xml()
        assert xml_data is not None
        assert xml_data['name'] == 'John'
        assert xml_data['age'] == '30'
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """
        Test handling of connection errors during receive.
        """
        scope = {
            'type': 'http',
            'method': 'POST',
            'path': '/api/test',
            'headers': [(b'content-type', b'application/json')]
        }

        # Mock receive to raise ConnectionError
        receive = AsyncMock(side_effect=ConnectionError("Connection lost"))

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'POST'
        assert result.path == '/api/test'
        assert 'x-error' in result.headers
        assert 'Connection error' in result.headers['x-error']
        assert result.query_string == ''
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self):
        """Test handling of timeout errors during receive."""
        scope = {
            'type': 'http',
            'method': 'GET',
            'path': '/api/timeout',
            'headers': []
        }

        # Mock receive to raise TimeoutError
        receive = AsyncMock(side_effect=asyncio.TimeoutError("Request timeout"))

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'GET'
        assert result.path == '/api/timeout'
        assert 'x-error' in result.headers
        assert 'Connection error' in result.headers['x-error']
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_unicode_decode_error_in_headers(self):
        """
        Test handling of UnicodeDecodeError in header processing.
        """
        scope = {
            'type': 'http',
            'method': 'POST',
            'path': '/api/test',
            'headers': [
                (b'content-type', b'application/json'),
                (b'invalid-header', b'\xff\xfe\x00\x00')  # Invalid UTF-8 bytes
            ]
        }

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': b'{"test": "data"}',
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'POST'
        assert result.path == '/api/test'
        assert 'x-error' in result.headers
        assert 'Encoding error' in result.headers['x-error']
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_unicode_decode_error_in_query_string(self):
        """Test handling of UnicodeDecodeError in query string processing."""
        scope = {
            'type': 'http',
            'method': 'GET',
            'path': '/api/test',
            'query_string': b'\xff\xfe\x00\x00',  # Invalid UTF-8 bytes
            'headers': []
        }

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': b'',
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'GET'
        assert result.path == '/api/test'
        assert 'x-error' in result.headers
        assert 'Encoding error' in result.headers['x-error']
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_key_error_handling(self):
        """Test handling of KeyError when required scope keys are missing."""
        # Create a mock scope that will cause KeyError when accessed
        scope = Mock()
        scope.get = Mock(side_effect=KeyError("Required key missing"))

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': b'',
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'GET'  # Default value
        assert result.path == '/'  # Default value
        assert 'x-error' in result.headers
        assert 'Missing key' in result.headers['x-error']
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_receive_message_not_http_request(self):
        """Test handling when receive message is not http.request type."""
        scope = {
            'type': 'http',
            'method': 'GET',
            'path': '/api/test',
            'headers': []
        }

        # Return a different message type
        receive = AsyncMock(return_value={
            'type': 'http.disconnect',  # Not http.request
            'body': b'should not be processed'
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'GET'
        assert result.path == '/api/test'
        assert result.body is None  # No body should be processed
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_missing_scope_defaults(self):
        """Test adapter behavior with missing scope keys (uses defaults)."""
        # Minimal scope with missing optional keys
        scope = {
            'type': 'http'
            # Missing method, path, query_string, headers
        }

        receive = AsyncMock(return_value={
            'type': 'http.request',
            'body': b'test',
            'more_body': False
        })

        result = await adapt_asgi_request(scope, receive)

        assert isinstance(result, MultiCloudEvent)
        assert result.method == 'GET'  # Default
        assert result.path == '/'  # Default
        assert result.headers == {}  # Default (empty dict)
        assert result.query_string == ''  # Default
        assert result.body == b'test'  # Should still process body as binary (no content-type)
        assert result.source == 'knative'
