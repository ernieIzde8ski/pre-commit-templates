from pathlib import Path
from typing import NamedTuple, overload

from frozenlist import FrozenList as frozenlist
from loguru import logger

__all__ = ["TemplateMatch", "get_matching_files", "is_up_to_date"]


class TemplateMatch(NamedTuple):
    template: Path
    target: Path


def get_matching_files(
    template_directory: Path, target_directory: Path, updated_paths: list[Path]
) -> frozenlist[TemplateMatch]:
    res: frozenlist[TemplateMatch] = frozenlist()

    for path in updated_paths:
        template_match: TemplateMatch

        if path.is_relative_to(template_directory):
            relative = path.relative_to(template_directory)
            target = target_directory / relative
            template_match = TemplateMatch(path, target)
        elif path.is_relative_to(target_directory):
            relative = path.relative_to(target_directory)
            template = template_directory / relative
            if template.exists():
                template_match = TemplateMatch(template, path)
            else:
                continue
        else:
            logger.warning(
                "path is not relative to either template or target directory: {path}"
            )
            continue

        res.append(template_match)
    res.freeze()

    return res


@overload
def is_up_to_date(target: Path, source: Path, /) -> bool:
    """Check if a target path is more or as recent as its source."""
    ...


@overload
def is_up_to_date(target: Path, source: Path, /, *extra_sources: Path) -> bool:
    """Check if a target path is more or as recent as its sources."""
    ...


def is_up_to_date(target: Path, *sources: Path) -> bool:
    if not target.exists():
        return False
    base_update_time = max(
        source.stat().st_mtime_ns for source in sources if source.exists()
    )
    target_update_time = target.stat().st_mtime_ns
    return target_update_time >= base_update_time
