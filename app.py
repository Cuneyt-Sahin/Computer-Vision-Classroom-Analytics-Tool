import streamlit as st
import cv2
import pandas as pd
import time
from datetime import datetime
import os
import io
import subprocess
import sys
from config import Config
from face_analyzer import FaceAnalyzer
from student_manager import StudentManager


st.set_page_config(
    page_title="AYBÜ SmartAttend | Auto Attendance",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Minimal safe styling to avoid breaking Streamlit Light/Dark modes */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #001a33 0%, #003366 100%);
        border-right: 2px solid #001a33;
    }
    /* Enforce white text for sidebar elements */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    .aybu-header { 
        color: #ffffff !important; 
        font-weight: 800; 
        text-align: center; 
        margin-bottom: 5px;
        padding-top: 15px;
    }
    .aybu-subheader {
        color: #80c1ff !important;
        font-weight: 600;
        text-align: center;
        font-size: 1.1em;
        margin-bottom: 25px;
    }
    
    .status-text {
        font-size: 1.1em;
        font-weight: bold;
        margin-bottom: 10px;
    }

    .alert-box { 
        background-color: #ffe6e6; 
        border-left: 6px solid #e60000; 
        padding: 15px; 
        border-radius: 8px; 
        color: #b30000; 
        font-weight: 800;
        font-size: 1.1em;
        animation: blinker 1s linear infinite;
        margin-bottom: 15px;
        box-shadow: 0px 4px 6px rgba(230, 0, 0, 0.1);
    }
    @keyframes blinker { 50% { opacity: 0.6; } }

    /* Primary buttons */
    .stButton>button { 
        border-radius: 8px; 
        width: 100%; 
        font-weight: bold; 
        transition: all 0.3s ease;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Initialize Session State
if "initialized" not in st.session_state:
    with st.spinner("⏳ Loading AI Models... (Please wait)"):
        st.session_state.manager = StudentManager()
        st.session_state.manager.sync_from_folder()
        st.session_state.analyzer = FaceAnalyzer()
        
        st.session_state.hit_counts = {}
        st.session_state.session_active = False
        st.session_state.live_list = pd.DataFrame(columns=["School No", "Full Name", "Entry Time", "Status"])
        st.session_state.present_count = 0
        st.session_state.total_students = len(st.session_state.manager.students_df)
        st.session_state.camera_index = 1
        st.session_state.initialized = True
        st.session_state.stop_video = False

def handle_attendance(student_id):
    """Processes a recognized student ID."""
    if not st.session_state.session_active:
        return

    # Hit Counter Logic
    if student_id not in st.session_state.hit_counts:
        st.session_state.hit_counts[student_id] = 0
    st.session_state.hit_counts[student_id] += 1

    # Threshold Check
    if st.session_state.hit_counts[student_id] == Config.REQUIRED_VOTING_HITS:
        success = st.session_state.manager.update_attendance(student_id)
        if success:
            st.session_state.present_count += 1
            
            student_row = st.session_state.manager.students_df[st.session_state.manager.students_df["School No"] == student_id].iloc[0]
            full_name = student_row["Full Name"]
            time_str = datetime.now().strftime("%H:%M:%S")

            new_record = pd.DataFrame([{
                "School No": student_id,
                "Full Name": full_name,
                "Entry Time": time_str,
                "Status": "✅ Present"
            }])
            st.session_state.live_list = pd.concat([new_record, st.session_state.live_list], ignore_index=True)


# --- 3. SIDEBAR ---
with st.sidebar:
    try:
        if os.path.exists("logo.svg"):
            import base64
            with open("logo.svg", "rb") as f:
                base64_svg = base64.b64encode(f.read()).decode("utf-8")
            svg_uri = f"data:image/svg+xml;base64,{base64_svg}"
            st.markdown(
                f'<div style="text-align: center; margin-bottom: 20px;"><img src="{svg_uri}" style="max-width: 100%;"></div>', 
                unsafe_allow_html=True
            )
        elif os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        elif os.path.exists("logo.jpg"):
            st.image("logo.jpg", use_container_width=True)
        else:
            st.markdown("<p style='text-align:center;'>(Please add logo.svg, logo.png or logo.jpg)</p>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"⚠️ Logo error: {e}")

    st.markdown("<h2 class='aybu-header'>SmartAttend</h2>", unsafe_allow_html=True)
    st.markdown("<div class='aybu-subheader'>Autonomous Attendance</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("⚙️ Session Control")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 Start", disabled=st.session_state.session_active):
            st.session_state.session_active = True
            st.session_state.manager.start_attendance_session()
            st.rerun()
    with col2:
        if st.button("🛑 Stop", disabled=not st.session_state.session_active):
            st.session_state.session_active = False
            st.session_state.manager.save_list()
            st.success("💾 Saved!")
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    st.subheader("📷 Camera Source")
    st.session_state.camera_index = st.number_input(
        "Camera device index",
        min_value=0,
        max_value=10,
        value=int(st.session_state.camera_index),
        step=1,
        help="Use your phone camera here if it appears as an external webcam on macOS. Common values are 1 or 2.",
    )
    st.caption(
        "If your phone is not listed as a webcam, use a companion app like Camo or DroidCam so macOS exposes it as a camera device."
    )

    st.markdown("---")
    st.subheader("📊 Live Metrics")
    
    total_val = st.session_state.total_students
    present_val = st.session_state.present_count
    absent_val = max(0, total_val - present_val)
    
    st.metric(label="🎓 Total Class", value=total_val)
    m_col1, m_col2 = st.columns(2)
    m_col1.metric(label="✅ Present", value=present_val)
    m_col2.metric(label="❌ Absent", value=absent_val)

    st.markdown("---")
    st.subheader("⬇️ Export Data")

    excel_buffer = io.BytesIO()
    st.session_state.manager.students_df.to_excel(excel_buffer, index=False)
    excel_data = excel_buffer.getvalue()

    st.download_button(
        label="📑 Download Excel Report",
        data=excel_data,
        file_name=f"Attendance_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        disabled=st.session_state.manager.students_df.empty
    )


# --- 4. MAIN LAYOUT ---
tab1, tab2 = st.tabs(["🎥 Live Attendance Dashboard", "➕ Add New Student"])

# ==== TAB 1: LIVE DASHBOARD ====
with tab1:
    col_vid, col_data = st.columns([6, 4])
    
    with col_vid:
        st.markdown("### Autonomous Tracking System", unsafe_allow_html=True)
        status_placeholder = st.empty()
        if st.session_state.session_active:
            status_placeholder.markdown("<div class='status-text' style='color:#007acc;'>🟢 Status: Session Active, Waiting for Faces...</div>", unsafe_allow_html=True)
        else:
            status_placeholder.markdown("<div class='status-text' style='color:#888;'>⚪ Status: Session Closed. Click 'Start' in the sidebar.</div>", unsafe_allow_html=True)

        src_col1, src_col2 = st.columns(2)
        with src_col1:
            use_cam = st.button("📸 Open Camera")
        with src_col2:
            st.session_state.stop_video = st.button("⏹️ Stop Stream")
            
        uploaded_video = st.file_uploader("🎬 Upload Video File for Processing", type=["mp4", "avi", "mov", "mkv"])
        use_uploaded_vid = st.button("▶️ Process Uploaded Video") if uploaded_video else False

        alert_placeholder = st.empty()
        video_placeholder = st.empty()
        
    with col_data:
        st.markdown("### Present Students Log")
        data_placeholder = st.empty()
        data_placeholder.dataframe(st.session_state.live_list, use_container_width=True, hide_index=True)

    if use_cam or use_uploaded_vid:
        if not st.session_state.session_active:
            st.warning("⚠️ Please 'Start' the attendance session from the sidebar first!")
        else:
            source = int(st.session_state.camera_index)
            if use_uploaded_vid:
                import tempfile
                # Save uploaded video to a temporary file since cv2.VideoCapture requires a path
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                tfile.write(uploaded_video.read())
                source = tfile.name

            cap = cv2.VideoCapture(source)
            status_placeholder.markdown("<div class='status-text' style='color:#28a745;'>🔄 Processing... Stream active.</div>", unsafe_allow_html=True)

            frame_count = 0

            while cap.isOpened() and not st.session_state.stop_video:
                ret, frame = cap.read()
                if not ret:
                    status_placeholder.warning("Video finished or camera inaccessible.")
                    break

                frame_count += 1
                if frame_count % Config.FRAME_SKIP != 0:
                    continue

                processed_frame, recognized_ids = st.session_state.analyzer.process_frame(frame)

                has_unknown = False
                if "Unknown" in recognized_ids or "Bilinmeyen" in recognized_ids:
                    has_unknown = True

                for person_id in recognized_ids:
                    if person_id not in ["Unknown", "Bilinmeyen"]:
                        handle_attendance(person_id)

                if has_unknown:
                    alert_placeholder.markdown(
                        "<div class='alert-box'>⚠️ SECURITY ALERT: Unidentified Person Detected!</div>", 
                        unsafe_allow_html=True
                    )
                else:
                    alert_placeholder.empty()

                rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(rgb_frame, channels="RGB", use_container_width=True)
                
                # Update Dataframe dynamically alongside the video
                data_placeholder.dataframe(st.session_state.live_list, use_container_width=True, hide_index=True)
                time.sleep(0.01)

            cap.release()
            st.session_state.stop_video = False
            status_placeholder.markdown("<div class='status-text' style='color:#888;'>⚪ Video stopped.</div>", unsafe_allow_html=True)

# ==== TAB 2: ADD NEW STUDENT ====
with tab2:
    st.markdown("### Student Registration Portal")
    st.write("Register a new student here. The AI encoding will automatically update and sync the database.")
    
    with st.form("add_student_form", clear_on_submit=True):
        col_f, col_l = st.columns(2)
        with col_f:
            f_name = st.text_input("First Name", placeholder="e.g., Jane")
        with col_l:
            l_name = st.text_input("Last Name", placeholder="e.g., Doe")
            
        s_id = st.text_input("Student ID Number", placeholder="e.g., 20260011")
        
        uploaded_img = st.file_uploader("Upload Clear Face Image", type=["jpg", "jpeg", "png"])
        
        submit = st.form_submit_button("Save Student & Train AI ✓")
        
        if submit:
            if not (f_name and l_name and s_id and uploaded_img):
                st.error("⚠️ All fields (First Name, Last Name, Student ID, and Image) are mandatory!")
            else:
                # Format to matching schema: firstname_lastname_id.jpg
                s_name = f"{f_name.strip()}_{l_name.strip()}".replace(" ", "_")
                filename = f"{s_name}_{s_id.strip()}.jpg".lower()
                filepath = os.path.join(Config.IMAGE_FOLDER, filename)
                
                # Check directory
                os.makedirs(Config.IMAGE_FOLDER, exist_ok=True)
                
                # Save Image
                with open(filepath, "wb") as f:
                    f.write(uploaded_img.read())
                st.success(f"📸 Image successfully saved as `{filename}`")
                
                # Trigger the Encoding process
                with st.spinner("🤖 Training AI with new face data. Please wait..."):
                    res = subprocess.run([sys.executable, "encoding.py"], capture_output=True, text=True)
                    
                    if res.returncode == 0:
                        st.success("✅ AI Face Encodings updated successfully!")
                        
                        # Resync Manager & Reload Analyzer into state
                        st.session_state.manager.sync_from_folder()
                        st.session_state.analyzer = FaceAnalyzer()
                        
                        # Update Tracker Metrics
                        st.session_state.total_students = len(st.session_state.manager.students_df)
                        
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to process AI encoding:\n{res.stderr}")
