import cv2
from inference import get_model
import supervision as sv
import PIL.Image
import google.generativeai as genai
import json
import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))



# Load a pre-trained YOLOv8n model
model = get_model(model_id="myeyes/33", api_key="2ApphPvEv99dpc6PLGEA")

# Initialize the video capture from the camera
cap = cv2.VideoCapture(0)  # 0 is typically the default camera

# Create supervision annotators
bounding_box_annotator = sv.BoundingBoxAnnotator()
label_annotator = sv.LabelAnnotator()

# Configure the Google Generative AI
genai.configure(api_key="AIzaSyDpSs5G9QzHoc3r0Y85M_bLuy3eTdEg8mE")

while True:
    # Capture a frame from the camera
    ret, frame = cap.read()
    if not ret:
        break

    # Run inference on the captured frame
    results = model.infer(frame)[0]

    # Load the results into the supervision Detections API
    detections = sv.Detections.from_inference(results)

    # Annotate the frame with our inference results
    annotated_frame = bounding_box_annotator.annotate(
        scene=frame, detections=detections)
    annotated_frame = label_annotator.annotate(
        scene=annotated_frame, detections=detections)

    # Display the annotated frame
    cv2.imshow('Annotated Camera Feed', annotated_frame)

    # Check if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        # Save the image
        image_path = 'cloth_detected.png'
        cv2.imwrite(image_path, frame)
        print('Image saved.')

        # Send the image to Gemini Pro Vision
        img = PIL.Image.open(image_path)
        model = genai.GenerativeModel('gemini-pro-vision')

        response = model.generate_content(["First, give a thorough explanation of the person's clothing, concentrating on a single item. Consider how it looks in light of the newest fashions. For conciseness and clarity, use bullet points. Second, please provide additional fashion advice based on what the wearer is now wearing. These should be divided into separate sections with titles that read 'feedback' and 'recommendations'", img])
        print(response.text)

        



     
        break

# Release the video capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()