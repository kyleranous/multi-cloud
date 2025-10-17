"""
Parsers use to normalize event data from Knative to the multi-cloud
event format.
"""
import logging
import json


async def parse_asgi_request(scope, receive) -> dict:
    """ 
    Parse a Knative HTTP Request into a normalized event dictionary.
    """
    try:
        # Receive the request body
        message = await receive()
        body = b''
            
        if message['type'] == 'http.request':
            body = message.get('body', b'')
                
            # Continue receiving if there's more body content
            while message.get('more_body', False):
                message = await receive()
                body += message.get('body', b'')

        # Convert headers from bytes to strings
        headers = {}
        for header_name, header_value in scope.get('headers', []):
            headers[header_name.decode('latin1')] = header_value.decode('latin1')

        # Parse request data
        event = {
            'method': scope.get('method'),
            'path': scope.get('path'),
            'query_string': scope.get('query_string', b'').decode(),
            'headers': headers,
        }

        # Try to parse body as JSON, fallback to string
        try:
            if body:
                body_str = body.decode()
                try:
                    parsed_body = json.loads(body_str)
                    if isinstance(parsed_body, dict):
                        event['body'] = parsed_body
                    else:
                        event['body'] = parsed_body
                except json.JSONDecodeError:
                    event['body'] = body_str
        except Exception as e:
            logging.warning(f"Could not decode body: {e}")
            event['body'] = str(body)
            
        return event
    
    except Exception as e:
        logging.error(f"Error parsing ASGI request: {e}")
        event = {
            'error': str(e)
        }


async def parse_cloud_event(scope, receive) -> dict:
    """ 
    Parse a Knative Cloud Event into a normalized event dictionary.
    """
    pass
