import streamlit as st
import cv2
import pandas as pd
import time
from datetime import datetime
import os
import io
import subprocess
import sys
import plotly.graph_objects as go
import plotly.express as px
from config import Config
from face_analyzer import FaceAnalyzer
from student_manager import StudentManager


st.set_page_config(
    page_title="AYBÜ SmartAttend | Auto Attendance",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 1. CSS ile Konteynerları "Karta" Dönüştür
st.markdown("""
    <style>
    /* Ana arkaplanı çok hafif gri yap ki beyaz kartlar öne çıksın */
    .stApp {
        background-color: #fcfcfc !important;
    }
    
    body, .stMainBlockContainer {
        background-color: #fcfcfc !important;
    }

    /* border=True olan tüm container'ları yakala ve gölge ekle */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: 1px solid #eee !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        padding: 15px !important;
    }
    
    /* Metrics Styling */
    [data-testid="metric-container"] {
        background: #ffffff !important;
        border-radius: 8px;
        border: 1px solid #eee !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03) !important;
        padding: 12px !important;
    }
    
    /* Button Styling */
    .stButton>button {
        background: #3b82f6 !important;
        color: #ffffff !important;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 8px 16px !important;
        transition: all 0.3s ease;
        box-shadow: 0 2px 6px rgba(59, 130, 246, 0.15);
    }
    
    .stButton>button:hover {
        background: #2563eb !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        transform: translateY(-1px);
    }
    
    /* Text Colors */
    body, .stMarkdown, .stApp {
        color: #1f2937 !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1f2937 !important;
        font-weight: 700 !important;
    }
    
    .stSubheader {
        color: #1f2937 !important;
        font-weight: 700 !important;
    }
    
    /* Messages */
    .stSuccess {
        background: #f0fdf4 !important;
        border-left: 3px solid #22c55e !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 2px 6px rgba(34, 197, 94, 0.08);
    }
    
    .stError {
        background: #fef2f2 !important;
        border-left: 3px solid #ef4444 !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 2px 6px rgba(239, 68, 68, 0.08);
    }
    
    .stWarning {
        background: #eff6ff !important;
        border-left: 3px solid #3b82f6 !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 2px 6px rgba(59, 130, 246, 0.08);
    }
    
    /* Hide Tab Border */
    .stTabs {
        border: none !important;
    }
    
    /* Hide Dividers */
    hr {
        border: none !important;
        height: 0 !important;
        margin: 0 !important;
    }
    
    /* Font */
    html, body, .stApp {
        font-family: 'Inter', 'Segoe UI', 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* SmartAttend Header Styling */
    .aybu-header {
        text-align: center !important;
        color: #3b82f6 !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    
    .aybu-subheader {
        text-align: center !important;
        color: #9ca3af !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        margin-bottom: 12px !important;
    }
    """, unsafe_allow_html=True)


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
                f'<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 15px; padding: 5px;"><img src="{svg_uri}" style="width: 50px; height: 50px; border-radius: 8px;"></div>', 
                unsafe_allow_html=True
            )
        elif os.path.exists("logo.png"):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image("logo.png", width=130)
        elif os.path.exists("logo.jpg"):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image("logo.jpg", width=130)
        else:
            st.markdown("<p style='text-align:center; color:#9ca3af; font-size:0.9em;'>(Please add logo.svg, logo.png or logo.jpg)</p>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"⚠️ Logo error: {e}")

    st.markdown("<h2 class='aybu-header'>SmartAttend</h2>", unsafe_allow_html=True)
    st.markdown("<div class='aybu-subheader'>Autonomous Attendance</div>", unsafe_allow_html=True)

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
    
    # Kamera Ayarları Expander
    with st.expander("📷 Kamera Ayarları"):
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

    # Canlı İstatistikler Expander
    with st.expander("📊 Canlı İstatistikler"):
        total_val = st.session_state.total_students
        present_val = st.session_state.present_count
        absent_val = max(0, total_val - present_val)
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric(label="🎓 Total", value=total_val)
        m_col2.metric(label="✅ Present", value=present_val)
        m_col3.metric(label="❌ Absent", value=absent_val)

    # Veri Dışa Aktarma Expander
    with st.expander("⬇️ Veri Dışa Aktarma"):
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
    # Metrics Row
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        
        total_students = st.session_state.total_students
        present_count = st.session_state.present_count
        absent_count = max(0, total_students - present_count)
        
        with col1:
            st.metric("📊 Total", total_students)
        with col2:
            st.metric("✅ Present", present_count)
        with col3:
            st.metric("❌ Absent", absent_count)
        with col4:
            attendance_rate = (present_count / max(1, total_students) * 100)
            st.metric("📈 Rate", f"{attendance_rate:.0f}%")
    
    # Charts & Table Row
    chart_col, table_col = st.columns(2)
    
    with chart_col:
        with st.container(border=True):
            st.subheader("📊 Attendance Ratio")
            
            if total_students > 0:
                chart_data = pd.DataFrame({
                    'Status': ['Present', 'Absent'],
                    'Count': [present_count, absent_count]
                })
                
                fig = go.Figure(data=[go.Pie(
                    labels=chart_data['Status'],
                    values=chart_data['Count'],
                    hole=0.4,
                    marker=dict(colors=['#10b981', '#f87171']),
                    textinfo='label+percent',
                    hoverinfo='label+value+percent'
                )])
                
                fig.update_layout(
                    font=dict(size=10, color='#1f2937'),
                    paper_bgcolor='#ffffff',
                    plot_bgcolor='#ffffff',
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=200,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with table_col:
        with st.container(border=True):
            st.subheader("👥 Present Students")
            data_placeholder = st.empty()
            data_placeholder.dataframe(st.session_state.live_list, use_container_width=True, hide_index=True)
    
    # Tracking System Row (Full Width)
    with st.container(border=True):
        st.subheader("🎥 Autonomous Tracking System")
        
        status_placeholder = st.empty()
        if st.session_state.session_active:
            status_placeholder.markdown("<div class='status-text'>🟢 Status: Session Active, Waiting for Faces...</div>", unsafe_allow_html=True)
        else:
            status_placeholder.markdown("<div class='status-text'>⚪ Status: Session Closed. Click 'Start' in the sidebar.</div>", unsafe_allow_html=True)

        src_col1, src_col2 = st.columns(2)
        with src_col1:
            use_cam = st.button("📸 Open Camera", use_container_width=True)
        with src_col2:
            st.session_state.stop_video = st.button("⏹️ Stop Stream", use_container_width=True)
            
        uploaded_video = st.file_uploader("🎬 Upload Video File for Processing", type=["mp4", "avi", "mov", "mkv"])
        use_uploaded_vid = st.button("▶️ Process Uploaded Video") if uploaded_video else False

        alert_placeholder = st.empty()
        video_placeholder = st.empty()
        
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
                status_placeholder.markdown("<div class='status-text'>🔄 Processing... Stream active.</div>", unsafe_allow_html=True)

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
                status_placeholder.markdown("<div class='status-text'>⚪ Video stopped.</div>", unsafe_allow_html=True)

# ==== TAB 2: ADD NEW STUDENT ====
with tab2:
    with st.container():
        st.subheader("📝 Student Registration Portal")
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
