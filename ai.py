import os
import json
from PIL import Image
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras import Model, Input
from tensorflow.keras.layers import Dense, Reshape, Conv2DTranspose, Conv2D
import tensorflow as tf


def crop_center(image, crop_width=32, crop_height=32):
    width, height = image.size
    left = (width - crop_width) / 2
    top = (height - crop_height) / 2
    right = (width + crop_width) / 2
    bottom = (height + crop_height) / 2
    return image.crop((left, top, right, bottom))


def prepare_data():
    recipe_vectors = []
    glaze_images = []

    for folder in os.listdir("recipe_images"):
        with open(f"recipe_images/{folder}/recipe.json", "r") as f:
            recipe = json.load(f)

        for image_file in os.listdir(f"recipe_images/{folder}"):
            if image_file.endswith(".jpg"):
                image = Image.open(f"recipe_images/{folder}/{image_file}").convert(
                    "RGB"
                )
                cropped_image = crop_center(image)
                recipe_vectors.append(recipe)
                glaze_images.append(np.array(cropped_image))

    # Convert to NumPy arrays
    recipe_vectors = np.array(recipe_vectors)
    glaze_images = np.array(glaze_images)

    # Save to disk
    np.save("pickled_vectors.npy", recipe_vectors)
    np.save("pickled_images.npy", glaze_images)


# prepare_data()


def create_datasets():
    vectors, images = np.load("pickled_vectors.npy"), np.load("pickled_images.npy")

    # Normalize images
    images = images / 255.0

    # Data split
    training_vectors, test_vectors, training_images, test_images = train_test_split(
        vectors, images, test_size=0.2, random_state=420
    )

    (
        training_vectors,
        validation_vectors,
        training_images,
        validation_images,
    ) = train_test_split(
        training_vectors, training_images, test_size=0.2, random_state=420
    )

    return (
        training_vectors,
        validation_vectors,
        test_vectors,
        training_images,
        validation_images,
        test_images,
    )


def create_nn():
    input_layer = Input(shape=(291,))
    x = Dense(128, activation="relu")(input_layer)
    x = Reshape((4, 4, 8))(x)  # This produces a tensor of shape (None, 4, 4, 8)
    x = Conv2DTranspose(64, (3, 3), strides=(2, 2), activation="relu", padding="same")(x)  # Output shape: (None, 8, 8, 64)
    x = Conv2DTranspose(32, (3, 3), strides=(2, 2), activation="relu", padding="same")(x)  # Output shape: (None, 16, 16, 32)
    x = Conv2DTranspose(32, (3, 3), strides=(2, 2), activation="relu", padding="same")(x)  # Output shape: (None, 32, 32, 32)
    x = Conv2D(3, (3, 3), activation="sigmoid", padding="same")(x)  # Output shape: (None, 32, 32, 3)

    model = Model(inputs=input_layer, outputs=x)

    # Compile the model
    model.compile(optimizer="adam", loss="mse")

    # Summary to show the architecture
    model.summary()

    return model


def train_and_save_model(
    model, training_vectors, validation_vectors, training_images, validation_images
):
    # Train the model
    history = model.fit(
        training_vectors,
        training_images,
        validation_data=(validation_vectors, validation_images),
        epochs=30,  # You can change the number of epochs
        batch_size=1,  # You can change the batch size
    )

    # Save the trained model
    model.save("trained_model.keras")

    return history

print(tf.sysconfig.get_build_info() )
# Prepare your data and neural network
(
    training_vectors,
    validation_vectors,
    test_vectors,
    training_images,
    validation_images,
    test_images,
) = create_datasets()
model = create_nn()

# Train and save the model
train_and_save_model(
    model, training_vectors, validation_vectors, training_images, validation_images
)
