import tomllib
from functools import cache
from pathlib import Path

from pydantic import BaseModel, Field, JsonValue, PrivateAttr

from .git import get_root

__all__ = ["Configs", "ConfigParseError"]


class ConfigParseError(RuntimeError): ...


def read_pyproject_config[T](
    path: Path, key: str = "pre_commit_templates", default: T = None
) -> dict[str, JsonValue] | T:
    """
    Read a dictionary from the given `pyproject.toml` path, if it exists.
    """
    if not path.exists():
        return default

    with open(path, mode="rb") as file:
        data: JsonValue = tomllib.load(file)

    res = data.get("tool", None)

    if res is None:
        return default

    if not isinstance(res, dict):
        raise ConfigParseError("tool section in pyproject.toml should be a dictionary")

    res = res.get(key, None)

    if res is None:
        return default
    elif isinstance(res, dict):
        return res

    raise ConfigParseError(
        f"unexpected value while parsing pyproject.toml: "
        f"`[tool.{key}]` should be a dict or None. "
        f"reading `{type(res)}` instead."
    )


class Configs(BaseModel):
    data: dict[str, JsonValue] = Field(default_factory=dict)
    """Data for the jinja2 environment."""
    template_directory: str = Field(default="./templates")
    """Directory to get templates from. Defined relative to the root directory of the repository."""
    target_directory: str = Field(default="./")
    """Directory to apply templates into. Defined relative to the root directory of the repository."""

    _repository_root: Path = PrivateAttr()

    @cache
    def resolve_template_directory(self) -> Path:
        return (self._repository_root / self.template_directory).resolve()

    @cache
    def resolve_target_directory(self) -> Path:
        return (self._repository_root / self.target_directory).resolve()

    @classmethod
    def from_environment(cls, root: Path | None = None):
        if root is None:
            root = get_root()

        pyproject_path = root / "pyproject.toml"
        pyproject_data = read_pyproject_config(pyproject_path)

        if pyproject_data is not None:
            res = cls.model_validate(pyproject_data)
        else:
            res = cls()

        res._repository_root = root

        return res
