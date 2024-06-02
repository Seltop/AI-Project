import sys
import tensorflow as tf
from keras import backend as K
from tensorflow.keras.preprocessing.image import img_to_array, load_img, save_img
import numpy as np

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

def preprocess_image(image_path, img_size=(512, 512)):
    img = load_img(image_path, target_size=img_size)
    img = img_to_array(img) / 255.0  # Normalize as during training
    return np.expand_dims(img, axis=0)

def save_image(img_array, path):
    img = (img_array[0] * 255).astype(np.uint8)
    save_img(path, img)

def process_frame(input_path, output_path):
    # Preprocess the image
    img = preprocess_image(input_path)
    # Get predictions from the model
    predictions = model.predict(img)
    # Save the processed image
    save_image(predictions, output_path)

if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    process_frame(input_path, output_path)
