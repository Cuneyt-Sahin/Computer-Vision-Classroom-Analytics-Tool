# 🎓 SmartAttend | AI-Powered Automatic Attendance System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv)
![InsightFace](https://img.shields.io/badge/InsightFace-00B8D9?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

> ### 🔴 Real-Time AI Attendance Dashboard
> *Track classroom attendance instantly with face recognition, live alerts, and automatic Excel export.*

---

### ⚠️ Important Note Regarding Face Data
This project uses the images inside `student_images/` to build the face embedding database.

The generated embedding file `student_dataset.npz` is included in the repository, so the dashboard can run immediately.

If you add new students from the app, the system will automatically:
- save the student photo to `student_images/`
- regenerate `student_dataset.npz`
- refresh the recognition model in the dashboard

---

**SmartAttend** is a real-time attendance automation system that combines **face recognition**, **Streamlit UI**, and **Excel-based attendance logging**. It is designed for classroom environments where the operator needs a fast, clean, and reliable way to track attendance using a live camera or uploaded video.

## 📸 Dashboard Preview

> Add screenshots from your own dashboard here if you want a preview section.

---

## 🚀 Key Features

* **🧠 Real-Time Face Recognition:** Detects students from a live camera feed or an uploaded video.
* **👤 Student Registration Panel:** Add a new student directly from the interface with first name, last name, student ID, and face image.
* **🔄 Automatic Dataset Refresh:** New student images are encoded automatically in the background after upload.
* **📝 Live Attendance Log:** Shows recognized students in a live table beside the video feed.
* **📊 Attendance Session Tracking:** Starts a new attendance column for each session and marks students as present or absent.
* **📁 Excel Export:** Downloads the current attendance sheet as an `.xlsx` file.
* **📷 External Camera Support:** Can use an external camera device, including a phone camera exposed to macOS as a webcam.
* **🎨 AYBÜ-Themed UI:** Uses a dark blue sidebar, clean layout, and modern Streamlit styling.

---

## 🛠️ Tech Stack

* **Core:** Python 3.10+
* **UI/UX:** Streamlit, Custom CSS
* **Computer Vision:** OpenCV
* **Face Recognition:** InsightFace
* **Data Processing:** Pandas, NumPy
* **File Export:** OpenPyXL / Excel output via Pandas

---

## 📂 Project Structure

```bash
Computer-Vision-Classroom-Analytics-Tool/
├── app.py               # Main Streamlit dashboard
├── config.py            # Central configuration values
├── face_analyzer.py     # Face detection and matching logic
├── student_manager.py   # Student list and attendance session manager
├── encoding.py          # Builds student embeddings from student_images/
├── student_dataset.npz   # Saved face embeddings used by the recognizer
├── attendance_list.xlsx  # Attendance output file
├── student_images/      # Student face images
├── logo.jpg             # Sidebar logo
└── README.md            # Documentation
```

---

## ⚡ Getting Started
Follow these steps to run the project locally.

### 1) Clone the Repository
```bash
git clone https://github.com/username/Computer-Vision-Classroom-Analytics-Tool.git
cd Computer-Vision-Classroom-Analytics-Tool
```

### 2) Create and Activate a Virtual Environment
It is recommended to use a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows
```

### 3) Install Dependencies

```bash
pip install streamlit opencv-python pandas numpy insightface onnxruntime openpyxl
```

### 4) Run the Dashboard
Launch the application. It will open in your default browser at `localhost:8501`.

```bash
streamlit run app.py
```

---

## 💡 How It Works?

- **Input:** The operator starts a session and selects either the built-in camera, an external camera, or an uploaded video.
- **Face Analysis:** `face_analyzer.py` detects faces and compares them against the embedding database.
- **Attendance Logic:** `student_manager.py` opens a new session column and marks recognized students as present.
- **Dataset Update:** When a new student is added, the app saves the image and regenerates embeddings automatically.
- **Live Output:** The recognized faces and attendance table are updated in real time beside the video feed.

---

## 📊 Model / System Behavior

- Attendance is confirmed after repeated recognition hits to reduce false positives.
- Unknown faces trigger a warning on the dashboard.
- The system keeps the attendance list in Excel format for easy sharing and reporting.

---

## 🧾 Typical Workflow

1. Click **Start** in the sidebar.
2. Choose a camera source or upload a video.
3. Let the system recognize students in real time.
4. Add a new student from the second tab if needed.
5. Download the updated attendance file with **Download Excel Report**.

---

## 👨‍💻 Author

Cüneyt Şahin

[LinkedIn Profile](https://www.linkedin.com/in/cuneyt-sahin)

[GitHub Profile](https://github.com/Cuneyt-Sahin)