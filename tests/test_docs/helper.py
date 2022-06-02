# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2022 Valory AG
#   Copyright 2018-2021 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module contains helper function to extract code from the .md files."""
import os
import re
from functools import partial
from pathlib import Path
from typing import Callable, Dict, List, Optional

import mistune  # type: ignore

from tests.conftest import ROOT_DIR


MISTUNE_BLOCK_CODE_ID = "block_code"
IPFS_HASH_REGEX = R"Qm[A-Za-z0-9]{44}"
NON_CODE_TOKENS = ["# ...\n"]


def block_code_filter(b: Dict) -> bool:
    """Check Mistune block is a code block."""
    return b["type"] == MISTUNE_BLOCK_CODE_ID


def type_filter(type_: Optional[str], b: Dict) -> bool:
    """
    Check Mistune code block is of a certain type.

    If the field "info" is None, return False.
    If type_ is None, this function always return true.

    :param type_: the expected type of block (optional)
    :param b: the block dicionary.
    :return: True if the block should be accepted, false otherwise.
    """
    if type_ is None:
        return True
    return b["info"].strip() == type_ if b["info"] is not None else False


def extract_code_blocks(filepath: str, filter_: Optional[str] = None) -> list:
    """Extract code blocks from .md files."""
    content = Path(filepath).read_text(encoding="utf-8")
    markdown_parser = mistune.create_markdown(renderer=mistune.AstRenderer())
    blocks = markdown_parser(content)
    actual_type_filter = partial(type_filter, filter_)
    code_blocks = list(filter(block_code_filter, blocks))
    bash_code_blocks = filter(actual_type_filter, code_blocks)
    return list(b["text"] for b in bash_code_blocks)


def extract_python_code(filepath: str) -> str:
    """Removes the license part from the scripts"""
    python_str = ""
    with open(filepath, "r") as python_file:
        read_python_file = python_file.readlines()
    for i in range(21, len(read_python_file)):
        python_str += read_python_file[i]

    return python_str


def read_file(filepath: str) -> str:
    """Loads a file into a string"""
    with open(filepath, "r") as file_:
        file_str = file_.read()
    return file_str


def remove_tokens(string: str, tokens: List[str]) -> str:
    """Removes tokens from a string"""
    for token in tokens:
        string = string.replace(token, "")
    return string


def remove_ips_hashes(string: str) -> str:
    """Replaces IPFS hashes with a placeholder"""
    return re.sub(IPFS_HASH_REGEX, "<ipfs_hash>", string, count=0, flags=0)


def check_code_block(
    md_file: str,
    code_info: Dict,
    doc_process_fn: Optional[Callable] = None,
    code_process_fn: Optional[Callable] = None,
) -> None:
    """Check code blocks from the documentation"""
    code_files = code_info["code_files"]
    skip_blocks = code_info["skip_blocks"]

    # Load the code blocks from the doc file
    doc_path = os.path.join(ROOT_DIR, md_file)
    code_blocks = extract_code_blocks(filepath=doc_path, filter_="yaml")

    if skip_blocks:
        code_blocks = [
            code_blocks[i] for i in range(len(code_blocks)) if i not in skip_blocks
        ]

    # Process the code blocks
    code_blocks = (
        list(map(doc_process_fn, code_blocks)) if doc_process_fn else code_blocks
    )

    # Ensure the code block mapping is correct. We ned a code file for each code block in the doc file
    assert len(code_blocks) == len(
        code_files
    ), f"Doc checker found {len(code_blocks)} non-skipped code blocks in {md_file} but only {len(code_files)} are being checked"

    for i, code_file in enumerate(code_files):
        # Load the code file and process it
        code_path = os.path.join(ROOT_DIR, code_file)
        code = read_file(code_path)
        code = code_process_fn(code) if code_process_fn else code

        # Perform the check
        assert (
            code_blocks[i] in code
        ), f"This code-block in {md_file} doesn't exist in the code file {code_file}:\n\n{code_blocks[i]}"
