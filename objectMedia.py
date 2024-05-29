
# STEP 1: Import the necessary modules.
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from collections import defaultdict

def objectDetection():
    # STEP 1.1: 
    ROW_SIZE = 10  # pixels
    FONT_SIZE = 4
    MARGIN = 30*FONT_SIZE
    FONT_THICKNESS = 4
    TEXT_COLOR = (255, 0, 0)  # red

    def visualize(
        image,
        detection_result
    ) -> np.ndarray:
        """Draws bounding boxes on the input image and return it.
        Args:
            image: The input RGB image.
            detection_result: The list of all "Detection" entities to be visualize.
        Returns:
            Image with bounding boxes.
        """
        for detection in detection_result.detections:
            # Draw bounding_box
            bbox = detection.bounding_box
            start_point = bbox.origin_x, bbox.origin_y
            end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
            cv2.rectangle(image, start_point, end_point, TEXT_COLOR, 3)

            # Draw label and score
            category = detection.categories[0]
            category_name = category.category_name
            probability = round(category.score, 2)
            result_text = category_name + ' (' + str(probability) + ')'
            text_location = (MARGIN + bbox.origin_x, MARGIN + ROW_SIZE + bbox.origin_y)
            cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)
            
        return image

    # STEP 2: Create an ObjectDetector object.
    base_options = python.BaseOptions(model_asset_path='efficientdet_lite0.tflite')
    options = vision.ObjectDetectorOptions(base_options=base_options,
                                        score_threshold=0.3)
    detector = vision.ObjectDetector.create_from_options(options)


    #IMAGE_FILE = 'image.jpg'

    import cv2




    # get webcam
    cap = cv2.VideoCapture(1)



    # get image from webcam
    while True:
        ret, frame = cap.read()

        # STEP 3: Load the input image.
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

        # STEP 4: Detect objects in the input image.
        detection_result = detector.detect(image,)

        
        # STEP 5: Process the detection result. In this case, visualize it.
        image_copy = np.copy(image.numpy_view())
        annotated_image = visualize(image_copy, detection_result)
        rgb_annotated_image = cv2.cvtColor(image_copy, cv2.COLOR_BGR2RGB)
        #cv2_imshow(rgb_annotated_image)

        # make a dictionary of objects and their scores
        predicted_classes = defaultdict()
        
        # TODO: loop through the detection results and add them to the dictionary
        for i in range(len(detection_result.detections)):
            objects = defaultdict()
            objects[detection_result.detections[i].categories[0].category_name] = detection_result.detections[0].categories[0].score
            #objects['box_xy'] = (detection_result.detections[0].bounding_box.origin_x, detection_result.detections[0].bounding_box.origin_y)
            #objects['box_width_height'] = (detection_result.detections[0].bounding_box.width, detection_result.detections[0].bounding_box.height)

            # add the dictionary to the predicted_classes dictionary
            predicted_classes[i] = objects

        with open("objects.txt", "r+") as f:
            data = f.read()
            #remove data from file
            f.seek(0)
            f.truncate()
            #write new data to file
            if data != predicted_classes:
                if len(predicted_classes) > 0:
                    visible_objects = [list(predicted_classes[i].keys()) for i in range(len(predicted_classes.keys()))]
                    f.write(f'Objects Pepper can see ' + str(visible_objects))
                else:
                    f.write("No objects detected")
                f.close()

        # show the frame
        frame = cv2.cvtColor(rgb_annotated_image, cv2.COLOR_BGR2RGB)
        cv2.imshow('frame', frame)
        

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == '__main__':
    objectDetection()
