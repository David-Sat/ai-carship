import streamlit as st

def display_progress():
    zero_count = 0
    non_zero_count = 0

    messages = [
        "Buckle up! We’re just getting started!",
        "Heating up the engines... here we go!",
        "Making magic happen...✨",
        "Loading awesomeness... please hold on.",
        "Crunching numbers and brewing coffee!",
        "Adding a pinch of creativity to the mix!",
        "Are we there yet? Nope, just half-way through!",
        "Onwards and upwards! We’re climbing higher!",
        "Smooth sailing now. We're getting closer!",
        "Just dotting the i's and crossing the t's.",
        "Last checks! Making sure everything's perfect.",
        "Almost there... Ready for the grand finale?",
        "Finishing touches being applied... stand by!",
        "All done! Thanks for sticking around. Let’s see the results!"
    ]

    for value in st.session_state.person.values():
        if value == 0:
            zero_count += 1
        else:
            non_zero_count += 1

    total_count = zero_count + non_zero_count
    progress = non_zero_count / total_count

    message_index = min(int(progress * len(messages)), len(messages) - 1)

    progress_bar = st.progress(0, text=messages[message_index])
    progress_bar.progress(progress, text=messages[message_index])