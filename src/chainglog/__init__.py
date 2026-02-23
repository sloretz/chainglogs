from dataclasses import dataclass

from catkin_pkg.changelog_generator_vcs import LogEntry


@dataclass
class SummarizedEntry:
    entry: LogEntry
    summary: str

    @property
    def author(self):
        return self.entry.author

    def affects_ros_package(self, ros_package_path):
        return self.entry.affects_path(ros_package_path)
