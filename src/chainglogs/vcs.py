import sys
from typing import Optional

from catkin_pkg.changelog_generator_vcs import get_vcs_client
from catkin_pkg.packages import find_package_paths


class VCS:
    """Handles version control operations and package mapping."""

    def __init__(self, path: str):
        self.path = path
        try:
            self.client = get_vcs_client(self.path)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def get_ros_package_paths(self) -> list[str]:
        return find_package_paths(self.path)

    def get_recent_changes(self) -> tuple[Optional[str], list[any]]:
        """
        Returns the most recent tag name and all log entries since that tag.
        """
        tags = self.client.get_tags()
        older_tag = tags[0].name if tags else None

        log_entries = self.client.get_log_entries(None, older_tag)

        return older_tag, log_entries

    def format_log_message(self, msg: str) -> str:
        return self.client.replace_repository_references(msg)
