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
from attendance_list import AttendanceList
from ui_manager import UIManager


def t(key: str, **kwargs) -> str:
    lang = st.session_state.get("language", "tr")
    return UIManager.t(lang, key, **kwargs)


st.set_page_config(
    page_title="AYBÜ SmartAttend | Auto Attendance",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

UIManager.apply_theme()


if "initialized" not in st.session_state:
    with st.spinner("⏳ Loading AI Models... (Please wait)"):
        st.session_state.manager = StudentManager()
        st.session_state.manager.sync_from_folder()
        st.session_state.analyzer = FaceAnalyzer()
        st.session_state.attendance_list = AttendanceList(st.session_state.manager)
        
        st.session_state.session_active = False
        st.session_state.total_students = len(st.session_state.manager.students_df)
        st.session_state.camera_index = 1
        st.session_state.toast_dismissed = False
        st.session_state.session_unknown_detected = False
        st.session_state.unknown_hits = 0
        st.session_state.language = "en"
        st.session_state.initialized = True
        st.session_state.stop_video = False

def handle_attendance(student_id):
    """Processes a recognized student ID."""
    if not st.session_state.session_active:
        return
    st.session_state.attendance_list.handle_attendance(student_id)

@st.dialog("📋 Yoklama Listesi / Attendance List", width="large")
def show_attendance_list_popup():
    st.dataframe(st.session_state.manager.students_df, use_container_width=True, hide_index=True)
    if st.button("Kapat / Close", use_container_width=True):
        st.rerun()

with st.sidebar:
    try:
        if os.path.exists("logo.svg"):
            import base64
            with open("logo.svg", "rb") as f:
                base64_svg = base64.b64encode(f.read()).decode("utf-8")
            svg_uri = f"data:image/svg+xml;base64,{base64_svg}"
            st.markdown(
                f'<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 18px; padding: 8px;"><img src="{svg_uri}" style="width: 120px; height: 120px; border-radius: 8px;"></div>', 
                unsafe_allow_html=True
            )
        elif os.path.exists("logo.png"):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image("logo.png", width=180)
        elif os.path.exists("logo.jpg"):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image("logo.jpg", width=180)
        else:
            st.markdown(f"<p style='text-align:center; color:#9ca3af; font-size:0.9em;'>{t('logo_missing')}</p>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(t("logo_error", error=e))

    st.selectbox(
        t("language"),
        options=["tr", "en"],
        format_func=lambda x: "Türkçe" if x == "tr" else "English",
        index=0 if st.session_state.language == "tr" else 1,
        help=t("language_help"),
        key="language_selector",
        on_change=lambda: None,
    )
    st.session_state.language = st.session_state.language_selector

    st.markdown("---")
    st.markdown(f"<div class='aybu-subheader'>{t('session_control')}</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("start"), disabled=st.session_state.session_active):
            st.session_state.session_active = True
            st.session_state.attendance_list.reset_session()
            st.session_state.manager.start_attendance_session()
            # Her yeni video/kamera baslatildiginda uyarilari sifirla
            st.session_state.session_unknown_detected = False
            st.session_state.unknown_hits = 0
            st.session_state.toast_dismissed = False
            st.rerun()
    with col2:
        if st.button(t("stop"), disabled=not st.session_state.session_active):
            st.session_state.session_active = False
            st.session_state.manager.save_list()
            st.success(t("saved"))
            time.sleep(1)
            st.rerun()
    
    with st.expander(t("camera_settings")):
        st.session_state.camera_index = st.number_input(
            t("camera_index"),
            min_value=0,
            max_value=10,
            value=int(st.session_state.camera_index),
            step=1,
            help=t("camera_help"),
        )
        st.caption(t("camera_caption"))

    with st.expander(t("live_stats")):
        total_val = st.session_state.total_students
        present_val = st.session_state.attendance_list.present_count
        absent_val = max(0, total_val - present_val)
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric(label="🎓 Total", value=total_val)
        m_col2.metric(label="✅ Present", value=present_val)
        m_col3.metric(label="❌ Absent", value=absent_val)


    with st.expander(t("export_data")):
        excel_buffer = io.BytesIO()
        st.session_state.manager.students_df.to_excel(excel_buffer, index=False)
        excel_data = excel_buffer.getvalue()

        st.download_button(
            label=t("download_excel"),
            data=excel_data,
            file_name=f"Attendance_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            disabled=st.session_state.manager.students_df.empty
        )

    st.markdown("---")
    st.markdown(f"<div class='aybu-subheader'>📝 {t('live_stats')} Management</div>", unsafe_allow_html=True)
    
    if st.button(t("view_list"), use_container_width=True):
        show_attendance_list_popup()
    
    if st.button(t("reset_all"), use_container_width=True):
        st.session_state.attendance_list.reset_all()
        st.success("Tüm veriler sıfırlandı." if st.session_state.language == "tr" else "All data reset.")
        time.sleep(1)
        st.rerun()
        
    del_id = st.text_input(t("delete_record"), placeholder="örn. 20260011")
    if st.button("➖ {0}".format("Tamamen Sil" if st.session_state.language == "tr" else "Delete Completely"), use_container_width=True):
        if del_id:
            res = st.session_state.attendance_list.delete_record(del_id.strip())
            if res:
                st.session_state.total_students = len(st.session_state.manager.students_df)
                
                with st.spinner("Yüz veritabanı temizleniyor... (AI Syncing)" if st.session_state.language == "tr" else "Cleaning face database... (AI Syncing)"):
                    subprocess.run([sys.executable, "encoding.py"], capture_output=True, text=True)
                    st.session_state.analyzer = FaceAnalyzer()
                
                st.success(f"{del_id} numaralı öğrenci tüm sistemden (Fotoğraf, Excel, AI Veritabanı) tamamen silindi." if st.session_state.language == "tr" else f"Student {del_id} permanently deleted from the entire system (Photo, Excel, AI DB).")
                time.sleep(2)
            else:
                st.error("Kayıtlı öğrenci bulunamadı." if st.session_state.language == "tr" else "Registered student not found.")
            st.rerun()


tab1, tab2 = st.tabs([t("tab_dashboard"), t("tab_student")])

with tab1:

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        
        metric_total = col1.empty()
        metric_present = col2.empty()
        metric_absent = col3.empty()
        metric_rate = col4.empty()
        
    chart_col, table_col = st.columns(2)
    
    with chart_col:
        with st.container(border=True):
            st.subheader(t("attendance_ratio"))
            chart_placeholder = st.empty()
            
    with table_col:
        with st.container(border=True):
            st.subheader(t("present_students"))
            data_placeholder = st.empty()

    def update_dashboard_ui():
        total_students = st.session_state.total_students
        present_count = st.session_state.attendance_list.present_count
        absent_count = max(0, total_students - present_count)
        attendance_rate = (present_count / max(1, total_students) * 100)
        
        metric_total.metric("📊 Total", total_students)
        metric_present.metric("✅ Present", present_count)
        metric_absent.metric("❌ Absent", absent_count)
        metric_rate.metric("📈 Rate", f"{attendance_rate:.0f}%")
        
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
            
            chart_placeholder.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"pie_{time.time()}")
        
        data_placeholder.dataframe(st.session_state.attendance_list.get_live_list(), use_container_width=True, hide_index=True)

    # Initial render
    update_dashboard_ui()
    
    with st.container(border=True):
        st.subheader(t("tracking_system"))
        
        status_placeholder = st.empty()
        if st.session_state.session_active:
            status_placeholder.markdown(f"<div class='status-text'>{t('session_active')}</div>", unsafe_allow_html=True)
        else:
            status_placeholder.markdown(f"<div class='status-text'>{t('session_closed')}</div>", unsafe_allow_html=True)

        src_col1, src_col2 = st.columns(2)
        with src_col1:
            use_cam = st.button(t("open_camera"), use_container_width=True)
        with src_col2:
            st.session_state.stop_video = st.button(t("stop_stream"), use_container_width=True)
            
        uploaded_video = st.file_uploader(t("upload_video"), type=["mp4", "avi", "mov", "mkv"])
        use_uploaded_vid = st.button(t("process_video")) if uploaded_video else False

        alert_placeholder = st.empty()
        video_placeholder = st.empty()
        
        if use_cam or use_uploaded_vid:
            if not st.session_state.session_active:
                st.session_state.session_active = True
                st.session_state.manager.start_attendance_session()
            
            # Her yeni video/kamera baslatildiginda uyarilari sifirla
            st.session_state.session_unknown_detected = False
            st.session_state.unknown_hits = 0
            st.session_state.toast_dismissed = False

            if not st.session_state.session_active:
                st.warning(t("start_warning"))
            else:
                source = int(st.session_state.camera_index)
                if use_uploaded_vid:
                    import tempfile
                    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                    tfile.write(uploaded_video.read())
                    source = tfile.name

                cap = None
                if use_cam:
                    camera_candidates = []
                    for candidate in [source, 0, 1, 2, 3]:
                        if candidate not in camera_candidates:
                            camera_candidates.append(candidate)

                    for candidate in camera_candidates:
                        test_cap = cv2.VideoCapture(candidate)
                        if test_cap.isOpened():
                            cap = test_cap
                            source = candidate
                            break
                        test_cap.release()
                else:
                    cap = cv2.VideoCapture(source)

                if cap is None or not cap.isOpened():
                    st.error(t("camera_error"))
                else:
                    status_placeholder.markdown(f"<div class='status-text'>{t('stream_active')}</div>", unsafe_allow_html=True)

                    frame_count = 0

                    while cap.isOpened() and not st.session_state.stop_video:
                        ret, frame = cap.read()
                        if not ret:
                            status_placeholder.warning(t("video_finished"))
                            break

                        frame_count += 1
                        if frame_count % Config.FRAME_SKIP != 0:
                            continue

                        processed_frame, recognized_ids = st.session_state.analyzer.process_frame(frame)

                        has_unknown_in_frame = False
                        if "Unknown" in recognized_ids or "Bilinmeyen" in recognized_ids:
                            has_unknown_in_frame = True
                            st.session_state.unknown_hits += 1
                            if st.session_state.unknown_hits >= 15:
                                st.session_state.session_unknown_detected = True
                        else:
                            # Also reset if there's no unknown in the frame to prevent random jumps 
                            # accumulating over a long time triggering it
                            st.session_state.unknown_hits = 0

                        has_new_update = False
                        for person_id in recognized_ids:
                            if person_id not in ["Unknown", "Bilinmeyen"]:
                                # Attempt attendance update
                                success = st.session_state.attendance_list.handle_attendance(person_id)
                                if success:
                                    has_new_update = True

                        # Sadece belirli bir miktar ust uste bilinmeyen gorduyse anlik kirmizi uyariyi ver
                        if st.session_state.unknown_hits >= 8:
                            alert_placeholder.markdown(
                                f"<div class='alert-box'>{t('security_alert')}</div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            alert_placeholder.empty()

                        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                        video_placeholder.image(rgb_frame, channels="RGB", use_container_width=True)

                        # Update UI stats and tables live ONLY when a new student is marked present
                        if has_new_update:
                            update_dashboard_ui()
                        time.sleep(0.01)

                    cap.release()
                    st.session_state.stop_video = False
                    status_placeholder.markdown(f"<div class='status-text'>{t('session_closed')}</div>", unsafe_allow_html=True)

                    if st.session_state.session_unknown_detected and not st.session_state.toast_dismissed:
                        st.write("---")
                        st.warning(t("session_warning"))
                        
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col2:
                            if st.button(t("close"), key="close_toast_btn", use_container_width=True):
                                st.session_state.toast_dismissed = True
                                st.rerun()

with tab2:
    with st.container():
        st.subheader(t("student_portal"))
        st.write(t("student_portal_desc"))
        
        with st.form("add_student_form", clear_on_submit=True):
            col_f, col_l = st.columns(2)
            with col_f:
                f_name = st.text_input(t("first_name"), placeholder="e.g., Jane")
            with col_l:
                l_name = st.text_input(t("last_name"), placeholder="e.g., Doe")
                
            s_id = st.text_input(t("student_id"), placeholder="e.g., 20260011")
            
            uploaded_img = st.file_uploader(t("image_upload"), type=["jpg", "jpeg", "png"])
            
            submit = st.form_submit_button(t("save_student"))
            
            if submit:
                if not (f_name and l_name and s_id and uploaded_img):
                    st.error(t("mandatory_fields"))
                else:
                    s_name = f"{f_name.strip()}_{l_name.strip()}".replace(" ", "_")
                    filename = f"{s_name}_{s_id.strip()}.jpg".lower()
                    filepath = os.path.join(Config.IMAGE_FOLDER, filename)
                    

                    os.makedirs(Config.IMAGE_FOLDER, exist_ok=True)
                    

                    with open(filepath, "wb") as f:
                        f.write(uploaded_img.read())
                    st.success(t("saved_image", filename=filename))
                    
                    # Trigger the Encoding process
                    with st.spinner(t("training")):
                        res = subprocess.run([sys.executable, "encoding.py"], capture_output=True, text=True)
                        
                        if res.returncode == 0:
                            st.success(t("encoding_ok"))
                            
                            # Resync Manager & Reload Analyzer into state
                            st.session_state.manager.sync_from_folder()
                            st.session_state.analyzer = FaceAnalyzer()
                            
                            # Update Tracker Metrics
                            st.session_state.total_students = len(st.session_state.manager.students_df)
                            
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(t("encoding_fail", stderr=res.stderr))
