from ...security import auth
import pytest


def test_should_get_password_hash_work():
    pass

def test_should_verify_password_pass_when_correct_password():
    pass

def test_should_verify_password_fail_when_incorrect_password():
    pass

def test_should_authenticate_user_return_user_when_correct():
    ...

def test_should_authenticate_user_return_false_when_incorrect():
    ...

def test_should_get_current_user_return_user_when_is_auth():
    ...
def test_should_get_current_user_raise_error_when_is_not_auth():
    ...
def test_should_get_current_user_raise_error_when_token_is_expired():
    ...