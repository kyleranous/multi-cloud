"""
Tests for MultiCloudEvents
"""
from multicloud.functions.common.multicloud_event import MultiCloudEvent


class TestMultiCloudEvent:
    """
    Tests for MultiCloudEvent data class.
    """
    def test_basic_event_creation(self, basic_get_event):
        """
        Test creating a basic MultiCloudEvent.
        """
        event = basic_get_event

        assert event.method == "GET"
        assert event.path == "/test"
        assert event.headers == {"content-type": "application/json"}
        assert event.query_string == ""
        assert event.body is None
        assert event.source == "unknown"

    def test_event_with_all_fields(self):
        """
        Test creating an event with all fields populated.
        """
        event = MultiCloudEvent(
            method="POST",
            path="/api/users",
            headers={"content-type": "application/json", "authorization": "Bearer token123"},
            query_string="limit=10&offset=0",
            body={"name": "John", "age": 30},
            source="knative"
        )

        assert event.method == "POST"
        assert event.path == "/api/users"
        assert event.query_string == "limit=10&offset=0"
        assert event.body == {"name": "John", "age": 30}
        assert event.source == "knative"

    def test_get_header_case_insensitive(self):
        """
        Test get_header method with case-insensitive lookup.
        """
        event = MultiCloudEvent(
            method="GET",
            path="/test",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer token",
                "X-Custom-Header": "custom-value"
            }
        )

        # Test exact case
        assert event.get_header("Content-Type") == "application/json"

        # Test lowercase
        assert event.get_header("content-type") == "application/json"

        # Test uppercase
        assert event.get_header("AUTHORIZATION") == "Bearer token"

        # Test mixed case
        assert event.get_header("x-CuStOm-HeAdEr") == "custom-value"

    def test_get_header_with_default(self, basic_get_event):
        """
        Test get_header method with default value.
        """
        event = basic_get_event

        # Header exists
        assert event.get_header("content-type") == "application/json"

        # Header doesn't exist, no default
        assert event.get_header("authorization") is None

        # Header doesn't exist, with default
        assert event.get_header("authorization", "none") == "none"

    def test_get_query_param_single_value(self):
        """
        Test get_query_param with single parameter values.
        """
        event = MultiCloudEvent(
            method="GET",
            path="/search",
            headers={},
            query_string="q=python&limit=10&active=true"
        )

        assert event.get_query_param("q") == "python"
        assert event.get_query_param("limit") == "10"
        assert event.get_query_param("active") == "true"

    def test_get_query_param_multiple_values(self):
        """
        Test get_query_param with multiple values (returns first).
        """
        event = MultiCloudEvent(
            method="GET",
            path="/search",
            headers={},
            query_string="tags=python&tags=web&tags=api"
        )

        # Should return the first value
        assert event.get_query_param("tags") == "python"

    def test_get_query_param_with_default(self):
        """
        Test get_query_param with default value.
        """
        event = MultiCloudEvent(
            method="GET",
            path="/search",
            headers={},
            query_string="q=python"
        )

        # Parameter exists
        assert event.get_query_param("q") == "python"

        # Parameter doesn't exist, no default
        assert event.get_query_param("limit") is None

        # Parameter doesn't exist, with default
        assert event.get_query_param("limit", "20") == "20"

    def test_get_query_param_empty_query_string(self):
        """
        Test get_query_param with empty query string.
        """
        event = MultiCloudEvent(
            method="GET",
            path="/test",
            headers={}
        )

        assert event.get_query_param("anything") is None
        assert event.get_query_param("anything", "default") == "default"

    def test_is_json_true_cases(self, basic_post_event):
        """
        Test is_json method returns True for JSON content types.
        """
        test_cases = [
            "application/json",
            "application/json; charset=utf-8",
            "Application/JSON",
            "APPLICATION/JSON",
            "text/json"  # Less common but should work
        ]

        for content_type in test_cases:
            basic_post_event.headers['content-type'] = content_type
            assert basic_post_event.is_json(), f"Failed for content-type: {content_type}"

    def test_is_json_false_cases(self, basic_post_event):
        """
        Test is_json method returns False for non-JSON content types.
        """
        test_cases = [
            "text/plain",
            "text/html",
            "application/xml",
            "application/x-www-form-urlencoded",
            "multipart/form-data"
        ]

        for content_type in test_cases:
            basic_post_event.headers['content-type'] = content_type
            assert not basic_post_event.is_json(), f"Failed for content-type: {content_type}"

    def test_is_json_no_content_type_header(self, basic_post_event):
        """
        Test is_json method when no content-type header is present.
        """
        basic_post_event.headers.pop('content-type', None)

        assert not basic_post_event.is_json()

    def test_get_json_with_dict_body(self):
        """
        Test get_json method with dictionary body.
        """
        body_data = {"name": "John", "age": 30, "active": True}
        event = MultiCloudEvent(
            method="POST",
            path="/api",
            headers={"content-type": "application/json"},
            body=body_data
        )

        result = event.get_json()
        assert result == body_data
        assert isinstance(result, dict)

    def test_get_json_with_non_dict_body(self, basic_post_event):
        """
        Test get_json method with non-dictionary body.
        """
        test_cases = [
            "string body",
            123,
            ["list", "body"],
            None
        ]

        for body in test_cases:
            basic_post_event.body = body

            assert basic_post_event.get_json() is None, f"Failed for body: {body}"

    def test_get_json_with_no_body(self):
        """
        Test get_json method when body is None.
        """
        event = MultiCloudEvent(
            method="GET",
            path="/api",
            headers={}
        )

        assert event.get_json() is None

    def test_dataclass_equality(self):
        """
        Test that two identical events are equal.
        """
        event1 = MultiCloudEvent(
            method="GET",
            path="/test",
            headers={"content-type": "application/json"},
            query_string="param=value",
            body={"data": "test"},
            source="knative"
        )

        event2 = MultiCloudEvent(
            method="GET",
            path="/test",
            headers={"content-type": "application/json"},
            query_string="param=value",
            body={"data": "test"},
            source="knative"
        )

        assert event1 == event2

    def test_dataclass_inequality(self, basic_get_event, basic_post_event):
        """
        Test that different events are not equal.
        """
        event1 = basic_get_event

        event2 = basic_post_event

        assert event1 != event2

    def test_repr_and_str(self, basic_get_event):
        """
        Test string representation of the event.
        """
        event = basic_get_event

        # Should not raise any exceptions
        repr_str = repr(event)
        str_str = str(event)

        assert "MultiCloudEvent" in repr_str
        assert "GET" in repr_str
        assert "/test" in repr_str
        assert "GET" in str_str
        assert "/test" in str_str

    def test_is_binary_with_bytes_body(self):
        """
        Test is_binary method with bytes body.
        """
        binary_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'  # PNG header
        event = MultiCloudEvent(
            method="POST",
            path="/upload",
            headers={"content-type": "image/png"},
            body=binary_data
        )

        assert event.is_binary()
        assert event.get_binary() == binary_data
        assert not event.is_json()

    def test_is_binary_with_non_bytes_body(self):
        """
        Test is_binary method with non-bytes body.
        """
        test_cases = [
            "string body",
            {"json": "body"},
            ["list", "body"],
            None
        ]

        for body in test_cases:
            event = MultiCloudEvent(
                method="POST",
                path="/api",
                headers={},
                body=body
            )

            assert not event.is_binary(), f"Failed for body: {body}"
            assert event.get_binary() is None

    def test_get_text_with_string_body(self):
        """
        Test get_text method with string body.
        """
        text_data = "Hello, World!"
        event = MultiCloudEvent(
            method="POST",
            path="/api",
            headers={"content-type": "text/plain"},
            body=text_data
        )

        assert event.get_text() == text_data
        assert event.get_text("utf-8") == text_data

    def test_get_text_with_bytes_body(self):
        """
        Test get_text method with bytes body.
        """
        text_data = "Hello, 世界!"
        bytes_data = text_data.encode('utf-8')

        event = MultiCloudEvent(
            method="POST",
            path="/api",
            headers={"content-type": "text/plain; charset=utf-8"},
            body=bytes_data
        )

        assert event.get_text() == text_data
        assert event.get_text("utf-8") == text_data

    def test_get_text_with_invalid_encoding(self):
        """
        Test get_text method with invalid encoding.
        """
        # Create bytes that can't be decoded as UTF-8
        invalid_utf8 = b'\xff\xfe\x00\x00'

        event = MultiCloudEvent(
            method="POST",
            path="/api",
            headers={"content-type": "application/octet-stream"},
            body=invalid_utf8
        )

        assert event.get_text() is None
        assert event.get_text("utf-8") is None

    def test_get_text_with_non_text_body(self):
        """
        Test get_text method with non-text body.
        """
        test_cases = [
            {"json": "body"},
            ["list", "body"],
            123,
            None
        ]

        for body in test_cases:
            event = MultiCloudEvent(
                method="POST",
                path="/api",
                headers={},
                body=body
            )

            assert event.get_text() is None, f"Failed for body: {body}"

    def test_is_form_data_true_cases(self, basic_post_event):
        """
        Test is_form_data method returns True for form data content types.
        """
        test_cases = [
            "application/x-www-form-urlencoded",
            "application/x-www-form-urlencoded; charset=utf-8",
            "Application/X-WWW-Form-Urlencoded",
            "APPLICATION/X-WWW-FORM-URLENCODED"
        ]

        for content_type in test_cases:
            basic_post_event.headers['content-type'] = content_type
            assert basic_post_event.is_form_data(), f"Failed for content-type: {content_type}"

    def test_is_form_data_false_cases(self, basic_post_event):
        """
        Test is_form_data method returns False for non-form data content types.
        """
        test_cases = [
            "application/json",
            "text/plain",
            "multipart/form-data",
            "application/xml",
            ""
        ]

        for content_type in test_cases:
            basic_post_event.headers['content-type'] = content_type
            assert not basic_post_event.is_form_data(), f"Failed for content-type: {content_type}"

    def test_is_multipart_true_cases(self, basic_post_event):
        """
        Test is_multipart method returns True for multipart content types.
        """
        test_cases = [
            "multipart/form-data",
            "multipart/form-data; boundary=----WebKitFormBoundary",
            "Multipart/Form-Data",
            "MULTIPART/FORM-DATA"
        ]

        for content_type in test_cases:
            basic_post_event.headers['content-type'] = content_type
            assert basic_post_event.is_multipart(), f"Failed for content-type: {content_type}"

    def test_is_multipart_false_cases(self, basic_post_event):
        """
        Test is_multipart method returns False for non-multipart content types.
        """
        test_cases = [
            "application/json",
            "application/x-www-form-urlencoded",
            "text/plain",
            "application/octet-stream",
            ""
        ]

        for content_type in test_cases:
            basic_post_event.headers['content-type'] = content_type
            assert not basic_post_event.is_multipart(), f"Failed for content-type: {content_type}"

    def test_form_data_body_handling(self):
        """
        Test handling of URL-encoded form data body.
        """
        form_data = "name=John+Doe&email=john%40example.com&age=30"
        event = MultiCloudEvent(
            method="POST",
            path="/submit",
            headers={"content-type": "application/x-www-form-urlencoded"},
            body=form_data
        )

        assert event.is_form_data()
        assert not event.is_json()
        assert not event.is_multipart()
        assert event.get_text() == form_data
        assert event.get_json() is None

    def test_multipart_form_data_body_handling(self):
        """
        Test handling of multipart form data body.
        """
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        multipart_body = (
            f'--{boundary}\r\n'
            'Content-Disposition: form-data; name="name"\r\n'
            '\r\n'
            'John Doe\r\n'
            f'--{boundary}\r\n'
            'Content-Disposition: form-data; name="file"; filename="test.txt"\r\n'
            'Content-Type: text/plain\r\n'
            '\r\n'
            'File content here\r\n'
            f'--{boundary}--\r\n'
        )

        event = MultiCloudEvent(
            method="POST",
            path="/upload",
            headers={"content-type": f"multipart/form-data; boundary={boundary}"},
            body=multipart_body
        )

        assert event.is_multipart()
        assert not event.is_json()
        assert not event.is_form_data()
        assert event.get_text() == multipart_body

    def test_binary_file_upload(self):
        """
        Test handling of binary file upload.
        """
        # Simulate a small PNG file
        png_data = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
            b'\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde'
        )

        event = MultiCloudEvent(
            method="POST",
            path="/upload-image",
            headers={
                "content-type": "image/png",
                "content-length": str(len(png_data))
            },
            body=png_data
        )

        assert event.is_binary()
        assert not event.is_json()
        assert not event.is_form_data()
        assert not event.is_multipart()
        assert event.get_binary() == png_data
        assert event.get_text() is None  # Can't decode binary as text

    def test_large_binary_data(self):
        """
        Test handling of larger binary data.
        """
        # Create 1KB of random binary data
        large_binary = bytes(range(256)) * 4

        event = MultiCloudEvent(
            method="POST",
            path="/upload-binary",
            headers={"content-type": "application/octet-stream"},
            body=large_binary
        )

        assert event.is_binary()
        assert len(event.get_binary()) == 1024
        assert event.get_binary() == large_binary

    def test_empty_form_data(self):
        """
        Test handling of empty form data.
        """
        event = MultiCloudEvent(
            method="POST",
            path="/submit",
            headers={"content-type": "application/x-www-form-urlencoded"},
            body=""
        )

        assert event.is_form_data()
        assert event.get_text() == ""
        assert not event.is_binary()

    def test_mixed_content_type_detection(self):
        """
        Test content type detection with various body types.
        """
        # JSON with correct content-type
        json_event = MultiCloudEvent(
            method="POST",
            path="/api",
            headers={"content-type": "application/json"},
            body={"key": "value"}
        )
        assert json_event.is_json()
        assert not json_event.is_form_data()
        assert not json_event.is_multipart()
        assert not json_event.is_binary()

        # Form data with text body
        form_event = MultiCloudEvent(
            method="POST",
            path="/form",
            headers={"content-type": "application/x-www-form-urlencoded"},
            body="key=value"
        )
        assert form_event.is_form_data()
        assert not form_event.is_json()
        assert not form_event.is_multipart()
        assert not form_event.is_binary()

        # Binary data with appropriate content-type
        binary_event = MultiCloudEvent(
            method="POST",
            path="/upload",
            headers={"content-type": "application/pdf"},
            body=b"%PDF-1.4"
        )
        assert binary_event.is_binary()
        assert not binary_event.is_json()
        assert not binary_event.is_form_data()
        assert not binary_event.is_multipart()
