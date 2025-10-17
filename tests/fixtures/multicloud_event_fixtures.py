"""
Test Fixtures for MultiCloudEvent Objects.
"""
import pytest
from multicloud.functions.common.multicloud_event import MultiCloudEvent


@pytest.fixture
def basic_get_event():
    """
    Basic GET Request with JSON content-Type.
    """
    return MultiCloudEvent(
        method="GET",
        path="/test",
        headers={"content-type": "application/json"},
    )


@pytest.fixture
def basic_post_event():
    """
    Basic POST Request with JSON content-Type.
    """
    return MultiCloudEvent(
        method="POST",
        path="/api",
        headers={"content-type": "application/json"},
    )


@pytest.fixture
def simple_xml_event():
    """
    Event with simple XML body.
    """
    return MultiCloudEvent(
        method="POST",
        path="/api/users",
        headers={"content-type": "application/xml"},
        body='<user><name>John Doe</name><age>30</age></user>'
    )

@pytest.fixture
def xml_with_attributes_event():
    """
    Event with XML containing attributes.
    """
    return MultiCloudEvent(
        method="POST",
        path="/api/users",
        headers={"content-type": "application/xml"},
        body='<user id="123" active="true"><name>Jane</name></user>'
    )

@pytest.fixture
def nested_xml_event():
    """
    Event with nested XML elements.
    """
    xml_body = '''
    <user>
        <profile>
            <name>John</name>
            <email>john@example.com</email>
        </profile>
        <settings>
            <theme>dark</theme>
        </settings>
    </user>
    '''.strip()

    return MultiCloudEvent(
        method="POST",
        path="/api/users",
        headers={"content-type": "application/xml"},
        body=xml_body
    )


@pytest.fixture
def duplicate_xml_tags_event():
    """Event with duplicate XML tags (creates lists)."""
    xml_body = '''
    <users>
        <user>John</user>
        <user>Jane</user>
        <user>Bob</user>
    </users>
    '''.strip()

    return MultiCloudEvent(
        method="POST",
        path="/api/users",
        headers={"content-type": "application/xml"},
        body=xml_body
    )


@pytest.fixture
def malformed_xml_event():
    """Event with malformed XML."""
    return MultiCloudEvent(
        method="POST",
        path="/api/data",
        headers={"content-type": "application/xml"},
        body='<user><name>John</name><unclosed>'
    )


@pytest.fixture
def json_string_event():
    """Event with JSON as string body."""
    return MultiCloudEvent(
        method="POST",
        path="/api/users",
        headers={"content-type": "application/json"},
        body='{"name": "John", "age": 30, "active": true}'
    )


@pytest.fixture
def malformed_json_event():
    """Event with malformed JSON string."""
    return MultiCloudEvent(
        method="POST",
        path="/api/data",
        headers={"content-type": "application/json"},
        body='{"name": "test", "invalid": json, "missing": quote}'
    )


@pytest.fixture
def png_binary_event():
    """Event with PNG binary data."""
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        b'\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde'
    )
    return MultiCloudEvent(
        method="POST",
        path="/upload",
        headers={"content-type": "image/png"},
        body=png_data
    )


@pytest.fixture
def large_binary_event():
    """Event with large binary data."""
    return MultiCloudEvent(
        method="POST",
        path="/upload-binary",
        headers={"content-type": "application/octet-stream"},
        body=bytes(range(256)) * 4
    )


@pytest.fixture
def form_data_event():
    """Event with URL-encoded form data."""
    return MultiCloudEvent(
        method="POST",
        path="/submit",
        headers={"content-type": "application/x-www-form-urlencoded"},
        body="name=John+Doe&email=john%40example.com&age=30"
    )


@pytest.fixture
def empty_form_event():
    """Event with empty form data."""
    return MultiCloudEvent(
        method="POST",
        path="/submit",
        headers={"content-type": "application/x-www-form-urlencoded"},
        body=""
    )


@pytest.fixture
def plain_text_event():
    """Event with plain text body."""
    return MultiCloudEvent(
        method="POST",
        path="/api",
        headers={"content-type": "text/plain"},
        body="Hello, World!"
    )


@pytest.fixture
def utf8_text_event():
    """Event with UTF-8 encoded text."""
    return MultiCloudEvent(
        method="POST",
        path="/api",
        headers={"content-type": "text/plain; charset=utf-8"},
        body="Hello, 世界!".encode('utf-8')
    )


@pytest.fixture
def invalid_encoding_event():
    """Event with bytes that can't be decoded as UTF-8."""
    return MultiCloudEvent(
        method="POST",
        path="/api",
        headers={"content-type": "application/octet-stream"},
        body=b'\xff\xfe\x00\x00'
    )


@pytest.fixture
def no_content_type_event():
    """Event without content-type header."""
    return MultiCloudEvent(
        method="POST",
        path="/api",
        headers={}
    )


@pytest.fixture
def case_sensitive_headers_event():
    """Event with mixed-case headers for testing case sensitivity."""
    return MultiCloudEvent(
        method="GET",
        path="/test",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
            "X-Custom-Header": "custom-value"
        }
    )


# Parametrized fixtures for content types
@pytest.fixture(params=[
    "application/xml",
    "application/xml; charset=utf-8",
    "text/xml",
    "Application/XML",
    "TEXT/XML"
])
def xml_content_type(request):
    """Various XML content types."""
    return request.param


@pytest.fixture(params=[
    "application/json",
    "text/plain",
    "application/x-www-form-urlencoded",
    "multipart/form-data",
    ""
])
def non_xml_content_type(request):
    """Non-XML content types."""
    return request.param


@pytest.fixture(params=[
    "application/json",
    "application/json; charset=utf-8",
    "Application/JSON",
    "APPLICATION/JSON",
    "text/json"
])
def json_content_type(request):
    """Various JSON content types."""
    return request.param


@pytest.fixture(params=[
    "text/plain",
    "text/html",
    "application/xml",
    "application/x-www-form-urlencoded",
    "multipart/form-data"
])
def non_json_content_type(request):
    """Non-JSON content types."""
    return request.param


@pytest.fixture(params=[
    "string body",
    123,
    ["list", "body"],
    None
])
def non_dict_body(request):
    """Non-dictionary body types."""
    return request.param


@pytest.fixture(params=[
    {"json": "body"},
    ["list", "body"],
    123,
    None
])
def non_text_body(request):
    """Non-text body types."""
    return request.param
