"""Tests for DupeClean config."""

from dupeclean.config import Config, get_config_path, get_data_path


class TestConfig:
    def test_default_config(self):
        config = Config()
        assert config.scanner.follow_symlinks is False
        assert config.scanner.threads == 4
        assert config.hasher.algorithm == "xxhash"

    def test_default_ignore_patterns(self):
        config = Config()
        assert ".git" in config.scanner.ignore_patterns
        assert "node_modules" in config.scanner.ignore_patterns

    def test_load_nonexistent(self, tmp_path):
        config = Config.load(tmp_path / "nonexistent.toml")
        assert config.scanner.threads == 4

    def test_save_and_load(self, tmp_path):
        config_path = tmp_path / "config.toml"
        config = Config()
        config.scanner.threads = 8
        config.hasher.algorithm = "md5"
        config.save(config_path)
        assert config_path.exists()
        loaded = Config.load(config_path)
        assert loaded.scanner.threads == 8
        assert loaded.hasher.algorithm == "md5"

    def test_save_creates_parent_dirs(self, tmp_path):
        config_path = tmp_path / "a" / "b" / "c" / "config.toml"
        config = Config()
        config.save(config_path)
        assert config_path.exists()


class TestPaths:
    def test_get_config_path(self):
        path = get_config_path()
        assert path is not None
        assert path.name == "config.toml"

    def test_get_data_path(self):
        path = get_data_path()
        assert path is not None
