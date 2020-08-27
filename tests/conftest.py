import pytest


@pytest.fixture
def event_loop():
    try:
        import asyncio

        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
