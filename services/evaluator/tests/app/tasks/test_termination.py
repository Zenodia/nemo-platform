# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import signal
import threading

import pytest
from nmp.evaluator.app.tasks import termination
from nmp.evaluator.app.tasks.termination import register_task_signal_handlers
from pytest_mock import MockerFixture


class TestRegisterTaskSignalHandlers:
    def test_registers_handlers_on_main_thread(self, mocker: MockerFixture):
        log = mocker.Mock()
        mocker.patch.object(termination, "log", log)
        signal_register = mocker.patch("nmp.evaluator.app.tasks.termination.signal.signal")

        register_task_signal_handlers()

        assert signal_register.call_count == 2
        assert signal_register.call_args_list[0].args[0] == signal.SIGTERM
        assert signal_register.call_args_list[1].args[0] == signal.SIGINT

        handler = signal_register.call_args_list[0].args[1]
        with pytest.raises(KeyboardInterrupt):
            handler(signal.SIGTERM, None)

        log.info.assert_called_once_with("Received %s. Exiting task gracefully.", "SIGTERM")

    def test_skips_registration_outside_main_thread(self, mocker: MockerFixture):
        log = mocker.Mock()
        mocker.patch.object(termination, "log", log)
        signal_register = mocker.patch("nmp.evaluator.app.tasks.termination.signal.signal")

        non_main_thread = mocker.Mock(spec=threading.Thread)
        main_thread = mocker.Mock(spec=threading.Thread)
        mocker.patch("nmp.evaluator.app.tasks.termination.threading.current_thread", return_value=non_main_thread)
        mocker.patch("nmp.evaluator.app.tasks.termination.threading.main_thread", return_value=main_thread)

        register_task_signal_handlers()

        signal_register.assert_not_called()
        log.debug.assert_called_once_with("Skipping signal handler registration outside main thread")
