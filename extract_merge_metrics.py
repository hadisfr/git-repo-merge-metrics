#!/usr/bin/env python

import re
import csv
from sys import argv, stderr
from os import linesep
from dataclasses import dataclass
from typing import Generator, Iterable, Dict, Any

from git import Repo, Git, Commit
from tqdm import tqdm


FIELD_NAMES = ["branch", "commit_hash", "timestamp", "added_lines", "removed_lines", "touched_files"]


@dataclass
class Diff:
    add: int
    remove: int
    files: int
    # addr: str

    @staticmethod
    def from_line(line: str):
        splitted = str.split(line, "\t")
        if splitted[0] == "-":
            splitted[0] = 0
        if splitted[1] == "-":
            splitted[1] = 0
        return Diff(int(splitted[0]), int(splitted[1]), 1)

    def __add__(self, other):
        return Diff(
            self.add + other.add,
            self.remove + other.remove,
            self.files + other.files,
        )


Diff.ZERO = Diff(0, 0, 0)


def get_diff_stat(git: Git, old_comit: Commit, new_commit: Commit) -> Diff:
    diff = git.diff(old_comit, new_commit, "--numstat").split(linesep)
    if not diff[0]:
        diff = []
    diff = map(Diff.from_line, diff)
    return sum(diff, Diff.ZERO)


def analyse_repo(addr: str) -> Generator[Dict[str, Any], None, None]:
    repo = Repo(addr)
    git = repo.git
    assert not repo.bare
    repo.config_reader()
    assert not repo.is_dirty(), "repo %s is dirty" % addr

    commit = repo.commit("master")
    while commit.parents:
        # print(commit)
        parent = commit.parents[0]
        merge_branch = re.match(r"Merge branch '(.*)' into 'master'", commit.message.split(linesep)[0])
        if merge_branch:
            assert commit.committed_date == commit.authored_date
            diff = get_diff_stat(git, parent, commit)
            merge_stat = {
                "branch": merge_branch[1],
                "commit_hash": commit.hexsha,
                "timestamp": commit.committed_date,
                "added_lines": diff.add,
                "removed_lines": diff.remove,
                "touched_files": diff.files,
            }
            yield merge_stat
        commit = parent


def write_csv(addr: str, merges: Iterable[Dict[str, Any]]) -> None:
    with open(addr, "w") as f:
        w = csv.DictWriter(f, FIELD_NAMES)
        w.writeheader()
        w.writerows(tqdm(merges))


def main():
    if len(argv) != 3 or not argv[2].endswith(".csv"):
        print("usage:\t%s git_repo result" % argv[0], file=stderr)
        exit(2)

    merges = analyse_repo(argv[1])
    write_csv(argv[2], merges)


if __name__ == '__main__':
    main()
