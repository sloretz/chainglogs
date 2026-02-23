# chainglog - update ROS CHANGELOG.rst files with AI

Update your ROS package's CHANGELOG.rst files using AI.

```
pip install chainglog
```

## Usage

Given a git or mercurial repository with ROS packages at `path/to/repository` ...

Show all commits since last release, and what ROS packages they affect:

```
chainglog show path/to/repository
```

Update all changelogs:

```
chainglog update path/to/repository
```

If you know what version you want to bump to, then use `--version`

```
chainglog update path/to/repository --version 1.2.3
```