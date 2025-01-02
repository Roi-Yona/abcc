from threading import Thread
from time import sleep
from typing import Callable, Tuple, Any

import streamlit as st
from matplotlib.pyplot import barbs
# The next import is for adding the context for threads under streamlit.
# Note that IT IS NOT a part of the official API, and this currently works for version 1.40.1,
# See the Github discussion for the history of solution hacks through different versions:
# https://github.com/streamlit/streamlit/issues/1326
from streamlit.runtime.scriptrunner import add_script_run_ctx


def advance_progress_bar(
        progress_bar: st.delta_generator.DeltaGenerator,
        progress_text: str,
        delay_time: int,
        starting_value: int = 0,
        last_value: int = 99,
        advance_delay: float = 0.1
):
    advances_number = int(delay_time // advance_delay)
    delay_left_after_loop = delay_time - (advances_number * advance_delay)
    bar_delta_value = (last_value - starting_value) / advances_number

    for i in range(advances_number):
        sleep(advance_delay)

        new_bar_value = starting_value + int(i * bar_delta_value)
        progress_bar.progress(new_bar_value, progress_text)

    sleep(delay_left_after_loop)


def run_func_with_fake_progress_bar(
        delay: int,
        loading_message: str,
        finish_message: str,
        func_to_run: Callable,
        *args,
        **kwargs
) -> Tuple[st.delta_generator.DeltaGenerator, Any]:
    """
    Runs the given function with a fake streamlit progress bar.

    Currently, the progress bar will wait at least `delay` seconds (does not "jump forward" even if the function finished running)
    :param delay: the number of seconds to spread the advancement across (will get stuck on "almost done" if the delay was reached but the function is still running)
    :param loading_message: message to display when the progress bar is partially full
    :param finish_message: message to display when the progress bar is complete
    :param func_to_run: the function to run
    :param args: args for running the function
    :param kwargs: kwargs for running the function
    :return: the progress bar object (if you want to remove it then call its "empty" method) and the function result
    """
    progress_bar = st.progress(0, text=loading_message)

    bar_advancement_thread = Thread(
        target=advance_progress_bar,
        args=(
            progress_bar,
            loading_message,
            delay
        )
    )
    add_script_run_ctx(bar_advancement_thread)

    bar_advancement_thread.start()
    result = func_to_run(*args, **kwargs)
    bar_advancement_thread.join()

    progress_bar.progress(100, text=finish_message)
    return progress_bar, result