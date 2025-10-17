import logging


def handler(event):
    logging.info("Handler received event: %s", event)
    
    return event