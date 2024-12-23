from time import sleep

import streamlit as st

def advance_progress_bar(
        progress_bar: st.delta_generator.DeltaGenerator,
        progress_text: str,
        delay_time: int,
        starting_value: int = 0,
        last_value: int = 99,
        advance_delay: float = 0.1
):
    advances_number = int(delay_time // advance_delay)
    delta_after_loop = delay_time - (advances_number * advance_delay)
    bar_delta_value = (last_value - starting_value) / advances_number

    print("!!!")
    print(bar_delta_value)
    print(delta_after_loop)
    print(advances_number)
    for i in range(advances_number):
        sleep(advance_delay)

        new_bar_value = starting_value + int(i * bar_delta_value)
        progress_bar.progress(new_bar_value, progress_text)

    sleep(delta_after_loop)