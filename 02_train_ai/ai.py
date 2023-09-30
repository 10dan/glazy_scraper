import os
import json
import tensorflow as tf
import numpy as np
from PIL import Image
from tensorflow.keras.layers import LeakyReLU
from sklearn.model_selection import train_test_split
from tensorflow.keras import Model, Input
from tensorflow.keras.layers import (
    Dense,
    Reshape,
    Conv2DTranspose,
    Conv2D,
    BatchNormalization,
)


def prepare_data():
    recipe_vectors = []
    glaze_images = []

    for folder in os.listdir("recipe_images_lazy"):
        with open(f"recipe_images_lazy/{folder}/recipe.json", "r") as f:
            recipe = json.load(f)
            if len(recipe) != 196:
                continue

        for image_file in os.listdir(f"recipe_images_lazy/{folder}"):
            if image_file.endswith(".jpg"):
                print(f"Processing: {image_file}")
                image = Image.open(f"recipe_images_lazy/{folder}/{image_file}").convert(
                    "RGB"
                )
                recipe_vectors.append(recipe)
                glaze_images.append(np.array(image))

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
        training_vectors, training_images, test_size=0.2, random_state=6969
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
    input_layer = Input(shape=(196,))  # Assuming your vector size is 196
    x = Dense(4096)(input_layer)  # 4096 = 4*4*256
    x = LeakyReLU()(x)
    x = BatchNormalization()(x)
    x = Reshape((4, 4, 256))(x)  # Adjusted channels to 256

    x = Conv2DTranspose(128, (3, 3), strides=(2, 2), padding="same")(x)  # 8x8x128
    x = LeakyReLU()(x)
    x = BatchNormalization()(x)

    x = Conv2DTranspose(64, (3, 3), strides=(2, 2), padding="same")(x)  # 16x16x64
    x = LeakyReLU()(x)
    x = BatchNormalization()(x)

    x = Conv2DTranspose(32, (3, 3), strides=(2, 2), padding="same")(x)  # 32x32x32
    x = LeakyReLU()(x)
    x = BatchNormalization()(x)

    x = Conv2DTranspose(16, (3, 3), strides=(2, 2), padding="same")(x)  # 64x64x16
    x = LeakyReLU()(x)
    x = BatchNormalization()(x)

    x = Conv2DTranspose(8, (3, 3), strides=(2, 2), padding="same")(x)  # 128x128x8
    x = LeakyReLU()(x)
    x = BatchNormalization()(x)

    x = Conv2DTranspose(4, (3, 3), strides=(2, 2), padding="same")(x)  # 256x256x4
    x = LeakyReLU()(x)
    x = BatchNormalization()(x)

    x = Conv2D(3, (3, 3), activation="sigmoid", padding="same")(x)  # 256x256x3

    model = Model(inputs=input_layer, outputs=x)
    model.compile(optimizer="adam", loss="mse")
    model.summary()

    return model


# test
def train_and_save_model(
    model, training_vectors, validation_vectors, training_images, validation_images
):
    # Train the model
    history = model.fit(
        training_vectors,
        training_images,
        validation_data=(validation_vectors, validation_images),
        epochs=10,  # You can change the number of epochs
        batch_size=32,  # You can change the batch size
    )

    # Save the trained model
    model.save("trained_model.keras")

    return history


if __name__ == "__main__":
    (
    training_vectors,
    validation_vectors,
    test_vectors,
    training_images,
    validation_images,
    test_images,
    ) = create_datasets()
    model = create_nn()
    train_and_save_model(
        model, training_vectors, validation_vectors, training_images, validation_images
    )
    print("Done!")
