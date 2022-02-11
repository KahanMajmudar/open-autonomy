# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2021-2022 Valory AG
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

"""Test the common.py module of the skill."""

import binascii
import json
import time
from pathlib import Path
from typing import Any, Type, cast
from unittest import mock

from packages.valory.protocols.contract_api.custom_types import State
from packages.valory.protocols.ledger_api.message import LedgerApiMessage
from packages.valory.skills.abstract_round_abci.base import BasePeriodState, StateDB
from packages.valory.skills.abstract_round_abci.behaviour_utils import BaseState

from tests.conftest import ROOT_DIR
from tests.test_skills.base import FSMBehaviourBaseCase


DRAND_VALUE = {
    "round": 1416669,
    "randomness": "f6be4bf1fa229f22340c1a5b258f809ac4af558200775a67dacb05f0cb258a11",
    "signature": (
        "b44d00516f46da3a503f9559a634869b6dc2e5d839e46ec61a090e3032172954929a5"
        "d9bd7197d7739fe55db770543c71182562bd0ad20922eb4fe6b8a1062ed21df3b68de"
        "44694eb4f20b35262fa9d63aa80ad3f6172dd4d33a663f21179604"
    ),
    "previous_signature": (
        "903c60a4b937a804001032499a855025573040cb86017c38e2b1c3725286756ce8f33"
        "61188789c17336beaf3f9dbf84b0ad3c86add187987a9a0685bc5a303e37b008fba8c"
        "44f02a416480dd117a3ff8b8075b1b7362c58af195573623187463"
    ),
}


class CommonBaseCase(FSMBehaviourBaseCase):
    """Base case for testing PriceEstimation FSMBehaviour."""

    path_to_skill = Path(
        ROOT_DIR, "packages", "valory", "skills", "price_estimation_abci"
    )


class BaseRandomnessBehaviourTest(CommonBaseCase):
    """Test RandomnessBehaviour."""

    randomness_behaviour_class: Type[BaseState]
    next_behaviour_class: Type[BaseState]
    done_event: Any

    def test_randomness_behaviour(
        self,
    ) -> None:
        """Test RandomnessBehaviour."""

        self.fast_forward_to_state(
            self.behaviour,
            self.randomness_behaviour_class.state_id,
            BasePeriodState(StateDB(initial_period=0, initial_data={})),
        )
        assert (
            cast(
                BaseState,
                cast(BaseState, self.behaviour.current_state),
            ).state_id
            == self.randomness_behaviour_class.state_id
        )
        self.behaviour.act_wrapper()
        self.mock_http_request(
            request_kwargs=dict(
                method="GET",
                headers="",
                version="",
                body=b"",
                url="https://drand.cloudflare.com/public/latest",
            ),
            response_kwargs=dict(
                version="",
                status_code=200,
                status_text="",
                headers="",
                body=json.dumps(DRAND_VALUE).encode("utf-8"),
            ),
        )

        self.behaviour.act_wrapper()
        self.mock_a2a_transaction()
        self._test_done_flag_set()
        self.end_round(self.done_event)

        state = cast(BaseState, self.behaviour.current_state)
        assert state.state_id == self.next_behaviour_class.state_id

    def test_invalid_drand_value(
        self,
    ) -> None:
        """Test invalid drand values."""
        self.fast_forward_to_state(
            self.behaviour,
            self.randomness_behaviour_class.state_id,
            BasePeriodState(StateDB(initial_period=0, initial_data={})),
        )
        assert (
            cast(
                BaseState,
                cast(BaseState, self.behaviour.current_state),
            ).state_id
            == self.randomness_behaviour_class.state_id
        )
        self.behaviour.act_wrapper()

        drand_value = DRAND_VALUE.copy()
        drand_value["randomness"] = binascii.hexlify(b"randomness_hex").decode()
        self.mock_http_request(
            request_kwargs=dict(
                method="GET",
                headers="",
                version="",
                body=b"",
                url="https://drand.cloudflare.com/public/latest",
            ),
            response_kwargs=dict(
                version="",
                status_code=200,
                status_text="",
                headers="",
                body=json.dumps(drand_value).encode(),
            ),
        )

    def test_invalid_response(
        self,
    ) -> None:
        """Test invalid json response."""
        self.fast_forward_to_state(
            self.behaviour,
            self.randomness_behaviour_class.state_id,
            BasePeriodState(StateDB(initial_period=0, initial_data={})),
        )
        assert (
            cast(
                BaseState,
                cast(BaseState, self.behaviour.current_state),
            ).state_id
            == self.randomness_behaviour_class.state_id
        )
        self.behaviour.act_wrapper()

        self.mock_http_request(
            request_kwargs=dict(
                method="GET",
                headers="",
                version="",
                body=b"",
                url="https://drand.cloudflare.com/public/latest",
            ),
            response_kwargs=dict(
                version="", status_code=200, status_text="", headers="", body=b""
            ),
        )
        self.behaviour.act_wrapper()
        time.sleep(1)
        self.behaviour.act_wrapper()

    def test_max_retries_reached_fallback(
        self,
    ) -> None:
        """Test with max retries reached."""
        self.fast_forward_to_state(
            self.behaviour,
            self.randomness_behaviour_class.state_id,
            BasePeriodState(StateDB(initial_period=0, initial_data={})),
        )
        assert (
            cast(
                BaseState,
                cast(BaseState, self.behaviour.current_state),
            ).state_id
            == self.randomness_behaviour_class.state_id
        )
        with mock.patch.object(
            self.behaviour.context.randomness_api,
            "is_retries_exceeded",
            return_value=True,
        ):
            self.behaviour.act_wrapper()
            self.mock_ledger_api_request(
                request_kwargs=dict(
                    performative=LedgerApiMessage.Performative.GET_STATE
                ),
                response_kwargs=dict(
                    performative=LedgerApiMessage.Performative.STATE,
                    state=State(ledger_id="ethereum", body={"hash": "0xa"}),
                ),
            )

            self.behaviour.act_wrapper()
            self.mock_a2a_transaction()
            self._test_done_flag_set()
            self.end_round(self.done_event)

            state = cast(BaseState, self.behaviour.current_state)
            assert state.state_id == self.next_behaviour_class.state_id

    def test_max_retries_reached_fallback_fail(
        self,
    ) -> None:
        """Test with max retries reached."""
        self.fast_forward_to_state(
            self.behaviour,
            self.randomness_behaviour_class.state_id,
            BasePeriodState(StateDB(initial_period=0, initial_data={})),
        )
        assert (
            cast(
                BaseState,
                cast(BaseState, self.behaviour.current_state),
            ).state_id
            == self.randomness_behaviour_class.state_id
        )
        with mock.patch.object(
            self.behaviour.context.randomness_api,
            "is_retries_exceeded",
            return_value=True,
        ):
            self.behaviour.act_wrapper()
            self.mock_ledger_api_request(
                request_kwargs=dict(
                    performative=LedgerApiMessage.Performative.GET_STATE
                ),
                response_kwargs=dict(
                    performative=LedgerApiMessage.Performative.ERROR,
                    state=State(ledger_id="ethereum", body={}),
                ),
            )

            self.behaviour.act_wrapper()

    def test_max_retries_reached_fallback_fail_case_2(
        self,
    ) -> None:
        """Test with max retries reached."""
        self.fast_forward_to_state(
            self.behaviour,
            self.randomness_behaviour_class.state_id,
            BasePeriodState(StateDB(initial_period=0, initial_data={})),
        )
        assert (
            cast(
                BaseState,
                cast(BaseState, self.behaviour.current_state),
            ).state_id
            == self.randomness_behaviour_class.state_id
        )
        with mock.patch.object(
            self.behaviour.context.randomness_api,
            "is_retries_exceeded",
            return_value=True,
        ):
            self.behaviour.act_wrapper()
            self.mock_ledger_api_request(
                request_kwargs=dict(
                    performative=LedgerApiMessage.Performative.GET_STATE
                ),
                response_kwargs=dict(
                    performative=LedgerApiMessage.Performative.STATE,
                    state=State(ledger_id="ethereum", body={}),
                ),
            )

            self.behaviour.act_wrapper()

    def test_clean_up(
        self,
    ) -> None:
        """Test when `observed` value is none."""
        self.fast_forward_to_state(
            self.behaviour,
            self.randomness_behaviour_class.state_id,
            BasePeriodState(StateDB(initial_period=0, initial_data={})),
        )
        assert (
            cast(
                BaseState,
                cast(BaseState, self.behaviour.current_state),
            ).state_id
            == self.randomness_behaviour_class.state_id
        )
        self.behaviour.context.randomness_api._retries_attempted = 1
        assert self.behaviour.current_state is not None
        self.behaviour.current_state.clean_up()
        assert self.behaviour.context.randomness_api._retries_attempted == 0


