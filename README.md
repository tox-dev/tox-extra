# tox-extra

This [tox plugin](https://github.com/topics/tox-plugin) adds a few extra checks
like:

- [tox-extra](#tox-extra)
  - [Checks Git Dirty Status](#checks-git-dirty-status)
  - [Checks system dependencies using bindep](#checks-system-dependencies-using-bindep)

## Checks Git Dirty Status

It ensures exit code 1 if git reports dirty or untracked files _after_ the run.

Usage example:

```shell
$ tox -e py
...
ERROR: Git reported dirty status. Git should never report dirty status at the end of testing, regardless if status is passed, failed or aborted.
On branch devel
Your branch is up to date with 'origin/devel'.

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	some-untracked.txt

nothing added to commit but untracked files present (use "git add" to track)
__________________________________________ summary ___________________________________________
ERROR:   py: failed
```

The goal of this plugin is to help developers be aware of files modified by tests
or untracked files before they commit the code. This plugin also does not take into
consideration the global `.gitignore`, something that can make git miss reporting
some untracked files, the goal being to assure that when a new developer clones and
runs the tests they do not endup with an unexpected git status.

If you have any cases where you expect to have git report dirty, please
add `--allow-dirty` to the command call to disable this check.

## Checks system dependencies using bindep

If a `bindep.txt` config file is found, tox will run `bindep [profiles]` to
check if dependencies, including test ones, are present. There is no need to
install bindep your self.

This plugin will add the following list of bindep profiles:

- `test` is always added as tox itself is a test tool
- exact tox env name
- tox env name itself split by `-'
- `pythonX.Y` and `pyXY` based on which python current tox env will use

This should allow developers to modify their `bindep.txt` file to include
system dependencies specific to a single tox environment if they wish.

To disable bindep feature, you can define `TOX_EXTRA_BINDEP=0` in your
environment.
