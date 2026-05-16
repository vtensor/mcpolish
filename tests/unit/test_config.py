"""pyproject.toml loader."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from mcpolish.config.loader import DEFAULT_CONFIG, load_config
from mcpolish.exceptions import ConfigError


def test_default_when_no_pyproject(tmp_path: Path):
    cfg = load_config(tmp_path)
    assert cfg.target_version == DEFAULT_CONFIG.target_version


def test_loads_select_ignore(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(textwrap.dedent('''
        [tool.mcpolish]
        select = ["MP001", "MP010"]
        ignore = ["MP020"]
        line-length = 110
    '''))
    cfg = load_config(tmp_path)
    assert cfg.select == ["MP001", "MP010"]
    assert cfg.ignore == ["MP020"]


def test_per_rule_config(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(textwrap.dedent('''
        [tool.mcpolish]

        [tool.mcpolish.MP010]
        allow = ["search"]
    '''))
    cfg = load_config(tmp_path)
    assert cfg.rules["MP010"]["allow"] == ["search"]


def test_invalid_toml_raises(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("not = valid = toml ===")
    with pytest.raises(ConfigError):
        load_config(tmp_path)
