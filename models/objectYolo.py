from __init__ import *
import cv2
from models.video_stream import VideoStreamCustom
import argparse


def yolo_object_detection(model_name, object_detect=True, yolo_threshold=0.8, vision=False, verbose=False, device='cpu', vision_freq=5, camera=0):
    video_stream = VideoStreamCustom(model_name=model_name, object_detect=object_detect, device=device, yolo_threshold=yolo_threshold, vision=vision, verbose=verbose, vision_freq=vision_freq)
    cap = cv2.VideoCapture(camera)
    video_stream(cap)

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='YOLO Object Detection')
    parser.add_argument('--model', type=str, default='models/yolo11n.pt', help='Path to the YOLO model file')
    parser.add_argument('--object_detect', type=bool, default=True, help='Enable or disable object detection')
    parser.add_argument('--threshold', type=float, default=0.8, help='YOLO detection threshold')
    parser.add_argument('--verbose', type=bool, default=False, help='Enable verbose logging')
    parser.add_argument('--vision', action='store_true', help='Enable vision model to analyze the image')
    parser.add_argument('--device', type=str, default='cpu', help='The device to run the od on ps(cpu or mps for MacOS)')
    parser.add_argument('--vision_freq', type=int, default=5, help='Frequency of video frames to process')
    parser.add_argument('--camera', type=int, default=0, help='Camera index to use')
    # Parse the arguments
    args = parser.parse_args()

    # Call the yolo_object_detection function with parsed arguments
    yolo_object_detection(
        model_name=args.model,
        object_detect=args.object_detect,
        yolo_threshold=args.threshold,
        vision=args.vision,
        verbose=args.verbose,
        device=args.device,
        vision_freq=args.vision_freq,
        camera=args.camera
    )
