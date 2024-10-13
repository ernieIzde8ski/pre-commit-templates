from pre_commit_templates.git import get_root


def test_get_root_is_proper():
    """Tests for trailing newlines in git command output."""
    root = get_root()
    assert not root.name.endswith("\n")
