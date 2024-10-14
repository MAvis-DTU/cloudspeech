from __init__ import *
import cv2
from models.video_stream import VideoStreamCustom

def yolo_object_detection(model_name, object_detect=True, yolo_threshold=0.8, verbose=False, device='cpu'):
    video_stream = VideoStreamCustom(model_name=model_name, object_detect=object_detect, device=device, yolo_threshold=yolo_threshold, verbose=verbose)
    cap = cv2.VideoCapture(0)
    video_stream(cap)
