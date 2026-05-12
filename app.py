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


UI_TEXT = {
    "tr": {
        "app_title": "AYBÜ SmartAttend | Otomatik Yoklama",
        "app_subtitle": "Otonom Yoklama",
        "language": "Dil",
        "language_help": "Arayüz dilini seçin.",
        "session_control": "⚙️ Oturum Kontrolü",
        "start": "🟢 Başlat",
        "stop": "🛑 Durdur",
        "camera_settings": "📷 Kamera Ayarları",
        "camera_index": "Kamera cihaz numarası",
        "camera_help": "Telefon kameranız macOS'ta harici kamera olarak görünüyorsa buradan seçebilirsiniz. Yaygın değerler 1 veya 2'dir.",
        "camera_caption": "Telefonunuz kamera olarak görünmüyorsa Camo veya DroidCam gibi bir uygulama kullanın.",
        "live_stats": "📊 Canlı İstatistikler",
        "export_data": "⬇️ Veri Dışa Aktarma",
        "download_excel": "📑 Excel Raporunu İndir",
        "tab_dashboard": "🎥 Canlı Yoklama Paneli",
        "tab_student": "➕ Yeni Öğrenci Ekle",
        "attendance_ratio": "📊 Yoklama Oranı",
        "present_students": "👥 Gelen Öğrenciler",
        "tracking_system": "🎥 Otonom Takip Sistemi",
        "session_active": "🟢 Durum: Oturum aktif, yüzler bekleniyor...",
        "session_closed": "⚪ Durum: Oturum kapalı. Soldaki 'Başlat' düğmesine basın.",
        "open_camera": "📸 Kamerayı Aç",
        "stop_stream": "⏹️ Akışı Durdur",
        "upload_video": "🎬 İşlenecek Video Dosyası Yükle",
        "process_video": "▶️ Yüklenen Videoyu İşle",
        "start_warning": "⚠️ Lütfen önce soldan yoklama oturumunu 'Başlat' düğmesiyle açın!",
        "camera_error": "⚠️ Kamera açılamadı. Kenar çubuğundaki kamera numarasını değiştirin (0, 1, 2, ...).",
        "stream_active": "🔄 İşleniyor... Akış aktif.",
        "video_finished": "Video bitti ya da kameraya erişilemiyor.",
        "security_alert": "⚠️ GÜVENLİK UYARISI: Tanımlanamayan kişi tespit edildi!",
        "session_warning": "⚠️ **Uyarı**: Bu oturumda tanımlanamayan kişiler tespit edildi ve hâlâ sınıfta olabilir. Lütfen yoklama listesini kontrol edin.",
        "close": "Kapat",
        "student_portal": "📝 Öğrenci Kayıt Paneli",
        "student_portal_desc": "Yeni bir öğrenci burada kaydedilir. Yapay zekâ kodlaması veritabanını otomatik günceller.",
        "first_name": "Ad",
        "last_name": "Soyad",
        "student_id": "Öğrenci No",
        "image_upload": "Net Yüz Fotoğrafı Yükleyin",
        "save_student": "Öğrenciyi Kaydet ve AI'yi Eğit ✓",
        "mandatory_fields": "⚠️ Tüm alanlar (Ad, Soyad, Öğrenci No ve Fotoğraf) zorunludur!",
        "saved_image": "📸 Görüntü başarıyla `{filename}` olarak kaydedildi",
        "training": "🤖 Yeni yüz verisiyle AI eğitiliyor. Lütfen bekleyin...",
        "encoding_ok": "✅ AI yüz kodlamaları başarıyla güncellendi!",
        "encoding_fail": "❌ AI kodlama işlemi başarısız oldu:\n{stderr}",
        "logo_error": "⚠️ Logo hatası: {error}",
        "logo_missing": "(Lütfen logo.svg, logo.png veya logo.jpg ekleyin)",
        "saved": "💾 Kaydedildi!",
    },
    "en": {
        "app_title": "AYBÜ SmartAttend | Auto Attendance",
        "app_subtitle": "Autonomous Attendance",
        "language": "Language",
        "language_help": "Choose the interface language.",
        "session_control": "⚙️ Session Control",
        "start": "🟢 Start",
        "stop": "🛑 Stop",
        "camera_settings": "📷 Camera Settings",
        "camera_index": "Camera device index",
        "camera_help": "Use your phone camera here if it appears as an external webcam on macOS. Common values are 1 or 2.",
        "camera_caption": "If your phone is not listed as a webcam, use a companion app like Camo or DroidCam.",
        "live_stats": "📊 Live Statistics",
        "export_data": "⬇️ Data Export",
        "download_excel": "📑 Download Excel Report",
        "tab_dashboard": "🎥 Live Attendance Dashboard",
        "tab_student": "➕ Add New Student",
        "attendance_ratio": "📊 Attendance Ratio",
        "present_students": "👥 Present Students",
        "tracking_system": "🎥 Autonomous Tracking System",
        "session_active": "🟢 Status: Session Active, Waiting for Faces...",
        "session_closed": "⚪ Status: Session Closed. Click 'Start' in the sidebar.",
        "open_camera": "📸 Open Camera",
        "stop_stream": "⏹️ Stop Stream",
        "upload_video": "🎬 Upload Video File for Processing",
        "process_video": "▶️ Process Uploaded Video",
        "start_warning": "⚠️ Please 'Start' the attendance session from the sidebar first!",
        "camera_error": "⚠️ Camera could not be opened. Try a different camera index in the sidebar (0, 1, 2, ...).",
        "stream_active": "🔄 Processing... Stream active.",
        "video_finished": "Video finished or camera inaccessible.",
        "security_alert": "⚠️ SECURITY ALERT: Unidentified Person Detected!",
        "session_warning": "⚠️ **Warning**: Unrecognized persons were detected during this session and may still be present in the classroom. Please review the attendance log.",
        "close": "Close",
        "student_portal": "📝 Student Registration Portal",
        "student_portal_desc": "Register a new student here. The AI encoding will automatically update and sync the database.",
        "first_name": "First Name",
        "last_name": "Last Name",
        "student_id": "Student ID Number",
        "image_upload": "Upload Clear Face Image",
        "save_student": "Save Student & Train AI ✓",
        "mandatory_fields": "⚠️ All fields (First Name, Last Name, Student ID, and Image) are mandatory!",
        "saved_image": "📸 Image successfully saved as `{filename}`",
        "training": "🤖 Training AI with new face data. Please wait...",
        "encoding_ok": "✅ AI Face Encodings updated successfully!",
        "encoding_fail": "❌ Failed to process AI encoding:\n{stderr}",
        "logo_error": "⚠️ Logo error: {error}",
        "logo_missing": "(Please add logo.svg, logo.png or logo.jpg)",
        "saved": "💾 Saved!",
    },
}


