"""
Unit tests for :mod:`kivymd.utils.asynckivy`.

The scheduler is driven manually with ``Clock.tick`` so no running
application/event loop is needed.
"""

import time

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty

from kivymd.utils import asynckivy


def test_start_completes_coroutine_without_await():
    results = []

    async def coro():
        results.append("ran")

    asynckivy.start(coro())
    # A coroutine that never awaits finishes synchronously.
    assert results == ["ran"]


def test_start_with_sleep_resumes_after_tick():
    results = []

    async def coro():
        value = await asynckivy.sleep(0)
        results.append(value)

    asynckivy.start(coro())
    # Not resumed yet: it is waiting on the scheduled Clock event.
    assert results == []

    # Advance the clock so the scheduled callback fires.
    for _ in range(5):
        if results:
            break
        time.sleep(0.01)
        Clock.tick()

    assert len(results) == 1
    # sleep() returns the elapsed time passed by Clock as first arg.
    assert isinstance(results[0], (int, float))


def test_event_await_resumes_on_dispatch():
    class Dispatcher(EventDispatcher):
        value = NumericProperty(0)

    dispatcher = Dispatcher()
    results = []

    async def coro():
        param = await asynckivy.event(dispatcher, "value")
        results.append(param)

    asynckivy.start(coro())
    assert results == []

    # Changing the property dispatches and resumes the coroutine.
    dispatcher.value = 42
    assert len(results) == 1
    param = results[0]
    # The awaited value is a CallbackParameter with the dispatch args.
    instance, new_value = param.args
    assert instance is dispatcher
    assert new_value == 42


def test_callback_parameter_structure():
    param = asynckivy.CallbackParameter(("a", "b"), {"k": "v"})
    assert param.args == ("a", "b")
    assert param.kwargs == {"k": "v"}
