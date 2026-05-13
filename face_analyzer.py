import cv2
import numpy as np
from insightface.app import FaceAnalysis
from config import Config

def sanitize_text_for_cv2(text):
    """Replaces Turkish characters with ASCII equivalents for OpenCV putText."""
    replacements = {
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'İ': 'I',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    }
    for tr_char, eng_char in replacements.items():
        text = text.replace(tr_char, eng_char)
    return text

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
                # 1) If confidence is above the match threshold -> recognized
                # 2) If confidence is below UNKNOWN_THRESHOLD_PERCENTAGE -> explicitly Unknown
                # 3) If confidence is between those two -> Uncertain 
                if max_similarity > self.threshold:
                    parts = best_match.split("_")
                    if len(parts) >= 2:
                        display_name = f"{parts[0]} {parts[1]}"
                        recognized_ids.append(parts[-1])  # Add number for attendance
                    else:
                        display_name = best_match
                        recognized_ids.append(best_match)

                    display_text = f"{display_name} ({max_similarity:.1f}%)"
                    color = (0, 255, 0)  # Green
                elif max_similarity < Config.UNKNOWN_THRESHOLD_PERCENTAGE:
                    display_text = f"Unknown ({max_similarity:.1f}%)"
                    color = (0, 0, 255)  # Red
                    recognized_ids.append("Unknown")
                else:
                    # Mid-range matches — show as uncertain but do not add to recognized list
                    display_text = f"Uncertain ({max_similarity:.1f}%)"
                    color = (0, 165, 255)  # Orange

            # Draw on Screen
            bbox = face.bbox.astype(int)
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            clean_display_text = sanitize_text_for_cv2(display_text)
            
            cv2.putText(
                frame,
                clean_display_text,
                (bbox[0], bbox[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

        return frame, recognized_ids
