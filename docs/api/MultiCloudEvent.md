# MultiCloudEvent

## Overview
`MultiCloudEvent` is a normalized event structure for multi-cloud serverless functions. It provides a consistent interface for handling http requests across different cloud platforms (Knative, AWS Lambda, Azure Functions, Google Cloud Functions, etc.)

## Class Definition
```python
@dataclass
class MultiCloudEvent:
    """
    A normalized event structure for multi-cloud serverless functions
    """
    method: str
    path: str
    headers: Dict[str, str]
    query_string: str = ""
    body: Optional[Union[bytes, str, dict, list]] = None
    source: str = "unknown"
```

## Properties
Core Properties
| Property     | Type             | Description | Default |
| :-------     | :---             | :---------- | :------ |
| method       | str              | HTTP Method (GET, POST, PUT, DELETE, etc.) | Required |
| path         | str              | Request path (e.g., `/api/users`) | Required |
| headers      | `Dict[str, str]` | HTTP Headers as key-value pairs   | Required |
| query_string | str              | Raw query string (e.g., `page=1&limit=10`) | `""` |
| body         | `Union[bytes, str, dict, list, None] | Request body in various formats | `None` |
| source       | str              | Platform identifier (knative, aws, azure, etc.) | `"unknown"` |

## Methods
### Header Operations
### get_header
`get_header(name: str, default: Optional[str] = None) -> Optional[str]`

Get header value case-insensitively.

**Parameters**:
- `name`: Header name to retrieve
- `default`: Default value if header not found

**Returns**: Header value or default

**Example**:
```python
event = MultiCloudEvent(
    method="GET",
    path="/api",
    headers={"Content-Type": "application/json", "Authorization": "Bearer token"}
)

content_type = event.get_header("content-type")  # "application/json"
auth = event.get_header("AUTHORIZATION")         # "Bearer token"  
missing = event.get_header("x-missing", "none")  # "none"
```

### Query Parameter Operations
### get_query_param
`get_query_param(name: str, default: Optional[str] = None) -> Optional[str]`

Extract query parameter by name

**Parameters**:
- `name`: Query parameter to retrieve
- `default`: Default value if query parameter not found

**Returns**: Query parameter value or default

**Example**:
```python
event = MultiCloudEvent(
    method="GET",
    path="/api",
    headers={"Content-Type": "application/json", "Authorization": "Bearer token"},
    query_string="page=1&limit=10"
)

event.get_query_parame("page") # 1
event.get_query_param("limit") # 10
event.get_query_param("name") # "none"
```

### Content Type Checks

### is_json

`is_json() -> bool`

Checks if the request content is JSON

**Returns**: `bool`

**Example**:
```python
event = MultiCloudEvent(
    method="POST",
    path="/api/users",
    headers={"Content-Type": "application/json"},
    body={"name": "John", "age": 30}
)

event.is_json() # True
event.is_xml() # False
```
### is_xml
`is_xml() -> bool`
Checks if the request content is XML

**Returns**: `bool`

**Example**:
```python
event = MultiCloudEvent(
    method="POST",
    path="/api", 
    headers={"Content-Type": "text/xml"},
    body="<user><name>John</name></user>"
)

event.is_xml() # True
event.is_json() # False
```

### is_form_data
`is_form_data() -> bool`
Checks if the request content is x-www-form-urlencoded

**Returns**: `bool`

**Example**:
```python
event = MultiCloudEvent(
    method="POST", 
    path="/api",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    body="name=John&age=30"
)

event.is_form_data() # True
event.is_json() # False
```

### is_multipart
`is_multipart() -> bool`

Checks if the request content is multipart form data

**Returns**: bool

**Example**:
```python
event = MultiCloudEvent(
    method="POST",
    path="/api/upload",
    headers={
        "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        "Content-Length": "1024"
    },
    body=b'------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="username"\r\n\r\nJohn\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="avatar"; filename="profile.jpg"\r\nContent-Type: image/jpeg\r\n\r\n[binary image data]\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--\r\n'
)

event.is_multipart() # True
```

### is_binary
`is_binary() -> bool`

Checks if request content type is binary

**Returns**: bool

**Example**:
```python
event = MultiCloudEvent(
    method="POST",
    path="/api/upload/image",
    headers={"Content-Type": "image/jpeg"},
    body=b'\xff\xd8\xff\xe0\x00\x10JFIF...'  # JPEG binary data
)

event.is_binary() # True
```

### Getters

### get_json
`get_json() -> Optional[Dict[str, Any]]`

Returns the body as a dictionary object

**Returns**: `Dict` or `None`

**Example**:
```python
event = MultiCloudEvent(
    method="POST",
    path="/api/users",
    headers={"Content-Type": "application/json"},
    body={"name": "John", "age": 30}
)

event.get_json() # {'name': 'John', 'age': 30}
```

### get_xml
`get_xml() -> Optional[Dict[str, Any]]`

Returns the body as a dictionary object

**Returns**: `Dict` or `None`

**Example**:
```python
event = MultiCloudEvent(
    method="POST",
    path="/api", 
    headers={"Content-Type": "text/xml"},
    body="<user><name>John</name></user>"
)

event.get_xml() # {'name': 'John'}
```

### get_binary
`get_binary() -> Optional[bytes]`

Returns the raw binary of the body object if it is a binary object.

**Returns**: `bytes` or `None`

**Example**:
```python
event = MultiCloudEvent(
    method="POST",
    path="/api/upload/image",
     headers={"Content-Type": "image/jpeg"},
   body=b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
)

len(event.get_binary()) # 20
```

### get_text
`get_text(encoding: Optional[str] = 'utf-8') -> Optional[str]`
Returns the body object as text decoding from bytes if necessary.

**Parameters**:
- `encoding`: Encoding to use for byte object

**Returns**: `str` or `None`

**Example**:
```python
event = MultiCloudEvent(
    method="POST",
    path="/api/data",
    headers={"Content-Type": "text/plain; charset=utf-8"},
    body=b"Hello World \xe2\x9c\x93"  # UTF-8 encoded bytes with checkmark
)

event.get_text()  # "Hello World ✓"
```

### get_base64
`get_base64() -> Optional[str]

Gets the base64 encoded string of the body if a binary object, or the body if it is a string.

**Returns**: `str` or `None`

**Example**:
```python
event = MultiCloudEvent(
    method="POST",
    path="/api/upload/image",
    headers={"Content-Type": "image/jpeg"},
    body=b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
)

event.get_base64() # "/9j.4AAQSkZJRgABAQEASABIAAA="
```