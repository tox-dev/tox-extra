# tox-extra

This [tox plugin](https://github.com/topics/tox-plugin) adds few extra checks
like:

- ensure exit code 1 if git reports dirty or untracked files _after_ the run

Usage example:

```
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

The goal of this plugin is to help developers be aware about files modified by tests
or untracked files before they commit the code. This plugin also does not take into
consideration the global `.gitignore`, something that can make git miss reporting
some untracked files, the goal being to assure that when a new developer clones and
runs the tests they do not endup with an unexpected git status.

If you have any cases where you expect to have git report dirty, please
add `--allow-dirty` to the command call to disable this check.
