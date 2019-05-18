import types

import pytest

from class_settings import Settings


def get_settings(settings, *, type):
    if type == "instance":
        return settings()
    elif type == "class":
        return settings
    else:
        raise ValueError(type)


class TestSettings:
    @pytest.fixture(params=["instance", "class"], autouse=True)
    def settings(self, request):
        class TestSettings(Settings):
            DEBUG = True
            CUSTOM = 1

        self.settings = get_settings(TestSettings, type=request.param)

    def test_init(self):
        assert self.settings.DEBUG is True
        assert self.settings.CUSTOM == 1
        assert self.settings.ALLOWED_HOSTS == []

    def test_dir(self):
        assert "DEBUG" in dir(self.settings)
        assert "CUSTOM" in dir(self.settings)
        assert "ALLOWED_HOSTS" in dir(self.settings)

    @pytest.mark.parametrize("settings", ["instance"], indirect=True)
    def test_is_overridden(self):
        assert self.settings.is_overridden("DEBUG")
        assert self.settings.is_overridden("CUSTOM")
        assert not self.settings.is_overridden("ALLOWED_HOSTS")


class TestSettingsInheritance:
    @pytest.mark.parametrize("settings_type", ["instance", "class"])
    def test_single_inheritance(self, settings_type):
        class BaseTestSettings(Settings):
            DEBUG = False
            ALLOWED_HOSTS = ["www.test.com"]

        class TestSettings(BaseTestSettings):
            DEBUG = True
            CUSTOM = 1

            @property
            def ALLOWED_HOSTS(self):
                allowed_hosts = super().ALLOWED_HOSTS.copy()
                allowed_hosts += ["test.test.com"]
                return allowed_hosts

        settings = get_settings(TestSettings, type=settings_type)

        assert settings.DEBUG is True
        assert settings.CUSTOM == 1
        if settings_type == "instance":
            assert settings.ALLOWED_HOSTS == ["www.test.com", "test.test.com"]

    @pytest.mark.parametrize("settings_type", ["instance", "class"])
    def test_multiple_inheritance(self, settings_type):
        class MySettings(Settings):
            DEBUG = False
            ALLOWED_HOSTS = ["www.test.com"]

        class TestSettings(Settings):
            DEBUG = True
            CUSTOM = 1

            @property
            def ALLOWED_HOSTS(self):
                allowed_hosts = super().ALLOWED_HOSTS.copy()
                allowed_hosts += ["test.test.com"]
                return allowed_hosts

        class MyTestSettings(MySettings, TestSettings):
            DEBUG = TestSettings.DEBUG

            @property
            def ALLOWED_HOSTS(self):
                allowed_hosts = super().ALLOWED_HOSTS.copy()
                allowed_hosts += ["my.test.com"]
                return allowed_hosts

        settings = get_settings(MyTestSettings, type=settings_type)

        assert settings.DEBUG is True
        assert settings.CUSTOM == 1
        if settings_type == "instance":
            assert settings.ALLOWED_HOSTS == ["www.test.com", "my.test.com"]


class TestSettingsMeta:
    @pytest.mark.parametrize("settings_type", ["instance", "class"])
    def test_default_settings(self, settings_type):
        class TestSettings(Settings):
            DEBUG = True

            class Meta:
                default_settings = types.SimpleNamespace(DEBUG=False, CUSTOM=1)

        settings = get_settings(TestSettings, type=settings_type)

        assert settings.DEBUG is True
        assert settings.CUSTOM == 1
        assert not hasattr(settings, "ALLOWED_HOSTS")

    @pytest.mark.parametrize("settings_type", ["instance", "class"])
    def test_inject_settings(self, settings_type):
        class BaseTestSettings(Settings):
            DEBUG = True
            CUSTOM = 1

        class TestSettings(BaseTestSettings):
            if CUSTOM:  # noqa
                ALLOWED_HOSTS += ["www.test.com"]  # noqa

            class Meta:
                inject_settings = True

        settings = get_settings(TestSettings, type=settings_type)

        assert settings.DEBUG is True
        assert settings.CUSTOM == 1
        assert settings.ALLOWED_HOSTS == ["www.test.com"]
