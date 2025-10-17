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