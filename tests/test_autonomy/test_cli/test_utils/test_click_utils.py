# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2022 Valory AG
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

"""Test for cli click utils."""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import click
import pytest
from aea.test_tools.click_testing import CliRunner

from autonomy.analyse.abci.app_spec import FSMSpecificationLoader as FSMSpecLoader
from autonomy.cli.utils.click_utils import (
    PathArgument,
    abci_spec_format_flag,
    chain_selection_flag,
    image_profile_flag,
    sys_path_patch,
)
from autonomy.deploy.chain import CHAIN_CONFIG
from autonomy.deploy.image import ImageProfiles


@dataclass
class ClickFlagTestCase:
    """ClickFlagTestCase"""

    decorator: callable
    items: Tuple
    opt_prefix: str = ""


@pytest.mark.parametrize(
    "test_case",
    [
        ClickFlagTestCase(image_profile_flag, ImageProfiles.ALL),
        ClickFlagTestCase(chain_selection_flag, tuple(CHAIN_CONFIG), opt_prefix="use-"),
        ClickFlagTestCase(abci_spec_format_flag, FSMSpecLoader.OutputFormats.ALL),
    ],
)
def test_flag_decorators(test_case: ClickFlagTestCase) -> None:
    """Test click flag decorators"""

    @click.command()
    @test_case.decorator()
    def dummy() -> None:
        """"""

    assert len(dummy.params) == len(test_case.items)
    for parameter, output_format in zip(dummy.params, reversed(test_case.items)):
        assert isinstance(parameter, click.Option)
        assert output_format in parameter.flag_value
        assert parameter.opts == [f"--{test_case.opt_prefix}{output_format}"]
        assert parameter.help


def test_path_argument() -> None:
    """Test PathArgument"""

    @click.command()
    @click.option("--path", type=PathArgument())
    def dummy(path) -> None:
        """"""
        click.echo(isinstance(path, Path))

    cli_runner = CliRunner()
    result = cli_runner.invoke(
        dummy, args=("--path", "packages"), standalone_mode=False
    )
    assert result.stdout.strip() == str(True)
