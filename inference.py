import os
import numpy as np
from keras.models import load_model
from tensorflow.keras.utils import load_img, img_to_array
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import tensorflow as tf

# Define the perceptual_loss function
def perceptual_loss(y_true, y_pred):
    vgg = tf.keras.applications.VGG16(include_top=False, weights='imagenet', input_shape=(256, 256, 3))
    vgg.trainable = False
    vgg_model = tf.keras.models.Model(inputs=vgg.input, outputs=vgg.get_layer('block3_conv3').output)
    y_true_features = vgg_model(y_true)
    y_pred_features = vgg_model(y_pred)
    return tf.reduce_mean(tf.square(y_true_features - y_pred_features))

# Define the combined_loss function
def combined_loss(y_true, y_pred):
    mse_loss = tf.keras.losses.MeanSquaredError()(y_true, y_pred)
    ssim_loss_value = tf.reduce_mean(1 - tf.image.ssim(y_true, y_pred, max_val=1.0))
    perceptual_loss_value = perceptual_loss(y_true, y_pred)
    return mse_loss + 0.5 * ssim_loss_value + 0.5 * perceptual_loss_value

# Load the model with custom loss functions
model = load_model('best_model.keras', custom_objects={'perceptual_loss': perceptual_loss, 'combined_loss': combined_loss})
print("Model loaded successfully!")

def preprocess_image(img_path, img_size=(512, 512)):
    try:
        img = load_img(img_path, target_size=img_size)
        img = img_to_array(img) / 255.0
        img = img.astype('float32')  # Ensure the correct dtype
        original_img = load_img(img_path)
        original_size = original_img.size
        return np.expand_dims(img, axis=0), original_size
    except Exception as e:
        print(f"Error in preprocess_image: {e}")
        raise

def resize_image(img_array, original_size):
    try:
        img = (img_array * 255).astype(np.uint8)
        img = cv2.resize(img, (original_size[0], original_size[1]), interpolation=cv2.INTER_LINEAR)
        img = img.astype('float32') / 255.0  # Ensure the correct dtype after resizing
        return img
    except Exception as e:
        print(f"Error in resize_image: {e}")
        raise

def display_images(original, predicted):
    try:
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes[0].imshow(original.astype('float32'))  # Ensure the correct dtype
        axes[0].set_title('Original Image')
        axes[0].axis('off')
        axes[1].imshow(predicted.astype('float32'))  # Ensure the correct dtype
        axes[1].set_title('Predicted Image')
        axes[1].axis('off')
        plt.show()
    except Exception as e:
        print(f"Error in display_images: {e}")
        raise

# Set the paths for the test images
test_folder_X = "F:/AI Project/data/test/DNxHQ"
test_folder_Y = "F:/AI Project/data/test/H264"
output_folder = "F:/AI Project/data/results"

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Get the list of test images
test_images_X = os.listdir(test_folder_X)

for img_name in test_images_X:
    img_path_X = os.path.join(test_folder_X, img_name)
    img_path_Y = os.path.join(test_folder_Y, img_name)

    try:
        img_X, original_size = preprocess_image(img_path_X)
        img_Y, _ = preprocess_image(img_path_Y)  # Load the Y image to display later

        print(f"Preprocessed image shape: {img_X.shape}, dtype: {img_X.dtype}")
        print(f"Original size: {original_size}")

        pred = model.predict(img_X)
        pred = pred.astype('float32')  # Ensure the correct dtype

        print(f"Prediction shape: {pred.shape}, dtype: {pred.dtype}")

        original_image_X = np.squeeze(img_X, axis=0)
        original_image_Y = np.squeeze(img_Y, axis=0)
        predicted_image = np.squeeze(pred, axis=0)
        predicted_image = predicted_image.astype('float32')  # Ensure the correct dtype

        print(f"Original image shape after squeeze: {original_image_X.shape}, dtype: {original_image_X.dtype}")
        print(f"Predicted image shape after squeeze: {predicted_image.shape}, dtype: {predicted_image.dtype}")

        predicted_image_resized = resize_image(predicted_image, original_size)
        predicted_image_resized = predicted_image_resized.astype('float32')  # Ensure the correct dtype

        print(f"Predicted image shape after resize: {predicted_image_resized.shape}, dtype: {predicted_image_resized.dtype}")

        # Save the original and predicted images
        original_image_display = Image.fromarray((original_image_X * 255).astype(np.uint8))
        predicted_image_display = Image.fromarray((predicted_image_resized * 255).astype(np.uint8))

        original_image_display.save(os.path.join(output_folder, f"original_{img_name}"))
        predicted_image_display.save(os.path.join(output_folder, f"predicted_{img_name}"))

        # Display the images
        display_images(np.array(original_image_display).astype('float32') / 255.0, predicted_image_resized)
    except Exception as e:
        print(f"Error during processing {img_name}: {e}")
