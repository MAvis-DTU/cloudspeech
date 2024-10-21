from __init__ import *
import cv2
import numpy as np
from models.yolo_model import ObjectDetect
import time
import os
from openai import OpenAI
import base64
import requests
import threading

class VideoStreamCustom:
    def __init__(self, model_name=None, 
                       object_detect=True, 
                       yolo_threshold=0.3, 
                       device='cpu', 
                       vision=False, 
                       verbose=False, 
                       vision_freq=5) -> None:
        self.object_detect = object_detect
        self.yolo_threshold = yolo_threshold
        self.model_name = model_name
        self.vision = vision
        self.vision_freq = vision_freq

        # Load the OpenAI API key from the file
        with open('credentials/openaiKey.txt', 'r') as f:
            os.environ['gpt4key'] = f.read()

        # Set the API key
        self.api_key = os.getenv("gpt4key")

        if device == 'mps':
            #set fallback to 1 to enable MPS
            print("MPS enabled")
            if verbose:
                print("-----------------")
                print("MPS enabled")

        if object_detect:
            self.OD = ObjectDetect(model_name, yolo_threshold=yolo_threshold, device=device, verbose=False)

    def analyze_image_with_openai(self,image_path="vision_output.jpg"):
        # Function to encode the image
        def encode_image(image_path="vision_output.jpg"):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        # Encode the image
        base64_image = encode_image(image_path)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Give a description of the environment"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        } 
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # save the response to a text file vision.txt
        with open("vision.txt", "w") as f:
            f.write("A description of the environment:\n\n" +response.json()['choices'][0]['message']['content'])
            f.close()

        return response.json()
    
    def plot_boxes(self, results, frame):
        """
        Takes a frame and its results as input, and plots the bounding boxes and label on to the frame.
        :param results: contains labels and coordinates predicted by model on the given frame.
        :param frame: Frame which has been scored.
        :return: Frame with bounding boxes and labels ploted on it.
        """
        if 'obb' in self.model_name:
            labels, cord, labels_conf, angle_rad = results
        else:
            labels, cord, labels_conf = results
        n = len(labels)

        for i in range(n):  
            # plot polygon around the object based on the coordinates cord
            if 'obb' in self.model_name:
                x1, y1, x2, y2, x3, y3, x4, y4 = cord[i].flatten()
                x1, y1, x2, y2, x3, y3, x4, y4 = int(x1), int(y1), int(x2), int(y2), int(x3), int(y3), int(x4), int(y4)
                # draw lines between the corners
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.line(frame, (x2, y2), (x3, y3), (0, 255, 0), 2)
                cv2.line(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                cv2.line(frame, (x4, y4), (x1, y1), (0, 255, 0), 2)
                # plot label on the object
                cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                # plot a line with angle_rad as the angle of the object
                angle_sin = np.sin(angle_rad[i].detach().cpu().numpy())
                angle_cos = np.cos(angle_rad[i].detach().cpu().numpy())
                # plot the line from the center of the object
                x_center = (x1 + x2 + x3 + x4) // 4
                y_center = (y1 + y2 + y3 + y4) // 4
                cv2.line(frame, (x_center, y_center), (x_center + int(500 * angle_cos), y_center + int(500 * angle_sin)), (0, 0, 255), 2)
                cv2.line(frame, (x_center, y_center), (x_center - int(500 * angle_cos), y_center - int(500 * angle_sin)), (0, 0, 255), 2)

            else:
                x1, y1, x2, y2 = cord[i].flatten()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # plot label on the object
                cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        return frame
    
    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        return self.OD.classes[int(x)]

    def __call__(self, video):
        frame_count = 0
        start_time = time.time()
        vision_start_time = time.time()
        while True:
            try:
                success, image = video.read()
                if not success:
                    print("Warning: Failed to read frame from stream, skipping...")
                    time.sleep(0.1)  # Short delay before retrying
                    continue
                
                # Flip the image horizontally
                image = cv2.flip(image, 1)
                # every 5 seconds save the frame to the disk 
                if time.time() - vision_start_time > self.vision_freq:
                    cv2.imwrite(f"vision_output.jpg", image)
                    vision_start_time = time.time()
                    if self.vision:
                        # run self.analyze_image_with_openai() in a thread
                        # to avoid blocking the main thread
                        thread1 = threading.Thread(target=self.analyze_image_with_openai)
                        thread1.start()
                
                # Resize image to 0.8 of the original size
                # image = cv2.resize(image, (0, 0), fx=0.8, fy=0.8)
                results = self.OD.score_frame(image)  # This takes a lot of time if ran on CPU
                # plot the bounding boxes and labels on the frame
                image = self.plot_boxes(results, image)
                # Save the labels to a text file
                predicted_classes = [self.OD.model.names[int(i)] for i in results[0]]
                with open("objects.txt", "r+") as f:
                    data = f.read()
                    #remove data from file
                    f.seek(0)
                    f.truncate()
                    #write new data to file
                    if len(predicted_classes) > 0:
                        f.write(f'Objects Pepper can see ' + str(", ".join(predicted_classes)))
                    else:
                        f.write("No objects detected")
                    f.close()       
                    
                frame_count += 1
                elapsed_time = time.time() - start_time
                elapsed_update_time = time.time() - os.path.getmtime("vision.txt")
                fps = frame_count / elapsed_time
                cv2.putText(image, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(image, f'Since update: {elapsed_update_time:.0f}s', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                
                cv2.imshow('Video', image)

                # end_time = time.time()  # Record the end time
                # frame_time = end_time - start_time
                # print(f"Time between frames: {frame_time:.4f} seconds")

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

        video.release()
        cv2.destroyAllWindows()