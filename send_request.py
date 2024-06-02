import requests
import json

# Define the path to the image
image_path = 'data/videos/frames/1080p/DNxHQ_frames_1080p/ACTIVE_TENNIS_FEMALE_5_f1_i26.jpg'

# URL of the Flask server endpoint
url = 'http://localhost:5000/predict'

# Open the image file in binary mode
with open(image_path, 'rb') as img_file:
    # Create a dictionary to store the file data
    files = {'image': img_file}

    # Send the POST request
    response = requests.post(url, files=files)

    # Print the server response text
    response_json = response.json()
    
    # Print the first few elements for verification
    prediction = response_json.get("prediction", [])
    if prediction:
        print("First few elements of the prediction:")
        print(prediction[:2])  # Adjust the slicing as needed
    else:
        print("No prediction found in the response.")
