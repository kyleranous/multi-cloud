"""
Tests for Knative ASGI request adapter
"""

import json
from unittest.mock import AsyncMock

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
        assert result.body is None or result.body == ''
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
        body_bytes = json.dumps(test_data).encode('utf-8')

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
        assert result.body == test_data
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
        full_body = json.dumps(json_data).encode('utf-8')
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
            is_last = (i == len(chunks) - 1)
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
        assert result.body == json_data
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
        assert result.method is None or result.method == 'GET'  # Depends on implementation
        assert result.path is None or result.path == '/'
        assert result.headers == {}
        assert result.query_string == ''
        assert result.source == 'knative'

    @pytest.mark.asyncio
    async def test_receive_exception_handling(self):
        """Test error handling when receive() raises an exception."""
        scope = {
            'type': 'http',
            'method': 'GET',
            'path': '/test',
            'query_string': b'',
            'headers': []
        }

        receive = AsyncMock(side_effect=Exception("Connection lost"))

        result = await adapt_asgi_request(scope, receive)

        # The adapter should handle the exception gracefully
        assert isinstance(result, MultiCloudEvent)
        # The specific error handling depends on your implementation
        # You might want to set error info in headers or have a specific error field

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
