"""
Tests for GlobalVariableStore.

Unit tests verifying the core functionality of the global variable store:
set/get/has/get_all, subscribe/unsubscribe, remove, and clear.
"""

from __future__ import annotations

import pytest
from calc_session import GlobalVariableStore


class TestGlobalVariableStoreBasic:
    """Unit tests for basic get/set/has/get_all operations."""

    def test_set_and_get(self):
        store = GlobalVariableStore()
        store.set("x", 42)
        assert store.get("x") == 42

    def test_get_nonexistent_returns_default(self):
        store = GlobalVariableStore()
        assert store.get("missing") is None
        assert store.get("missing", 0) == 0

    def test_has_existing_variable(self):
        store = GlobalVariableStore()
        store.set("pi", 3.14)
        assert store.has("pi") is True

    def test_has_nonexistent_variable(self):
        store = GlobalVariableStore()
        assert store.has("nope") is False

    def test_get_all_empty(self):
        store = GlobalVariableStore()
        assert store.get_all() == {}

    def test_get_all_returns_copy(self):
        store = GlobalVariableStore()
        store.set("a", 1)
        store.set("b", 2)
        all_vars = store.get_all()
        assert all_vars == {"a": 1, "b": 2}
        # Modifying the returned dict should not affect the store
        all_vars["c"] = 3
        assert not store.has("c")

    def test_set_overwrites_existing(self):
        store = GlobalVariableStore()
        store.set("x", 10)
        store.set("x", 20)
        assert store.get("x") == 20

    def test_set_various_types(self):
        store = GlobalVariableStore()
        store.set("int_val", 100)
        store.set("float_val", 3.14)
        store.set("str_val", "hello")
        store.set("list_val", [1, 2, 3])
        assert store.get("int_val") == 100
        assert store.get("float_val") == 3.14
        assert store.get("str_val") == "hello"
        assert store.get("list_val") == [1, 2, 3]


class TestGlobalVariableStoreSubscribe:
    """Unit tests for subscribe/unsubscribe and listener notification."""

    def test_subscribe_notified_on_set(self):
        store = GlobalVariableStore()
        notifications = []
        store.subscribe(lambda name, value: notifications.append((name, value)))
        store.set("x", 42)
        assert notifications == [("x", 42)]

    def test_multiple_subscribers(self):
        store = GlobalVariableStore()
        log1 = []
        log2 = []
        store.subscribe(lambda n, v: log1.append((n, v)))
        store.subscribe(lambda n, v: log2.append((n, v)))
        store.set("y", 99)
        assert log1 == [("y", 99)]
        assert log2 == [("y", 99)]

    def test_unsubscribe_stops_notifications(self):
        store = GlobalVariableStore()
        notifications = []
        callback = lambda name, value: notifications.append((name, value))
        store.subscribe(callback)
        store.set("a", 1)
        store.unsubscribe(callback)
        store.set("b", 2)
        assert notifications == [("a", 1)]

    def test_unsubscribe_nonexistent_callback_is_safe(self):
        store = GlobalVariableStore()
        callback = lambda name, value: None
        # Should not raise
        store.unsubscribe(callback)

    def test_subscribe_same_callback_twice_only_registers_once(self):
        store = GlobalVariableStore()
        notifications = []
        callback = lambda name, value: notifications.append((name, value))
        store.subscribe(callback)
        store.subscribe(callback)
        store.set("x", 1)
        # Should only be notified once
        assert notifications == [("x", 1)]

    def test_subscriber_receives_name_and_value(self):
        store = GlobalVariableStore()
        received = {}

        def on_change(name, value):
            received[name] = value

        store.subscribe(on_change)
        store.set("pi", 3.14159)
        store.set("e", 2.71828)
        assert received == {"pi": 3.14159, "e": 2.71828}


class TestGlobalVariableStoreRemove:
    """Unit tests for remove() method."""

    def test_remove_existing_variable(self):
        store = GlobalVariableStore()
        store.set("x", 10)
        store.remove("x")
        assert not store.has("x")
        assert store.get("x") is None

    def test_remove_nonexistent_variable_is_safe(self):
        store = GlobalVariableStore()
        # Should not raise
        store.remove("nonexistent")

    def test_remove_notifies_listeners_with_none(self):
        store = GlobalVariableStore()
        notifications = []
        store.subscribe(lambda n, v: notifications.append((n, v)))
        store.set("x", 42)
        store.remove("x")
        assert notifications == [("x", 42), ("x", None)]

    def test_remove_does_not_notify_if_not_exists(self):
        store = GlobalVariableStore()
        notifications = []
        store.subscribe(lambda n, v: notifications.append((n, v)))
        store.remove("ghost")
        assert notifications == []


class TestGlobalVariableStoreClear:
    """Unit tests for clear() method."""

    def test_clear_removes_all_variables(self):
        store = GlobalVariableStore()
        store.set("a", 1)
        store.set("b", 2)
        store.set("c", 3)
        store.clear()
        assert store.get_all() == {}
        assert not store.has("a")
        assert not store.has("b")
        assert not store.has("c")

    def test_clear_notifies_for_each_variable(self):
        store = GlobalVariableStore()
        notifications = []
        store.set("x", 10)
        store.set("y", 20)
        store.subscribe(lambda n, v: notifications.append((n, v)))
        store.clear()
        # Should notify for each removed variable with None
        assert ("x", None) in notifications
        assert ("y", None) in notifications
        assert len(notifications) == 2

    def test_clear_empty_store_is_safe(self):
        store = GlobalVariableStore()
        notifications = []
        store.subscribe(lambda n, v: notifications.append((n, v)))
        store.clear()
        assert notifications == []
