"""
Tests for MultiCloudEvents
"""
import base64
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


class TestMultiCloudHeaders:
    """
    Test for header related functionality in MultiCloudEvent.
    """
    def test_get_header_case_insensitive(self, case_sensitive_headers_event):
        """
        Test get_header method with case-insensitive lookup.
        """
        event = case_sensitive_headers_event

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


class TestMultiCloudQueryParams:
    """
    Test Query Parameter related functionality for MultiCloudEvent.
    """
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


class TestMultiCloudJson:
    """
    Tests for JSON related functionality in MultiCloudEvent.
    """
    def test_is_json_true_cases(self, json_content_type):
        """
        Test is_json method returns True for JSON content types.
        """
        event = MultiCloudEvent(
            method="POST",
            path="/api",
            headers={"content-type": json_content_type}
        )
        assert event.is_json(), f"Failed for content-type: {json_content_type}"

    def test_is_json_false_cases(self, non_json_content_type):
        """
        Test is_json method returns False for non-JSON content types.
        """
        event = MultiCloudEvent(
            method="POST",
            path="/api",
            headers={"content-type": non_json_content_type}
        )
        assert not event.is_json(), f"Failed for content-type: {non_json_content_type}"

    def test_is_json_no_content_type_header(self, no_content_type_event):
        """
        Test is_json method when no content-type header is present.
        """
        assert not no_content_type_event.is_json()

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

    def test_get_json_lazy_parsing(self, json_string_event):
        """
        Test get_json method with lazy parsing from string body.
        """
        result = json_string_event.get_json()
        expected = {"name": "John", "age": 30, "active": True}

        assert result == expected
        assert isinstance(result, dict)

    def test_get_json_with_malformed_json(self, malformed_json_event):
        """
        Test get_json method with malformed JSON string.
        """
        assert malformed_json_event.get_json() is None
        assert malformed_json_event.get_text() is not None  # Should still return as text

    def test_get_json_non_json_content_type(self):
        """
        Test get_json returns None for non-JSON content types.
        """
        event = MultiCloudEvent(
            method="POST",
            path="/api/data",
            headers={"content-type": "text/plain"},
            body='{"name": "test"}'  # Valid JSON but wrong content-type
        )

        assert event.get_json() is None


class TestMultiCloudBinary:
    """
    Tests for Binary related functionality in MultiCloudEvent.
    """
    def test_is_binary_with_bytes_body(self, png_binary_event):
        """
        Test is_binary method with bytes body.
        """
        assert png_binary_event.is_binary()
        assert png_binary_event.get_binary() is not None
        assert not png_binary_event.is_json()

    def test_is_binary_with_non_bytes_body(self, non_dict_body):
        """
        Test is_binary method with non-bytes body.
        """
        event = MultiCloudEvent(
            method="POST",
            path="/api",
            headers={},
            body=non_dict_body
        )

        assert not event.is_binary(), f"Failed for body: {non_dict_body}"
        assert event.get_binary() is None

    def test_get_text_with_string_body(self, plain_text_event):
        """
        Test get_text method with string body.
        """
        assert plain_text_event.get_text() == "Hello, World!"
        assert plain_text_event.get_text("utf-8") == "Hello, World!"

    def test_get_text_with_bytes_body(self, utf8_text_event):
        """
        Test get_text method with bytes body.
        """
        expected = "Hello, 世界!"
        assert utf8_text_event.get_text() == expected
        assert utf8_text_event.get_text("utf-8") == expected

    def test_get_text_with_invalid_encoding(self, invalid_encoding_event):
        """
        Test get_text method with invalid encoding.
        """
        assert invalid_encoding_event.get_text() is None
        assert invalid_encoding_event.get_text("utf-8") is None

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

    def test_binary_file_upload(self, png_binary_event):
        """
        Test handling of binary file upload.
        """
        assert png_binary_event.is_binary()
        assert not png_binary_event.is_json()
        assert not png_binary_event.is_form_data()
        assert not png_binary_event.is_multipart()
        assert png_binary_event.get_binary() is not None
        assert png_binary_event.get_text() is None  # Can't decode binary as text

    def test_large_binary_data(self, large_binary_event):
        """
        Test handling of larger binary data.
        """
        assert large_binary_event.is_binary()
        assert len(large_binary_event.get_binary()) == 1024
        assert large_binary_event.get_binary() == bytes(range(256)) * 4


