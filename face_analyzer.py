import cv2
import numpy as np
from insightface.app import FaceAnalysis
from config import Config


class FaceAnalyzer:
    def __init__(
        self,
        embeddings_path=Config.EMBEDDINGS_FILE,
        threshold=Config.MATCH_THRESHOLD_PERCENTAGE,
        providers=Config.PROVIDERS,
        det_size=Config.DET_SIZE,
    ):
        self.threshold = threshold
        self.providers = providers

        print("🧠 Loading AI Model...")
        self.app = FaceAnalysis(name=Config.MODEL_NAME, providers=self.providers)
        self.app.prepare(ctx_id=0, det_size=det_size)

        print(f"📂 Loading Database: {embeddings_path}")
        try:
            self.known_faces_data = np.load(embeddings_path, allow_pickle=True)
            self.known_names = self.known_faces_data.files
        except Exception as e:
            print(f"⚠️ Error: Could not read embedding file! ({e})")
            self.known_names = []

    def calculate_similarity(self, embedding1, embedding2):
        """
        Calculates Cosine Similarity between two vectors and scales it to 0-100%.
        """
        # Fix vector lengths to 1 (Normalize)
        vec1 = embedding1 / np.linalg.norm(embedding1)
        vec2 = embedding2 / np.linalg.norm(embedding2)

        # Calculate pure similarity
        sim = np.dot(vec1, vec2)

        # Convert to percentage (Treat negative values as 0)
        return max(0, sim) * 100

    def process_frame(self, frame):
        """
        Takes a single frame, finds faces, draws boxes, and returns the processed frame.
        Also returns a list of recognized school numbers (or names) in this frame.
        """
        recognized_ids = []  # List of recognized people in this frame
        faces = self.app.get(frame)

        for face in faces:
            current_embedding = face.normed_embedding
            best_match = "Unknown"
            max_similarity = 0.0

            # Compare against everyone in the database
            for name in self.known_names:
                db_embedding = self.known_faces_data[name]
                match_percentage = self.calculate_similarity(
                    current_embedding, db_embedding
                )

                if match_percentage > max_similarity:
                    max_similarity = match_percentage
                    best_match = name

            # Visualization Decisions
            if max_similarity > self.threshold:
                # If filename is formatted as Name_Surname_SchoolNo, format it neatly
                parts = best_match.split("_")
                if len(parts) >= 2:
                    display_name = f"{parts[0]} {parts[1]}"  # Just Name and Surname
                    recognized_ids.append(parts[-1])  # Add number to the list (For attendance)
                else:
                    display_name = best_match
                    recognized_ids.append(best_match)

                display_text = f"{display_name} ({max_similarity:.1f}%)"
                color = (0, 255, 0) 
            else:
                display_text = f"Unknown ({max_similarity:.1f}%)"
                color = (0, 0, 255) 
                recognized_ids.append("Unknown")

            # Draw on Screen
            bbox = face.bbox.astype(int)
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            cv2.putText(
                frame,
                display_text,
                (bbox[0], bbox[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

        return frame, recognized_ids

    def run_video_test(self, video_path=Config.VIDEO_SOURCE):
        """
        Used to test the system in an OpenCV window.
        In the real application, this loop runs inside Streamlit.
        """
        try:
            source = int(video_path)
        except ValueError:
            source = video_path
            
        cap = cv2.VideoCapture(source)
        print("\n▶️ Analysis starting... Press 'q' to exit.")

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # FPS Optimization: Process every N frames
            if frame_count % Config.FRAME_SKIP != 0:
                continue

            # Send frame to Class and get processed version
            processed_frame, recognized_persons = self.process_frame(frame)

            # Print to terminal for Debug
            if recognized_persons:
                print(f"Frame {frame_count}: Detected IDs: {recognized_persons}")

            cv2.imshow("SmartAttend - Face Recognition", processed_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    analyzer = FaceAnalyzer()

    # Test with your own video or '0' for camera 
    analyzer.run_video_test("a.mp4")
