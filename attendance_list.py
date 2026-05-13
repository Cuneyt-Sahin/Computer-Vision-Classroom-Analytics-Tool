import pandas as pd
from datetime import datetime
import os
from config import Config

class AttendanceList:
    def __init__(self, manager):
        self.manager = manager
        self.reset_session()

    def reset_session(self):
        """Resets the live attendance state for a new session."""
        self.hit_counts = {}
        self.live_list = pd.DataFrame(columns=["School No", "Full Name", "Entry Time", "Status"])
        self.present_count = 0
        self.session_unknown_detected = False

    def handle_attendance(self, student_id):
        """Processes a recognized student ID."""
        # Hit Counter Logic
        if student_id not in self.hit_counts:
            self.hit_counts[student_id] = 0
        
        # Don't increment or process if already recorded
        is_already_present = student_id in self.live_list["School No"].values
        if is_already_present:
            return False
            
        self.hit_counts[student_id] += 1

        # Threshold Check
        if self.hit_counts[student_id] == Config.REQUIRED_VOTING_HITS:
            success = self.manager.update_attendance(student_id)
            if success:
                self.present_count += 1
                
                # Fetch full name
                student_row = self.manager.students_df[self.manager.students_df["School No"] == student_id].iloc[0]
                full_name = student_row["Full Name"]
                time_str = datetime.now().strftime("%H:%M:%S")

                new_record = pd.DataFrame([{
                    "School No": student_id,
                    "Full Name": full_name,
                    "Entry Time": time_str,
                    "Status": "✅ Present"
                }])
                self.live_list = pd.concat([new_record, self.live_list], ignore_index=True)
                return True
        return False
        
    def get_live_list(self):
        """Returns the current live attendance list."""
        return self.live_list
        
    def delete_record(self, student_id):
        """Remove a student completely from the database (Excel) and the live list."""
        student_id = str(student_id).strip()
        found_in_live = False
        
        if student_id in self.live_list["School No"].values:
            # Remove from live DataFrame
            self.live_list = self.live_list[self.live_list["School No"] != student_id].copy()
            self.live_list.reset_index(drop=True, inplace=True)
            
            # Reset hit count
            if student_id in self.hit_counts:
                del self.hit_counts[student_id]
                
            # Decrease count
            self.present_count = max(0, self.present_count - 1)
            found_in_live = True
            
        # Update underlying manager - Completely remove the row and save the excel file
        student_exists = student_id in self.manager.students_df["School No"].values
        if student_exists:
            # Remove entirely from the main DataFrame
            self.manager.students_df = self.manager.students_df[self.manager.students_df["School No"] != student_id]
            self.manager.students_df.reset_index(drop=True, inplace=True)
            
            # Instantly save to update the .xlsx file
            self.manager.save_list()
            
            # Delete the student's image from the folder
            if os.path.exists(Config.IMAGE_FOLDER):
                for filename in os.listdir(Config.IMAGE_FOLDER):
                    name_part, _ = os.path.splitext(filename)
                    if name_part.endswith(f"_{student_id}"):
                        file_path = os.path.join(Config.IMAGE_FOLDER, filename)
                        try:
                            os.remove(file_path)
                            print(f"Deleted image: {file_path}")
                        except Exception as e:
                            print(f"Error deleting image {file_path}: {e}")
                            
            return True
            
        return found_in_live
        
    def reset_all(self):
        """Clears all attendance data."""
        self.reset_session()
        self.manager.reset_attendance()
