import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from config import Config

def main():
    providers = Config.PROVIDERS
    app = FaceAnalysis(
        name=Config.MODEL_NAME, 
        root="~/.insightface",
        providers=providers,
    )
    app.prepare(ctx_id=0, det_size=Config.DET_SIZE)

    IMAGE_DATA_FOLDER = Config.IMAGE_FOLDER
    SAVE_PATH = Config.EMBEDDINGS_FILE
    
    if not os.path.exists(IMAGE_DATA_FOLDER):
        print(f"❌ Error: Image folder '{IMAGE_DATA_FOLDER}' not found!")
        return

    database = {}
    
    print(f"Scanning folder '{IMAGE_DATA_FOLDER}'...")
    for filename in os.listdir(IMAGE_DATA_FOLDER):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(IMAGE_DATA_FOLDER, filename)
            img = cv2.imread(img_path)
            if img is None: 
                print(f"⚠️ Warning: Could not read image '{filename}'")
                continue

            faces = app.get(img)

            if faces:
                embedding = faces[0].embedding
                name = os.path.splitext(filename)[0]
                database[name] = embedding
                print(f"✅ Extracted face from '{filename}' -> Named '{name}'")
            else:
                print(f"❌ No faces detected in '{filename}'")

    if database:
        np.savez_compressed(SAVE_PATH, **database)
        print(f"\n🎉 Process completed! {len(database)} faces saved to {SAVE_PATH}.")
    else:
        print(f"\n⚠️ No faces found to save in folder.")

if __name__ == "__main__":
    main()
