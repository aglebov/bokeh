#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2024, Anaconda, Inc., and Bokeh Contributors.
# All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Boilerplate
#-----------------------------------------------------------------------------
from __future__ import annotations # isort:skip

import pytest ; pytest

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
import os
import sys
import webbrowser
from unittest.mock import MagicMock, patch

# Bokeh imports
from tests.support.util.env import envset

# Module under test
import bokeh.util.browser as bub # isort:skip

#-----------------------------------------------------------------------------
# Setup
#-----------------------------------------------------------------------------

_open_args = None

class _RecordingWebBrowser:
    def open(self, *args, **kw):
        global _open_args
        _open_args = args, kw

#-----------------------------------------------------------------------------
# General API
#-----------------------------------------------------------------------------

def test_get_browser_controller_dummy() -> None:
    b = bub.get_browser_controller('none')
    assert isinstance(b, bub.DummyWebBrowser)

def test_get_browser_controller_None() -> None:
    b = bub.get_browser_controller(None)
    assert b == webbrowser

@patch('webbrowser.get')
def test_get_browser_controller_value(mock_get: MagicMock) -> None:
    bub.get_browser_controller('foo')
    assert mock_get.called
    assert mock_get.call_args[0] == ("foo",)
    assert mock_get.call_args[1] == {}

@patch('webbrowser.get')
def test_get_browser_controller_dummy_with_env(mock_get: MagicMock) -> None:
    with envset(BOKEH_BROWSER="bar"):
        bub.get_browser_controller('none')

@patch('webbrowser.get')
def test_get_browser_controller_None_with_env(mock_get: MagicMock) -> None:
    with envset(BOKEH_BROWSER="bar"):
        bub.get_browser_controller()
        assert mock_get.called
        assert mock_get.call_args[0] == ("bar",)
        assert mock_get.call_args[1] == {}

@patch('webbrowser.get')
def test_get_browser_controller_value_with_env(mock_get: MagicMock) -> None:
    with envset(BOKEH_BROWSER="bar"):
        bub.get_browser_controller('foo')
        assert mock_get.called
        assert mock_get.call_args[0] == ("foo",)
        assert mock_get.call_args[1] == {}

def test_view_bad_new() -> None:
    with pytest.raises(RuntimeError) as e:
        bub.view("foo", new="junk") # type: ignore
        assert str(e) == "invalid 'new' value passed to view: 'junk', valid values are: 'same', 'window', or 'tab'"

def test_view_args() -> None:
    db = bub.DummyWebBrowser
    bub.DummyWebBrowser = _RecordingWebBrowser

    # test http locations used as-is
    bub.view("http://foo", browser="none")
    assert _open_args == (('http://foo',), {'autoraise': True, 'new': 0})

    # test non-http locations treated as local files
    bub.view("/foo/bar", browser="none")
    if sys.platform == "win32":
        assert _open_args == (('file://' + os.path.splitdrive(os.getcwd())[0] + '\\foo\\bar',), {'autoraise': True, 'new': 0})
    else:
        assert _open_args == (('file:///foo/bar',), {'autoraise': True, 'new': 0})

    # test autoraise passed to open
    bub.view("http://foo", browser="none", autoraise=False)
    assert _open_args == (('http://foo',), {'autoraise': False, 'new': 0})

    # test handling of new values
    bub.view("http://foo", browser="none", new="same")
    assert _open_args == (('http://foo',), {'autoraise': True, 'new': 0})
    bub.view("http://foo", browser="none", new="window")
    assert _open_args == (('http://foo',), {'autoraise': True, 'new': 1})
    bub.view("http://foo", browser="none", new="tab")
    assert _open_args == (('http://foo',), {'autoraise': True, 'new': 2})

    bub.DummyWebBrowser = db

def test_NEW_PARAM() -> None:
    assert bub.NEW_PARAM == {"same": 0, "window": 1, "tab": 2}

#-----------------------------------------------------------------------------
# Dev API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Private API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------
