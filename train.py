from ultralytics import YOLO

def main():
    # Load a pre-trained model (we use YOLOv8 nano here as a starting point)
    # It will use this as a base and fine-tune it for your dataset
    model = YOLO("yolov8n.pt") 

    # Train the model
    # Replace 'data.yaml' with the path to your dataset's yaml file
    # You can adjust epochs (how many times it goes through data) based on your needs
    results = model.train(
        data="fire-detection.v1i.yolov8/data.yaml",   # Path to your dataset config file
        epochs=50,          # Increased for better accuracy
        imgsz=640,          # Increased image size to detect small objects like a lighter flame
        device="cpu"        # Running on CPU as requested
    )

    print("Training complete! Your new model is saved in the 'runs/detect/train/weights' folder.")

if __name__ == "__main__":
    main()
