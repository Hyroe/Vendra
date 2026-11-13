from django.conf import settings


def test_custom_user_model_is_configured():
    assert settings.AUTH_USER_MODEL == "accounts.User"


def test_time_is_utc_aware():
    assert settings.TIME_ZONE == "UTC"
    assert settings.USE_TZ is True


def test_drf_uses_json_error_handler():
    assert settings.REST_FRAMEWORK["EXCEPTION_HANDLER"] == "common.exceptions.api_exception_handler"
