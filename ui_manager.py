import streamlit as st

class UIManager:
    """Manages User Interface configurations, themes, and multi-language support (i18n)."""
    
    UI_TEXT = {
        "tr": {
            "app_title": "AYBÜ SmartAttend | Otomatik Yoklama",
            "app_subtitle": "Otonom Yoklama",
            "language": "Dil",
            "language_help": "Arayüz dilini seçin.",
            "session_control": "⚙️ Oturum Kontrolü",
            "start": "🟢 Başlat",
            "stop": "🛑 Durdur",
            "reset_all": "🗑️ Seçilenleri ve Tüm Listeyi Temizle",
            "delete_record": "Öğrenciyi Veritabanından Tamamen Sil (No)",
            "view_list": "👁️ Listeyi Görüntüle",
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
            "session_closed": "⚪ Durum: Oturum kapalı. Kamerayı Aç'a basın.",
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
            "reset_all": "🗑️ Clear List and All Status",
            "delete_record": "Delete Student from Database (ID)",
            "view_list": "👁️ View List",
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
            "session_closed": "⚪ Status: Session Closed. Click 'Open Camera'.",
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

    @staticmethod
    def t(lang: str, key: str, **kwargs) -> str:
        """Retrieves and formats a multi-language text safely based on the interface language."""
        text = UIManager.UI_TEXT.get(lang, UIManager.UI_TEXT["en"]).get(key, key)
        return text.format(**kwargs)

    @staticmethod
    def apply_theme():
        """Injects custom CSS global styles to Streamlit interface."""
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
            </style>
        """, unsafe_allow_html=True)