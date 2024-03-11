import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
import pathlib


def train(e, b, h,directory):
    # Load Data
    data_dir = pathlib.Path(directory).with_suffix('')
    image_count = len(list(data_dir.glob('*/*.jpg')))

    # Print image count
    print(image_count)

    # Define standard image dimensions
    batch_size = b
    img_height = h
    img_width = h
    epochs = e
    colVals = 1
    # training dataset
    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size)

    # validation dataset
    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size)

    # display class data
    class_names = train_ds.class_names
    print(class_names)
    num_classes = len(class_names)

    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    # recolor
    normalization_layer = layers.Rescaling(1. / 255)
    normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
    image_batch, labels_batch = next(iter(normalized_ds))
    first_image = image_batch[0]
    # Notice the pixel values are now in `[0,1]`.
    print(np.min(first_image), np.max(first_image))

    data_augmentation = keras.Sequential(
        [
            layers.RandomFlip("horizontal",
                              input_shape=(img_height,
                                           img_width,
                                           3)),
            layers.RandomRotation(1),
            layers.RandomZoom(0.1),
        ]
    )
    # Create Model
    model = Sequential([
        data_augmentation,
        layers.Rescaling(1. / 255),
        layers.Conv2D(16, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Dropout(0.2),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(num_classes, name="outputs")
    ])
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs
    )
    score = history.history['val_accuracy'][-1]
    if score > 0.84:
        model.save("" + str(batch_size) + "_" + str(img_height) + "_" + "_" + str(epochs) + "_" + str(score) + ".h5")
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']

    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs_range = range(epochs)

    plt.figure(figsize=(16, 8))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')
    plt.show()


def guess(premadeModel,path):
    imageName = path.split("/")[-1]
    # Load model
    model = keras.models.load_model(premadeModel)
    # Load image
    info = model.get_config()["layers"][0]["config"]["batch_input_shape"] # Returns pretty much every information about your model)
    length = info[1]
    width = info[2]
    img = keras.preprocessing.image.load_img(
        path, target_size=(length, width)
    )
    img_array = keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch
    class_names = ['black',"blue","green"]

    predictions = model.predict(img_array)

    score = tf.nn.softmax(predictions[0])
    choice = class_names[np.argmax(score)]
    confidence = 100 * np.max(score)

    print(choice)
    print(        imageName+" most likely belongs in the {} bin with {:.2f} percent confidence.".format(choice,confidence))
    if choice == "glass" or choice == "metal" or choice == "plastic":
        print(
            imageName+" most likely belongs in the blue bin with {:.2f} percent confidence.".format(confidence))
        choice = "blue"
    elif choice == "cardboard" or choice == "paper":
        print(
            imageName+" most likely belongs in the black bin with {:.2f} percent confidence.".format(confidence))
        choice = "black"
    elif choice == "biological" or choice == "trash":
        print(
            imageName+" most likely belongs in the green bin with {:.2f} percent confidence.".format(confidence))
        choice = "green"
    print("")

    return choice


if __name__ == "__main__":
    guess("16_100__350_0.8941256999969482.h5","cereal.jpg")
    print("Hello World")