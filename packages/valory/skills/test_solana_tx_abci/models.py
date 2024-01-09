# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2023 Valory AG
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

"""This module contains the shared state for the Solana test application."""

from packages.valory.skills.abstract_round_abci.models import BaseParams
from packages.valory.skills.abstract_round_abci.models import (
    BenchmarkTool as BaseBenchmarkTool,
)
from packages.valory.skills.abstract_round_abci.models import Requests as BaseRequests
from packages.valory.skills.abstract_round_abci.models import (
    SharedState as BaseSharedState,
)
from packages.valory.skills.test_solana_tx_abci.composition import ComposedAbciApp
from packages.valory.skills.test_solana_tx_abci.rounds import SolanaTestAbciApp


MARGIN = 5


Requests = BaseRequests
BenchmarkTool = BaseBenchmarkTool


class SharedState(BaseSharedState):
    """Keep the current shared state of the skill."""

    abci_app_cls = ComposedAbciApp


class Params(BaseParams):
    """Keep the current parameters of the skill."""

    def __init__(self, **kwargs):
        """Initialize the parameters."""
        super().__init__(**kwargs)
        self.squad_vault = self._ensure("squad_vault", kwargs, str)
        self.transfer_to_pubkey = self._ensure("transfer_to_pubkey", kwargs, str)
        self.transfer_lamports = self._ensure("transfer_lamports", kwargs, int)