def t(key: str, **kwargs) -> str:
    lang = st.session_state.get("language", "tr")
    text = UI_TEXT.get(lang, UI_TEXT["en"]).get(key, key)
    return text.format(**kwargs)


st.set_page_config(
    page_title="AYBÜ SmartAttend | Auto Attendance",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    /* Toast notification (bottom-right, closable) */
    .toast-notification {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: #b91c1c;
        color: #ffffff;
        padding: 20px 24px;
        padding-right: 45px;
        border-radius: 10px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        z-index: 10000;
        max-width: 400px;
        font-size: 14px;
        line-height: 1.5;
        animation: slideIn 0.4s ease-out;
    }
    .toast-notification h3 {
        margin: 0 0 8px 0;
        font-size: 16px;
        font-weight: 700;
    }
    .toast-notification p {
        margin: 0;
        font-size: 13px;
    }
    .toast-close {
        position: absolute;
        top: 12px;
        right: 12px;
        background: none;
        border: none;
        color: #ffffff;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0.8;
        transition: opacity 0.2s;
    }
    .toast-close:hover {
        opacity: 1;
    }
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes fadeOut {
        from {
            opacity: 1;
        }
        to {
            opacity: 0;
        }
    }
    }
    """, unsafe_allow_html=True)


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
        st.session_state.session_unknown_detected = False
        st.session_state.toast_dismissed = False
        st.session_state.language = "en"
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

    st.markdown("<h2 class='aybu-header'>SmartAttend</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='aybu-subheader'>{t('app_subtitle')}</div>", unsafe_allow_html=True)

    st.subheader(t("session_control"))
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("start"), disabled=st.session_state.session_active):
            st.session_state.session_active = True
            st.session_state.manager.start_attendance_session()
            # reset unknown flag for a fresh session
            st.session_state.session_unknown_detected = False
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
        present_val = st.session_state.present_count
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


tab1, tab2 = st.tabs([t("tab_dashboard"), t("tab_student")])

with tab1:

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
    
    chart_col, table_col = st.columns(2)
    
    with chart_col:
        with st.container(border=True):
            st.subheader(t("attendance_ratio"))
            
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
            st.subheader(t("present_students"))
            data_placeholder = st.empty()
            data_placeholder.dataframe(st.session_state.live_list, use_container_width=True, hide_index=True)
    
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
            if use_cam and not st.session_state.session_active:
                st.session_state.session_active = True
                st.session_state.manager.start_attendance_session()
                st.session_state.session_unknown_detected = False
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

                        has_unknown = False
                        if "Unknown" in recognized_ids or "Bilinmeyen" in recognized_ids:
                            has_unknown = True
                            st.session_state.session_unknown_detected = True

                        for person_id in recognized_ids:
                            if person_id not in ["Unknown", "Bilinmeyen"]:
                                handle_attendance(person_id)

                        if has_unknown:
                            alert_placeholder.markdown(
                                f"<div class='alert-box'>{t('security_alert')}</div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            alert_placeholder.empty()

                        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                        video_placeholder.image(rgb_frame, channels="RGB", use_container_width=True)

                        data_placeholder.dataframe(st.session_state.live_list, use_container_width=True, hide_index=True)
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
