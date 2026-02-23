import datetime
import os
from typing import Optional

from . import SummarizedEntry

from catkin_pkg.changelog import CHANGELOG_FILENAME
from catkin_pkg.changelog_generator import (
    version_from_tag,
    get_version_section_match,
    generate_version_headline,
)


class ChangelogUpdater:
    """Handles the updating and formatting of CHANGELOG.rst files."""

    def __init__(self, base_path, version=None):
        self.base_path = base_path
        self.version = version

    def _changelog_path(self, pkg_path) -> str:
        return os.path.join(self.base_path, pkg_path, CHANGELOG_FILENAME)

    def has_changelog(self, pkg_path) -> bool:
        return os.path.exists(self._changelog_path(pkg_path))

    def update_package_changelog(
        self,
        pkg_path: str,
        summaries: list[SummarizedEntry],
        previous_tag: Optional[str],
    ):
        if not self.has_changelog(pkg_path):
            print(self._changelog_path(pkg_path))
            print(
                f"Skipping {pkg_path} because it does not have a {CHANGELOG_FILENAME}"
            )
            return

        if len(summaries) == 0:
            print(f"Skipping {pkg_path} because no recent changes affected it")
            return

        # Read existing changelog
        changelog_path = self._changelog_path(pkg_path)
        with open(changelog_path, "r", encoding="utf-8") as f:
            data = f.read()

        # Find insertion point
        match = None
        if previous_tag:
            last_version = version_from_tag(previous_tag)
            match = get_version_section_match(data, last_version)

        # Generate new section content
        today = datetime.date.today().strftime("%Y-%m-%d")
        headline = generate_version_headline(self.version, today)

        new_content_lines = [headline]
        contributors = set()
        for summary in summaries:
            new_content_lines.append(f"* {summary.summary}")
            contributors.add(summary.author)

        new_content_lines.append("")
        new_content_lines.append(f"* Contributors: {', '.join(sorted(contributors))}")
        new_content_lines.append("\n")

        new_text = "\n".join(new_content_lines)

        # Insert into file
        if match:
            # Insert before last tag
            updated_data = data[: match.start()] + new_text + data[match.start() :]
        else:
            # Append to end of the file
            updated_data = data + "\n" + new_text

        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write(updated_data)

        print(f"Updated {changelog_path}")
