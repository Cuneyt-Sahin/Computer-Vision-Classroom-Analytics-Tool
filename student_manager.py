import os
import pandas as pd
from datetime import datetime
from config import Config

class StudentManager:
    def __init__(self, excel_path=Config.ATTENDANCE_EXCEL_PATH):
        self.excel_path = excel_path
        self.current_session_col = None 
        self.students_df = self.load_list()

    def load_list(self):
        """Loads the current list; if it doesn't exist, opens an empty table with just the school number and name columns."""
        if os.path.exists(self.excel_path):
            return pd.read_excel(self.excel_path, dtype={"School No": str})
        return pd.DataFrame(columns=["School No", "Full Name"])

    def parse_filename(self, filename):
        """Separates the name and number from the file name."""
        raw_name = os.path.splitext(filename)[0]
        parts = raw_name.split("_")

        if len(parts) < 2:
            return None, None

        school_no = parts[-1]
        full_name = " ".join(parts[:-1])
        return full_name, school_no

    def add_student(self, full_name, school_no):
        """Adds a new student to the list. Assigns '-' to past attendances."""
        if school_no in self.students_df["School No"].values:
            return False  # Student already exists

        new_student = {"School No": str(school_no), "Full Name": full_name}

        # If there are past attendance columns, this new student wasn't in the system
        # those days, so we place "-" (or a blank) in those past session columns.
        for col in self.students_df.columns:
            if col not in ["School No", "Full Name"]:
                new_student[col] = "-"

        # Add the new student to the DataFrame
        self.students_df = pd.concat(
            [self.students_df, pd.DataFrame([new_student])], ignore_index=True
        )
        return True

    def sync_from_folder(self, folder_path=Config.IMAGE_FOLDER):
        """Scans the folder and adds people not in the database to the list."""
        if not os.path.exists(folder_path):
            print(f"Folder not found: {folder_path}")
            return

        for filename in os.listdir(folder_path):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                name, no = self.parse_filename(filename)
                if name and no:
                    self.add_student(name, no)
        self.save_list()

    def start_attendance_session(self):
        """
        Runs when the camera/video feed opens.
        Opens a new column with the current date and marks everyone as '❌ Absent'.
        """
        now = datetime.now()
        # Column name format: "19-04-2026 | 10:30"
        self.current_session_col = now.strftime("%d-%m-%Y | %H:%M")

        # Open a new column and mark everyone as "Absent" by default
        self.students_df[self.current_session_col] = "❌ Absent"
        print(f"\n🟢 New Attendance Session Started: {self.current_session_col}")

    def update_attendance(self, school_no):
        """When the system recognizes a person, marks their status as 'Present' with the timestamp."""
        if not self.current_session_col:
            print("⚠️ Error: start_attendance_session() must be executed first!")
            return False

        if school_no in self.students_df["School No"].values:
            # Get arrival time (e.g., 10:35:12)
            time_str = datetime.now().strftime("%H:%M:%S")
            mark = f"✅ Present ({time_str})"

            self.students_df.loc[
                self.students_df["School No"] == school_no, self.current_session_col
            ] = mark
            return True
        return False

    def save_list(self):
        """Saves the student list to Excel."""
        self.students_df.to_excel(self.excel_path, index=False)
        print(f"💾 Attendance saved: {self.excel_path}")


if __name__ == "__main__":
    manager = StudentManager()

    manager.sync_from_folder()

    manager.start_attendance_session()

    manager.update_attendance("210209001")

    manager.update_attendance("123456789")

    manager.save_list()
