# Function
import logging
import json

# Import the handler from the same directory
try:
    from .handler import handler
except ImportError:
    try:
        from handler import handler
    except ImportError:
        logging.error("Could not import handler from handler.py")
        handler = None


from multi_cloud.functions.knative import parse_asgi_request

def new():
    """ New is the only method that must be implemented by a Function.
    The instance returned can be of any name.
    """
    return Function()


class Function:
    def __init__(self):
        """ The init method is an optional method where initialization can be
        performed. See the start method for a startup hook which includes
        configuration.
        """

    async def handle(self, scope, receive, send):
        """ Handle all HTTP requests to this Function other than readiness
        and liveness probes."""

        logging.info("Request Received - calling handler")

        try:
            event = await parse_asgi_request(scope, receive)

            # Call your handler function
            if handler:
                result = handler(event)
                logging.info(f"Handler returned: {result}")
                
                # Prepare response
                if isinstance(result, (dict, list)):
                    response_body = json.dumps(result).encode()
                    content_type = b'application/json'
                else:
                    response_body = str(result).encode()
                    content_type = b'text/plain'
            else:
                response_body = b'Handler not available'
                content_type = b'text/plain'

        except Exception as e:
            logging.error(f"Error processing request: {e}")
            response_body = f'Error: {str(e)}'.encode()
            content_type = b'text/plain'

        # Send response
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                [b'content-type', content_type],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': response_body,
        })

    def start(self, cfg):
        """ start is an optional method which is called when a new Function
        instance is started, such as when scaling up or during an update.
        Provided is a dictionary containing all environmental configuration.
        Args:
            cfg (Dict[str, str]): A dictionary containing environmental config.
                In most cases this will be a copy of os.environ, but it is
                best practice to use this cfg dict instead of os.environ.
        """
        logging.info("Function starting")

    def stop(self):
        """ stop is an optional method which is called when a function is
        stopped, such as when scaled down, updated, or manually canceled.  Stop
        can block while performing function shutdown/cleanup operations.  The
        process will eventually be killed if this method blocks beyond the
        platform's configured maximum studown timeout.
        """
        logging.info("Function stopping")

    def alive(self):
        """ alive is an optional method for performing a deep check on your
        Function's liveness.  If removed, the system will assume the function
        is ready if the process is running. This is exposed by default at the
        path /health/liveness.  The optional string return is a message.
        """
        return True, "Alive"

    def ready(self):
        """ ready is an optional method for performing a deep check on your
        Function's readiness.  If removed, the system will assume the function
        is ready if the process is running.  This is exposed by default at the
        path /health/rediness.
        """
        return True, "Ready"