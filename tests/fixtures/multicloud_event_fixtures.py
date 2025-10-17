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
