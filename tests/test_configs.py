from pathlib import Path
from typing import cast

import pytest
from pydantic import JsonValue

from pre_commit_templates.configs import Configs

this_file = Path(__file__)
repository_root = this_file.parent.parent


@pytest.fixture
def repo_configs(pytestconfig: pytest.Config) -> Configs:
    KEY: str = "configs/repo_configs"
    val: JsonValue | None = cast(
        JsonValue | None,
        pytestconfig.cache.get(KEY, None),  # pyright: ignore[reportUnknownMemberType]
    )

    if val is None:
        res = Configs.from_environment(repository_root)
        pytestconfig.cache.set(KEY, res.model_dump(mode="json"))
        return res
    else:
        return Configs.model_validate(val)


def test_config_dirs_can_be_resolved(repo_configs: Configs) -> None:
    # addresses an older bug where config dirs were not resolved
    _ = repo_configs.resolve_target_directory()