class TestMultiCloudFormData:
    """
    Tests for Form Data related functionality in MultiCloudEvent.
    """
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

    def test_form_data_body_handling(self, form_data_event):
        """
        Test handling of URL-encoded form data body.
        """
        assert form_data_event.is_form_data()
        assert not form_data_event.is_json()
        assert not form_data_event.is_multipart()
        assert form_data_event.get_text() == "name=John+Doe&email=john%40example.com&age=30"
        assert form_data_event.get_json() is None

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

    def test_empty_form_data(self, empty_form_event):
        """
        Test handling of empty form data.
        """
        assert empty_form_event.is_form_data()
        assert empty_form_event.get_text() == ""
        assert not empty_form_event.is_binary()

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

class TestMultiCloudXml:
    """
    Tests for XML related functionality in MultiCloudEvent.
    """
    def test_is_xml_true_cases(self):
        """
        Test is_xml method returns True for XML content types.
        """
        test_cases = [
            "application/xml",
            "application/xml; charset=utf-8",
            "text/xml",
            "Application/XML",
            "TEXT/XML"
        ]

        for content_type in test_cases:
            event = MultiCloudEvent(
                method="POST",
                path="/api",
                headers={"content-type": content_type}
            )
            assert event.is_xml(), f"Failed for content-type: {content_type}"

    def test_is_xml_false_cases(self):
        """
        Test is_xml method returns False for non-XML content types.
        """
        test_cases = [
            "application/json",
            "text/plain",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            ""
        ]

        for content_type in test_cases:
            event = MultiCloudEvent(
                method="POST",
                path="/api",
                headers={"content-type": content_type}
            )
            assert not event.is_xml(), f"Failed for content-type: {content_type}"

    def test_get_xml_simple(self):
        """
        Test get_xml method with simple XML.
        """
        xml_string = '<user><name>John Doe</name><age>30</age></user>'

        event = MultiCloudEvent(
            method="POST",
            path="/api/users",
            headers={"content-type": "application/xml"},
            body=xml_string
        )

        result = event.get_xml()
        expected = {
            'name': 'John Doe',
            'age': '30'
        }

        assert result == expected
        assert isinstance(result, dict)

    def test_get_xml_with_attributes(self):
        """
        Test get_xml method with XML containing attributes.
        """
        xml_string = '<user id="123" active="true"><name>Jane</name></user>'

        event = MultiCloudEvent(
            method="POST",
            path="/api/users",
            headers={"content-type": "application/xml"},
            body=xml_string
        )

        result = event.get_xml()
        expected = {
            '@attributes': {'id': '123', 'active': 'true'},
            'name': 'Jane'
        }

        assert result == expected

    def test_get_xml_with_nested_elements(self):
        """
        Test get_xml method with nested XML elements.
        """
        xml_string = '''
        <user>
            <profile>
                <name>John</name>
                <email>john@example.com</email>
            </profile>
            <settings>
                <theme>dark</theme>
            </settings>
        </user>
        '''

        event = MultiCloudEvent(
            method="POST",
            path="/api/users",
            headers={"content-type": "application/xml"},
            body=xml_string.strip()
        )

        result = event.get_xml()
        expected = {
            'profile': {
                'name': 'John',
                'email': 'john@example.com'
            },
            'settings': {
                'theme': 'dark'
            }
        }

        assert result == expected

    def test_get_xml_with_duplicate_tags(self):
        """
        Test get_xml method with duplicate XML tags (should create list).
        """
        xml_string = '''
        <users>
            <user>John</user>
            <user>Jane</user>
            <user>Bob</user>
        </users>
        '''

        event = MultiCloudEvent(
            method="POST",
            path="/api/users",
            headers={"content-type": "application/xml"},
            body=xml_string.strip()
        )

        result = event.get_xml()
        expected = {
            'user': ['John', 'Jane', 'Bob']
        }

        assert result == expected

    def test_get_xml_malformed(self):
        """
        Test get_xml method with malformed XML.
        """
        malformed_xml = '<user><name>John</name><unclosed>'

        event = MultiCloudEvent(
            method="POST",
            path="/api/data",
            headers={"content-type": "application/xml"},
            body=malformed_xml
        )

        assert event.get_xml() is None

    def test_get_xml_non_xml_content_type(self):
        """
        Test get_xml returns None for non-XML content types.
        """
        event = MultiCloudEvent(
            method="POST",
            path="/api/data",
            headers={"content-type": "application/json"},
            body='<user><name>test</name></user>'  # Valid XML but wrong content-type
        )

        assert event.get_xml() is None

    def test_get_xml_non_string_body(self):
        """
        Test get_xml returns None for non-string body.
        """
        event = MultiCloudEvent(
            method="POST",
            path="/api/data",
            headers={"content-type": "application/xml"},
            body=b'<user><name>test</name></user>'  # bytes body
        )

        assert event.get_xml() is None

    def test_get_base64_with_binary_data(self):
        """
        Test get_base64 method with binary data.
        """
        binary_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'

        event = MultiCloudEvent(
            method="POST",
            path="/upload",
            headers={"content-type": "image/png"},
            body=binary_data
        )

        result = event.get_base64()

        # Verify it's valid base64 and can be decoded back
        decoded = base64.b64decode(result)
        assert decoded == binary_data
        assert isinstance(result, str)

    def test_get_base64_with_non_binary_body(self):
        """
        Test get_base64 returns None for non-binary body.
        """
        event = MultiCloudEvent(
            method="POST",
            path="/api",
            headers={"content-type": "text/plain"},
            body="text content"
        )

        assert event.get_base64() is None

    def test_enhanced_get_text_with_dict_body(self):
        """
        Test get_text returns None for dict body.
        """
        event = MultiCloudEvent(
            method="POST",
            path="/api",
            headers={"content-type": "application/json"},
            body={"name": "test"}
        )

        assert event.get_text() is None

    def test_enhanced_get_text_with_list_body(self):
        """
        Test get_text returns None for list body.
        """
        event = MultiCloudEvent(
            method="POST",
            path="/api",
            headers={"content-type": "application/json"},
            body=["item1", "item2"]
        )

        assert event.get_text() is None

    def test_content_type_case_sensitivity(self):
        """
        Test that all content-type checks are case insensitive.
        """
        event = MultiCloudEvent(
            method="POST",
            path="/api",
            headers={"Content-Type": "APPLICATION/JSON; CHARSET=UTF-8"},
            body='{"test": true}'
        )

        assert event.is_json()
        assert not event.is_xml()
        assert not event.is_form_data()
        assert not event.is_multipart()

        # Test XML case insensitivity
        event.headers["Content-Type"] = "TEXT/XML"
        assert not event.is_json()
        assert event.is_xml()

    def test_multiple_content_parsing_methods(self):
        """
        Test that an event can be accessed via multiple methods.
        """
        json_string = '{"name": "John", "age": 30}'

        event = MultiCloudEvent(
            method="POST",
            path="/api/users",
            headers={"content-type": "application/json"},
            body=json_string
        )

        # Should work as both JSON and text
        json_data = event.get_json()
        text_data = event.get_text()

        assert json_data == {"name": "John", "age": 30}
        assert text_data == json_string
        assert event.get_binary() is None  # Not binary
        assert event.get_base64() is None  # Not binary
