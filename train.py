import os
import numpy as np
from keras import layers, models
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import load_img, img_to_array
from tqdm import tqdm
from keras.callbacks import EarlyStopping, ModelCheckpoint
import keras.callbacks
import logging
import tensorflow as tf
from keras import layers, models, backend as K
from keras.applications import VGG16
from keras.models import Model
from tensorflow.keras.mixed_precision import Policy, set_global_policy

# Set mixed precision policy
policy = Policy('mixed_float16')
set_global_policy(policy)

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

resolution = 512

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

original_height = 1080
original_width = 1920

vgg = VGG16(include_top=False, weights='imagenet', input_shape=(resolution, resolution, 3))
vgg.trainable = False
vgg_model = models.Model(inputs=vgg.input, outputs=vgg.get_layer('block3_conv3').output)

def unet_model(input_size=(resolution, resolution, 3)):
    inputs = layers.Input(input_size)

    # Encoder
    conv1 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(inputs)
    conv1 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(conv1)
    pool1 = layers.MaxPooling2D(pool_size=(2, 2))(conv1)

    conv2 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(pool1)
    conv2 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(conv2)
    pool2 = layers.MaxPooling2D(pool_size=(2, 2))(conv2)

    conv3 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(pool2)
    conv3 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(conv3)
    pool3 = layers.MaxPooling2D(pool_size=(2, 2))(conv3)

    conv4 = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(pool3)
    conv4 = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(conv4)
    pool4 = layers.MaxPooling2D(pool_size=(2, 2))(conv4)

    conv5 = layers.Conv2D(1024, (3, 3), activation='relu', padding='same')(pool4)
    conv5 = layers.Conv2D(1024, (3, 3), activation='relu', padding='same')(conv5)

    # Decoder
    up6 = layers.Conv2DTranspose(512, (2, 2), strides=(2, 2), padding='same')(conv5)
    merge6 = layers.Concatenate()([conv4, up6])
    conv6 = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(merge6)
    conv6 = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(conv6)

    up7 = layers.Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same')(conv6)
    merge7 = layers.Concatenate()([conv3, up7])
    conv7 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(merge7)
    conv7 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(conv7)

    up8 = layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(conv7)
    merge8 = layers.Concatenate()([conv2, up8])
    conv8 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(merge8)
    conv8 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(conv8)

    up9 = layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(conv8)
    merge9 = layers.Concatenate()([conv1, up9])
    conv9 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(merge9)
    conv9 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(conv9)
    
    conv10 = layers.Conv2D(3, (1, 1), activation='sigmoid')(conv9)

    return models.Model(inputs, conv10)

def ssim_loss(y_true, y_pred):
    return 1 - tf.reduce_mean(tf.image.ssim(y_true, y_pred, max_val=1.0))

def combined_loss(y_true, y_pred):
    mse_loss = K.mean(K.square(y_pred - y_true))
    ssim_loss_value = ssim_loss(y_true, y_pred)
    # Ensure both have the same data type
    mse_loss = tf.cast(mse_loss, dtype=tf.float32)
    ssim_loss_value = tf.cast(ssim_loss_value, dtype=tf.float32)
    return mse_loss + 0.5 * ssim_loss_value  # Adjust the weight as needed

def load_images(path, img_size=(resolution, resolution), max_images=None):
    images = []
    filenames = []
    file_list = os.listdir(path)
    if max_images:
        file_list = file_list[:max_images]

    for filename in tqdm(file_list, desc=f'Loading images from {path}'):
        try:
            img_path = os.path.join(path, filename)
            img = load_img(img_path, target_size=img_size)
            img = img_to_array(img) / 255.0
            images.append(img)
            filenames.append(filename)
        except Exception as e:
            logging.error(f'Error loading image {filename}: {e}')
        # Debugging: Print image shape
        logging.debug(f'Loaded image {filename} with shape {img.shape}')

        # Check memory usage and break if needed
        if len(images) % 100 == 0:
            logging.info(f'Loaded {len(images)} images so far...')

    # Debugging: Print overall dataset shape
    logging.info(f'Loaded {len(images)} images in total.')
    return np.array(images), filenames

class TQDMProgressBar(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        print(f'Epoch {epoch + 1}: {logs}')

    def on_train_batch_end(self, batch, logs=None):
        self.prog_bar.update(1)

    def on_train_begin(self, logs=None):
        self.prog_bar = tqdm(total=self.params['steps'], desc='Training', position=0, leave=True)

    def on_train_end(self, logs=None):
        self.prog_bar.close()

input_images_path = "data/videos/frames/1080p/DNxHQ_frames_1080p"
output_images_path = "data/videos/frames/1080p/H264_frames_1080p"

input_images, input_filenames = load_images(input_images_path, img_size=(resolution, resolution))
print("Finished loading DNxHQ images.")
output_images, output_filenames = load_images(output_images_path, img_size=(resolution, resolution))
print("Finished loading H264 images.")

assert set(input_filenames) == set(output_filenames), "Mismatch filename"
print("No mismatch")

input_images = [img for _, img in sorted(zip(input_filenames, input_images))]
output_images = [img for _, img in sorted(zip(output_filenames, output_images))]
print("Finished sorting")

input_images = np.array(input_images)
output_images = np.array(output_images)
print("Array transformation complete")

X_train, X_val, y_train, y_val = train_test_split(input_images, output_images, test_size=0.1)
print("Finished Train Test Split")

model = unet_model(input_size=(resolution, resolution, 3))
model.compile(optimizer='adam', loss=combined_loss)
print("Finished compiling the model")

early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
checkpoint = ModelCheckpoint('best_model.keras', monitor='val_loss', save_best_only=True, verbose=1)

model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=10, batch_size=2,  # Adjusted batch size to manage memory
          callbacks=[TQDMProgressBar(), early_stopping, checkpoint])

model.save('model.keras')
