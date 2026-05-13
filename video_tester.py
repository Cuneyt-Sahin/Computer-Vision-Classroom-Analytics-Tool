import cv2
from config import Config
from face_analyzer import FaceAnalyzer

class VideoTester:
    def __init__(self, analyzer: FaceAnalyzer):
        self.analyzer = analyzer

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
            processed_frame, recognized_persons = self.analyzer.process_frame(frame)

          
            if recognized_persons:
                print(f"Frame {frame_count}: Detected IDs: {recognized_persons}")

            cv2.imshow("SmartAttend - Face Recognition", processed_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    analyzer = FaceAnalyzer()
    tester = VideoTester(analyzer)

   
    tester.run_video_test("a.mp4")
