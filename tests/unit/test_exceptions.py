# -*- coding: UTF-8 -*-

import asyncio

from librouteros.exceptions import (
    LibRouterosError,
    RouterAsyncTimeoutError,
    RouterSyncTimeoutError,
    RouterTimeoutError,
    TrapError,
)


def test_TrapError_newlines():
    r"""Assert that string representation replaces \r\n with comma."""
    error = TrapError(message="some\r\n string")
    assert str(error) == "some, string"


def test_RouterTimeoutError_is_base():
    """RouterTimeoutError is the base timeout error, under LibRouterosError."""
    assert issubclass(RouterTimeoutError, LibRouterosError)


def test_RouterAsyncTimeoutError_hierarchy():
    """Async timeout: a RouterTimeoutError and (for back-compat) an asyncio.TimeoutError."""
    assert issubclass(RouterAsyncTimeoutError, RouterTimeoutError)
    assert issubclass(RouterAsyncTimeoutError, asyncio.TimeoutError)


def test_RouterSyncTimeoutError_hierarchy():
    """Sync timeout: a RouterTimeoutError and (for back-compat) an OSError."""
    assert issubclass(RouterSyncTimeoutError, RouterTimeoutError)
    assert issubclass(RouterSyncTimeoutError, OSError)


def test_both_timeouts_caught_by_base():
    """Both concrete timeouts are catchable via the common RouterTimeoutError base."""
    assert issubclass(RouterAsyncTimeoutError, RouterTimeoutError)
    assert issubclass(RouterSyncTimeoutError, RouterTimeoutError)
