import pytest

from class_settings import Env, Settings


@pytest.fixture
def env(request, monkeypatch):
    for name, value in request.param.items():
        monkeypatch.setenv(name, value)
    return Env()


class TestEnv:
    @pytest.mark.parametrize(
        "env", [{"DJANGO_SECRET_KEY": "test", "DJANGO_CUSTOM": "1"}], indirect=True
    )
    def test_env(self, env):
        class TestSettings(Settings):
            SECRET_KEY = env("SECRET_KEY")
            CUSTOM = env("CUSTOM")

        settings = TestSettings()

        assert settings.SECRET_KEY == "test"
        assert settings.CUSTOM == "1"

    @pytest.mark.parametrize("env", [{"DJANGO_SECRET_KEY": "test"}], indirect=True)
    def test_env_default(self, env):
        class TestSettings(Settings):
            SECRET_KEY = env("SECRET_KEY", default="abc")
            CUSTOM = env("CUSTOM", default=1)

        settings = TestSettings()

        assert settings.SECRET_KEY == "test"
        assert settings.CUSTOM == 1

    @pytest.mark.parametrize(
        "env", [{"DJANGO_SECRET_KEY": "test", "CUSTOMCUSTOM": "1"}], indirect=True
    )
    def test_env_prefix(self, env):
        class TestSettings(Settings):
            SECRET_KEY = env("SECRET_KEY", prefix="DJANGO_")
            CUSTOM = env("CUSTOM", prefix="CUSTOM")

        settings = TestSettings()

        assert settings.SECRET_KEY == "test"
        assert settings.CUSTOM == "1"

    @pytest.mark.parametrize(
        "env", [{"DJANGO_SECRET_KEY": "test", "DJANGO_CUSTOM": "1"}], indirect=True
    )
    def test_env_deferred(self, env):
        class TestSettings(Settings):
            SECRET_KEY = env()
            CUSTOM = env()

        settings = TestSettings()

        assert settings.SECRET_KEY == "test"
        assert settings.CUSTOM == "1"

    @pytest.mark.parametrize("env", [{"DJANGO_SECRET_KEY": "test"}], indirect=True)
    def test_env_optional(self, env):
        class TestSettings(Settings):
            SECRET_KEY = env("SECRET_KEY", optional=True)
            CUSTOM = env("CUSTOM", optional=True)

        settings = TestSettings()

        assert settings.SECRET_KEY == "test"
        assert not hasattr(settings, "CUSTOM")

    @pytest.mark.parametrize(
        "env",
        [{"DJANGO_SECRET_KEY": "test", "DJANGO_CUSTOMCUSTOM": "1"}],
        indirect=True,
    )
    def test_env_prefixed(self, env):
        class TestSettings(Settings):
            with env.prefixed("DJANGO_"):
                SECRET_KEY = env("SECRET_KEY")
                with env.prefixed("CUSTOM"):
                    CUSTOM = env("CUSTOM")

        settings = TestSettings()

        assert settings.SECRET_KEY == "test"
        assert settings.CUSTOM == "1"

    @pytest.mark.parametrize("env", [{"DJANGO_CUSTOM": "custom"}], indirect=True)
    def test_env_parser(self, env):
        @env.parser
        def custom(value, custom=False):
            return custom and value == "custom"

        class TestSettings(Settings):
            CUSTOM = env.custom("CUSTOM", custom=True)

        settings = TestSettings()

        assert settings.CUSTOM is True


class TestEnvParsers:
    @pytest.mark.parametrize(
        "env",
        [{"DJANGO_INT": "1", "DJANGO_FLOAT": "1.5", "DJANGO_COMPLEX": "1+2j"}],
        indirect=True,
    )
    def test_numeric(self, env):
        class TestSettings(Settings):
            INT = env.int("INT")
            FLOAT = env.float("FLOAT")
            COMPLEX = env.complex("COMPLEX")

        settings = TestSettings()

        assert settings.INT == 1
        assert settings.FLOAT == 1.5
        assert settings.COMPLEX == 1 + 2j

    @pytest.mark.parametrize(
        "env",
        [{"DJANGO_LIST": "test, abc", "DJANGO_TUPLE": "test, abc"}],
        indirect=True,
    )
    def test_sequence(self, env):
        class TestSettings(Settings):
            LIST = env.list("LIST")
            TUPLE = env.tuple("TUPLE")

        settings = TestSettings()

        assert settings.LIST == ["test", "abc"]
        assert settings.TUPLE == ("test", "abc")

    @pytest.mark.parametrize("env", [{"DJANGO_STR": "test"}], indirect=True)
    def test_text_sequence(self, env):
        class TestSettings(Settings):
            STR = env.str("STR")

        settings = TestSettings()

        assert settings.STR == "test"

    @pytest.mark.parametrize(
        "env", [{"DJANGO_BYTES": "test", "DJANGO_BYTEARRAY": "test"}], indirect=True
    )
    def test_binary_sequence(self, env):
        class TestSettings(Settings):
            BYTES = env.bytes("BYTES", encoding="ascii")
            BYTEARRAY = env.bytearray("BYTEARRAY", encoding="ascii")

        settings = TestSettings()

        assert settings.BYTES == b"test"
        assert settings.BYTEARRAY == bytearray(b"test")

    @pytest.mark.parametrize(
        "env",
        [{"DJANGO_SET": "test, abc", "DJANGO_FROZENSET": "test, abc"}],
        indirect=True,
    )
    def test_set(self, env):
        class TestSettings(Settings):
            SET = env.set("SET")
            FROZENSET = env.frozenset("FROZENSET")

        settings = TestSettings()

        assert settings.SET == {"test", "abc"}
        assert settings.FROZENSET == frozenset({"test", "abc"})

    @pytest.mark.parametrize("env", [{"DJANGO_DICT": "test = abc"}], indirect=True)
    def test_mapping(self, env):
        class TestSettings(Settings):
            DICT = env.dict("DICT")

        settings = TestSettings()

        assert settings.DICT == {"test": "abc"}

    @pytest.mark.parametrize("env", [{"DJANGO_BOOL": "true"}], indirect=True)
    def test_other(self, env):
        class TestSettings(Settings):
            BOOL = env.bool("BOOL")

        settings = TestSettings()

        assert settings.BOOL is True

    @pytest.mark.parametrize("env", [{"DJANGO_JSON": '{"test": "abc"}'}], indirect=True)
    def test_custom(self, env):
        class TestSettings(Settings):
            JSON = env.json("JSON")

        settings = TestSettings()

        assert settings.JSON == {"test": "abc"}


class TestEnvMeta:
    @pytest.mark.parametrize(
        "env", [{"CUSTOM_SECRET_KEY": "test", "CUSTOM_CUSTOM": "1"}], indirect=True
    )
    def test_env_prefix(self, env):
        class TestSettings(Settings):
            SECRET_KEY = env("SECRET_KEY")
            CUSTOM = env("CUSTOM")

            class Meta:
                env_prefix = "CUSTOM_"

        settings = TestSettings()

        assert settings.SECRET_KEY == "test"
        assert settings.CUSTOM == "1"
