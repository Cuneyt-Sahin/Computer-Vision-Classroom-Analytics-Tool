import os

class Config:
    MODEL_NAME = "buffalo_l"
    PROVIDERS =[
        "CoreMLExecutionProvider",
        "CUDAExecutionProvider",
        "CPUExecutionProvider",
    ]
    DET_SIZE = (640, 640)
    THRESHOLD = 0.65

    # file paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMAGE_FOLDER = os.path.join(BASE_DIR, "student_images")
    EMBEDDINGS_FILE = os.path.join(BASE_DIR, "student_dataset.npz")

    # video source settings
    VIDEO_SOURCE = 0
    FRAME_SKIP = 3  # Process every 3rd frame to reduce CPU load

    # attendance settings
    ATTENDANCE_EXCEL_PATH = os.path.join(BASE_DIR, "attendance_list.xlsx")
    MATCH_THRESHOLD_PERCENTAGE = 50.0  # Percentage needed for a positive match
    REQUIRED_VOTING_HITS = 2  # Number of frames a person must be detected to be marked present
