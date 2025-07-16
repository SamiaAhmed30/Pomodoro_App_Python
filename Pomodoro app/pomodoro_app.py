import streamlit as st
import time
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Pomodoro Timer",
    page_icon="🍅",
    layout="centered",
    initial_sidebar_state="expanded"
)

def init_session_state():
    defaults = {
        "reps": 0,
        "time_left": 0,
        "start_time": None,
        "running": False,
        "status": "Ready",
        "marks": "",
        "just_finished": False,
        "total_work_time": 0,
        "session_start": None,
        "last_notification": None,
        "auto_start": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

st.sidebar.title("⏱️ Timer Settings")
st.sidebar.markdown("### Duration (minutes)")
WORK_MIN = st.sidebar.slider("Work Duration", 15, 90, 25, step=5)
SHORT_BREAK_MIN = st.sidebar.slider("Short Break", 5, 20, 5, step=1)
LONG_BREAK_MIN = st.sidebar.slider("Long Break", 15, 60, 20, step=5)

st.sidebar.markdown("### Preferences")
st.session_state.auto_start = st.sidebar.checkbox("Auto-start next session", value=st.session_state.auto_start)
show_stats = st.sidebar.checkbox("Show session statistics", value=True)
notification_sound = st.sidebar.checkbox("Play notification sound", value=True)

def get_status_and_duration():
    if st.session_state.reps % 8 == 0 and st.session_state.reps != 0:
        return "Long Break", LONG_BREAK_MIN * 60
    elif st.session_state.reps % 2 == 0:
        return "Short Break", SHORT_BREAK_MIN * 60
    else:
        return "Work", WORK_MIN * 60

def start_timer():
    st.session_state.reps += 1
    st.session_state.status, duration = get_status_and_duration()
    st.session_state.time_left = duration
    st.session_state.start_time = time.time()
    st.session_state.running = True
    st.session_state.just_finished = False
    if st.session_state.session_start is None:
        st.session_state.session_start = datetime.now()

def reset_timer():
    st.session_state.reps = 0
    st.session_state.time_left = 0
    st.session_state.start_time = None
    st.session_state.running = False
    st.session_state.status = "Ready"
    st.session_state.marks = ""
    st.session_state.just_finished = False
    st.session_state.total_work_time = 0
    st.session_state.session_start = None

def pause_timer():
    if st.session_state.running:
        now = time.time()
        elapsed = int(now - st.session_state.start_time)
        st.session_state.time_left = max(st.session_state.time_left - elapsed, 0)
        st.session_state.running = False

def resume_timer():
    if not st.session_state.running and st.session_state.time_left > 0:
        st.session_state.start_time = time.time()
        st.session_state.running = True

def format_time(seconds):
    mins, secs = divmod(max(0, int(seconds)), 60)
    return f"{mins:02d}:{secs:02d}"

def get_status_color(status):
    if status == "Work":
        return "#FF6B6B"
    elif status == "Short Break":
        return "#4ECDC4"
    elif status == "Long Break":
        return "#45B7D1"
    else:
        return "#95A5A6"

st.title("🍅 Pomodoro Timer")

status_color = get_status_color(st.session_state.status)
st.markdown(f"""
    <div style="text-align: center; padding: 20px; border-radius: 10px; 
                background-color: {status_color}20; border: 2px solid {status_color};">
        <h2 style="color: {status_color}; margin: 0;">Session {st.session_state.reps}</h2>
        <h3 style="color: {status_color}; margin: 10px 0;">{st.session_state.status}</h3>
    </div>
""", unsafe_allow_html=True)

timer_placeholder = st.empty()

if st.session_state.running:
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = st.session_state.time_left - elapsed
    if remaining <= 0:
        st.session_state.running = False
        st.session_state.time_left = 0
        st.session_state.just_finished = True
        if st.session_state.status == "Work":
            work_sessions = (st.session_state.reps + 1) // 2
            st.session_state.marks = "✓" * work_sessions
            st.session_state.total_work_time += WORK_MIN
        remaining = 0
        if st.session_state.auto_start:
            time.sleep(1)
            start_timer()
    current_time = remaining
else:
    current_time = st.session_state.time_left

timer_display = format_time(current_time)
progress = 0
if st.session_state.status != "Ready":
    _, total_duration = get_status_and_duration()
    progress = max(0, (total_duration - current_time) / total_duration)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
        <div style="text-align: center; font-size: 3em; font-weight: bold; 
                    color: {status_color}; margin: 20px 0;">
            ⏳ {timer_display}
        </div>
    """, unsafe_allow_html=True)
    if st.session_state.status != "Ready":
        st.progress(progress)

st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("▶️ Start", disabled=st.session_state.running, use_container_width=True):
        start_timer()
        st.rerun()

with col2:
    if st.button("⏸️ Pause", disabled=not st.session_state.running, use_container_width=True):
        pause_timer()
        st.rerun()

with col3:
    if st.button("⏯️ Resume", disabled=st.session_state.running or st.session_state.time_left == 0, use_container_width=True):
        resume_timer()
        st.rerun()

with col4:
    if st.button("🔄 Reset", use_container_width=True):
        reset_timer()
        st.rerun()

if st.session_state.marks:
    st.success(f"🎯 Work sessions completed: {st.session_state.marks} ({len(st.session_state.marks)} sessions)")

if show_stats and st.session_state.session_start:
    st.markdown("---")
    st.subheader("📊 Session Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Work Time", f"{st.session_state.total_work_time} min")
    with col2:
        session_duration = datetime.now() - st.session_state.session_start
        st.metric("Session Duration", f"{int(session_duration.total_seconds() // 60)} min")
    with col3:
        work_sessions = len(st.session_state.marks)
        st.metric("Work Sessions", work_sessions)

if st.session_state.just_finished:
    st.balloons()
    if st.session_state.status == "Work":
        st.success("🎉 Great work! Time for a break!")
    else:
        st.info("⏰ Break time's over! Ready to get back to work?")
    if notification_sound:
        st.markdown(
            """
            <audio autoplay>
              <source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg">
            </audio>
            """,
            unsafe_allow_html=True
        )
    st.session_state.just_finished = False

st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em;">
        💡 <strong>Pro tip:</strong> Use the sidebar to customize your work and break durations. 
        The Pomodoro Technique suggests 25-minute work sessions with 5-minute breaks.
    </div>
""", unsafe_allow_html=True)

if st.session_state.running:
    time.sleep(1)
    st.rerun()
