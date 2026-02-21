#!/usr/bin/env python3

import argparse

from . import SummarizedEntry
from .changelog_updater import ChangelogUpdater
from .vcs import VCS


def cmd_show(args):
    """Executes the 'show' command."""
    vcs = VCS(args.path)
    _, log_entries = vcs.get_recent_changes()
    ros_package_paths = vcs.get_ros_package_paths()

    if not log_entries:
        print("No changes found since the last tag.")
        return

    for entry in log_entries:
        print(f"\nCommit: {entry.msg.splitlines()[0]}")
        print(f"Author: {entry.author}")
        affected_pkgs = [pkg for pkg in ros_package_paths if entry.affects_path(pkg)]

        if affected_pkgs:
            print("Affected packages:")
            for pkg in affected_pkgs:
                print(f"  - {pkg}")
        else:
            print("Affected packages: None")


def cmd_update(args):
    """Executes the 'update' command."""
    # This is a slow import
    from .ai import AI

    vcs = VCS(args.path)
    previous_tag, log_entries = vcs.get_recent_changes()
    ros_package_paths = vcs.get_ros_package_paths()

    ai_client = AI()
    updater = ChangelogUpdater(args.path)

    # Generate AI summaries
    summaries: list[SummarizedEntry] = []
    for entry in log_entries:
        linked_msg = vcs.format_log_message(entry.msg)
        summary = ai_client.summarize_commit(linked_msg)
        summaries.append(SummarizedEntry(entry=entry, summary=summary))

    for pkg_path in ros_package_paths:
        subset = []
        for se in summaries:
            if se.affects_ros_package(pkg_path):
                subset.append(se)
        updater.update_package_changelog(pkg_path, subset, previous_tag)


def main():
    parser = argparse.ArgumentParser(
        description="Generate changelog entries for ROS packages using Gemini."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_parser = subparsers.add_parser(
        "show", help="Show changes and affected packages without modifying files."
    )
    show_parser.add_argument("path", help="Path to the repository")

    update_parser = subparsers.add_parser(
        "update", help="Update CHANGELOG.rst files using AI summaries."
    )
    update_parser.add_argument("path", help="Path to the repository")

    args = parser.parse_args()

    if args.command == "show":
        cmd_show(args)
    elif args.command == "update":
        cmd_update(args)


if __name__ == "__main__":
    main()
