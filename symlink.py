#!/usr/bin/env python3
#-*- coding: utf-8 -*

from __future__ import annotations

import os
import sys
from pathlib import Path

# dos에서 사용할 symlink
# dos 및 tinybox.link 명령은 symlink 표현이 어려움

def _remove_existing(dst_path: Path) -> None:
  if not dst_path.exists() and not dst_path.is_symlink():
    return

  if dst_path.is_dir() and not dst_path.is_symlink():
    raise IsADirectoryError(f"destination is directory: {dst_path}")

  dst_path.unlink()

def _symlink(src_path: Path, dst_path: Path) -> None:
  if not src_path.exists():
    raise FileNotFoundError(f"source not found: {src_path}")

  if not src_path.is_file():
    raise ValueError(f"source is not file: {src_path}")

  _remove_existing(dst_path)

  try:
    os.symlink(src_path.resolve(), dst_path, target_is_directory=False)
    print(f"OK: symlink created {src_path.resolve() {dst_path}")
  except OSError as exc:
    raise OSError(
      f"failed to create symlink: {src_path} {dst_path} error={exc}"
    )  from exc

def main() -> int:
  if len(sys.argv) != 3:
    print("Usage: symlink.py <src_file> <dst_file>", file=sys.stderr)

  src_path = Path(sys.argv[1])
  dst_path = Path(sys.argv[2])

  try:
    _symlink(src_path=src_path, dst_path=dst_path)
    return 0
  except Exception as exc:
    print(f"ERROR: {exc}", file=sys.stderr)
    return 1


if __name__ == '__main__':
  raise SystemExit(main())
