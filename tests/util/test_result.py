
from util.result import Err, ErrProtocol, Ok, OkProtocol, Result, ResultProtocol


# Functional tests
def test_ok_wraps_value_correctly():
    result = Ok("success")
    assert result.value == "success"
    assert result.to_result().is_ok()
    assert result.to_result().unwrap() == "success"


def test_err_wraps_error_correctly():
    result = Err("failure")
    assert result.error == "failure"
    assert result.to_result().is_err()
    assert result.to_result().unwrap_err() == "failure"


def test_result_ok_behavior():
    result = Result.ok(123)
    assert result.is_ok()
    assert not result.is_err()
    assert result.unwrap() == 123


def test_result_err_behavior():
    result = Result.err("some error")
    assert result.is_err()
    assert not result.is_ok()
    assert result.unwrap_err() == "some error"


# Protocol conformance tests
def test_ok_conforms_to_ok_protocol():
    ok = Ok(42)
    assert isinstance(ok, OkProtocol)
    assert ok.value == 42


def test_err_conforms_to_err_protocol():
    err = Err("boom")
    assert isinstance(err, ErrProtocol)
    assert err.error == "boom"


def test_result_conforms_to_result_protocol_ok():
    result = Result.ok("abc")
    assert isinstance(result, ResultProtocol)
    assert result.is_ok()
    assert result.unwrap() == "abc"


def test_result_conforms_to_result_protocol_err():
    result = Result.err("bad")
    assert isinstance(result, ResultProtocol)
    assert result.is_err()
    assert result.unwrap_err() == "bad"