class BaseSelectKeeperBehaviourTest(CommonBaseCase):
    """Test SelectKeeperBehaviour."""

    select_keeper_behaviour_class: Type[BaseState]
    next_behaviour_class: Type[BaseState]
    done_event: Any

    def test_select_keeper(
        self,
    ) -> None:
        """Test select keeper agent."""
        participants = frozenset({self.skill.skill_context.agent_address, "a_1", "a_2"})
        self.fast_forward_to_state(
            behaviour=self.behaviour,
            state_id=self.select_keeper_behaviour_class.state_id,
            period_state=BasePeriodState(
                StateDB(
                    initial_period=0,
                    initial_data=dict(
                        participants=participants,
                        most_voted_randomness="56cbde9e9bbcbdcaf92f183c678eaa5288581f06b1c9c7f884ce911776727688",
                    ),
                )
            ),
        )
        assert (
            cast(
                BaseState,
                cast(BaseState, self.behaviour.current_state),
            ).state_id
            == self.select_keeper_behaviour_class.state_id
        )
        self.behaviour.act_wrapper()
        self.mock_a2a_transaction()
        self._test_done_flag_set()
        self.end_round(self.done_event)
        state = cast(BaseState, self.behaviour.current_state)
        assert state.state_id == self.next_behaviour_class.state_id

    def test_select_keeper_preexisting_keeper(
        self,
    ) -> None:
        """Test select keeper agent."""
        participants = frozenset({self.skill.skill_context.agent_address, "a_1", "a_2"})
        preexisting_keeper = next(iter(participants))
        self.fast_forward_to_state(
            behaviour=self.behaviour,
            state_id=self.select_keeper_behaviour_class.state_id,
            period_state=BasePeriodState(
                StateDB(
                    initial_period=0,
                    initial_data=dict(
                        participants=participants,
                        most_voted_randomness="56cbde9e9bbcbdcaf92f183c678eaa5288581f06b1c9c7f884ce911776727688",
                        most_voted_keeper_address=preexisting_keeper,
                    ),
                )
            ),
        )
        assert (
            cast(
                BaseState,
                cast(BaseState, self.behaviour.current_state),
            ).state_id
            == self.select_keeper_behaviour_class.state_id
        )
        self.behaviour.act_wrapper()
        self.mock_a2a_transaction()
        self._test_done_flag_set()
        self.end_round(self.done_event)
        state = cast(BaseState, self.behaviour.current_state)
        assert state.state_id == self.next_behaviour_class.state_id