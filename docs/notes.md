# Notes

## Functions
Code at the top of the handler should be parsed into a `start` function that is called by start when cmopiling the code for knative.

## Knative Functions

`scope` - dict
```python
{
    'type': 'http', 
    'http_version': '1.1', 
    'asgi': {
        'spec_version': '2.1', 
        'version': '3.0'
    }, 
    'method': 'PATCH', 
    'scheme': 'http', 
    'path': '/test/2', 
    'raw_path': b'/test/2', 
    'query_string': b'test=Hello&test2=World', 
    'root_path': '', 
    'headers': [
        (b'content-type', b'application/json'), 
        (b'user-agent', b'PostmanRuntime/7.48.0'), 
        (b'accept', b'*/*'), 
        (b'postman-token', b'7cfc9171-e5ec-41e2-815f-08df3f362f09'), 
        (b'host', b'localhost:8080'), 
        (b'accept-encoding', b'gzip, deflate, br'), 
        (b'connection', b'keep-alive'), 
        (b'content-length', b'31')
    ], 
    'client': ('127.0.0.1', 58020), 
    'server': ('127.0.0.1', 8080), 
    'state': {}, 
    'extensions': {}
}
```


`receive` - <class 'method'>
