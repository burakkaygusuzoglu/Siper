from siper.config import Settings


def test_defaults_point_to_lm_studio():
    settings = Settings()
    assert settings.upstream_base_url == "http://localhost:1235"


def test_env_variable_overrides_default(monkeypatch):
    monkeypatch.setenv("SIPER_UPSTREAM_BASE_URL", "http://example.test:9999")
    assert Settings().upstream_base_url == "http://example.test:9999"
