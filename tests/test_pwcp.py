import os
import sys
from io import StringIO
from unittest.mock import patch
from subprocess import STDOUT, CalledProcessError, check_output

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pwcp import main
from pwcp.hooks import is_package


def test_regular_file():
    with patch("sys.stdout", new=StringIO()):
        main(["tests/hello.py"])
        assert sys.stdout.getvalue() == "Hello world! (python)\n"


def test_ppy_file():
    with patch("sys.stdout", new=StringIO()):
        main(["tests/hello.ppy"])
        assert sys.stdout.getvalue() == "Hello world!\n"


def test_run_module():
    with patch("sys.stdout", new=StringIO()):
        main(["-m", "tests.a_module", "1", "2", "3"])
        assert sys.stdout.getvalue() == "b = 6\n"


def test_comments():
    main(["tests/comments.ppy"])


def test_imports():
    main(["tests/test_modules.ppy"])
    assert sys.modules["hello"].__file__ == os.path.join(
        os.path.abspath("tests"), "hello.ppy"
    )
    del sys.modules["hello"]


def test_py_import():
    main(["--prefer-py", "tests/test_modules.ppy"])
    assert sys.modules["hello"].__file__ == os.path.join(
        os.path.abspath("tests"), "hello.py"
    )
    del sys.modules["hello"]


def test_syntax_error():
    with pytest.raises(CalledProcessError) as ctx:
        check_output(
            [sys.executable, "-m", "pwcp", "tests/syntax_error.ppy"],
            stderr=STDOUT,
        )
    assert ctx.value.output.splitlines()[1].strip() == b'print("hello")!'


def test_type_error():
    with pytest.raises(CalledProcessError) as ctx:
        check_output(
            [sys.executable, "-m", "pwcp", "tests/type_error.ppy"],
            stderr=STDOUT,
        )
    assert ctx.value.output.splitlines()[2].strip() == b"print('1' + 1)"


def test_is_package():
    assert is_package("tests") is True
    assert is_package("tests.test_modules") is False
    with pytest.warns(match="Module file or directory not found"):
        assert is_package("inexistent") is False
