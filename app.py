from flask import Flask, jsonify
import tensorflow as tf
from keras import backend as K
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import io
from PIL import Image
import base64
import os

app = Flask(__name__)

# Define the custom loss functions
def perceptual_loss(y_true, y_pred):
    vgg = tf.keras.applications.VGG16(include_top=False, weights='imagenet', input_shape=(256, 256, 3))
    vgg.trainable = False
    vgg_model = tf.keras.models.Model(inputs=vgg.input, outputs=vgg.get_layer('block3_conv3').output)
    y_true_features = vgg_model(y_true)
    y_pred_features = vgg_model(y_pred)
    return tf.reduce_mean(tf.square(y_true_features - y_pred_features))

def combined_loss(y_true, y_pred):
    mse_loss = tf.keras.losses.MeanSquaredError()(y_true, y_pred)
    ssim_loss_value = tf.reduce_mean(1 - tf.image.ssim(y_true, y_pred, max_val=1.0))
    perceptual_loss_value = perceptual_loss(y_true, y_pred)
    return mse_loss + 0.5 * ssim_loss_value + 0.5 * perceptual_loss_value

# Load your Keras model with the custom loss functions
model = tf.keras.models.load_model('best_model.keras', custom_objects={'perceptual_loss': perceptual_loss, 'combined_loss': combined_loss})

# Function to preprocess the image
def preprocess_image(image_path, img_size=(512, 512)):
    img = load_img(image_path, target_size=img_size)
    img = img_to_array(img) / 255.0  # Normalize as during training
    return np.expand_dims(img, axis=0)

# Function to resize and convert numpy array to base64
def resize_and_convert_to_base64(img_array, target_size=(1920, 1080)):
    img = Image.fromarray((img_array * 255).astype(np.uint8))
    img = img.resize(target_size, Image.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

@app.route('/process-image', methods=['POST'])
def process_image():
    try:
        image_path = "F:/AI Project/temp screenshots/chosen_frame.png"  # Path to the saved frame
        if not os.path.exists(image_path):
            return jsonify({'error': 'No frame found'}), 400

        # Preprocess the image
        features = preprocess_image(image_path)
        # Get predictions from the model
        predictions = model.predict(features)
        # Assuming you need the first prediction
        prediction = predictions[0]
        # Resize and convert the prediction to base64
        transformed_image = resize_and_convert_to_base64(prediction)
        # Return the transformed image as a base64 string
        return jsonify({'transformed_image': transformed_image})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
