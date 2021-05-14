import pytest
import os
import sys

sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))
sys.path.append("src.project")
from src.project import main, auth, recommender_system, create_app


def test_recommendations():
    ERROR_CODE = -1
    assert recommender_system.songs_dict({'': 0}, 10) != ERROR_CODE


def test_login():
    f_class = auth.login.__class__
    assert isinstance(auth.login, f_class)


def test_signup():
    f_class = auth.signup.__class__
    assert isinstance(auth.signup, f_class)


def test_logout():
    f_class = auth.logout.__class__
    assert isinstance(auth.logout, f_class)


def test_profile():
    f_class = main.profile.__class__
    assert isinstance(main.profile, f_class)


def test_rate():
    f_class = main.rate_get.__class__
    assert isinstance(main.rate_get, f_class)


def test_homepage():
    f_class = main.index.__class__
    assert isinstance(main.index, f_class)


test_recommendations()
test_login()
test_signup()
test_logout()
test_profile()
test_rate()
test_homepage()


