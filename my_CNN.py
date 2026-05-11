import os
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPool2D
from tensorflow.keras.optimizers import SGD
from sklearn.utils.class_weight import compute_class_weight # pesos de clase y desbalanceo


# Hyperparameters
target_size = (120, 120)
batch_size = 32
epochs = 50

# Importando el set de datos
dataset_train = "./Motifs_train/"
dataset_test = "./Motifs_test/"
min_num_samples = 5

print("all samples:")
dirs = os.listdir(dataset_train)
num_samples = [len(files) for r, d, files in os.walk(dataset_train)]
num_samples = num_samples[1:] # exclude first top directory
print(dirs)
print(num_samples)
labels = [j for (i, j) in zip(num_samples, dirs) if i >= min_num_samples]

ok_samples = [ [j,i] for (i,j) in zip(num_samples,dirs) if i >= min_num_samples ]
print("samples with more than " + str(min_num_samples) + " samples" , ok_samples)

labels = [j for (i, j) in zip(num_samples, dirs) if i >= min_num_samples]
print(labels)

# Data generators para poder hacer data augmentation
datagen_train_val = ImageDataGenerator(
    rotation_range=10,
    width_shift_range=0.05,
    height_shift_range=0.05,
    zoom_range=0.1,
    horizontal_flip=True,
    vertical_flip=False,
    validation_split=0.2,
    #preprocessing_function=preprocess_input,
    rescale=1./255
)

print("train_ds:")
train_ds = datagen_train_val.flow_from_directory(
    dataset_train,
    classes=labels,
    target_size=target_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='training'
)

print("val_ds:")
val_ds = datagen_train_val.flow_from_directory(
    dataset_train,
    classes=labels,
    target_size=target_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation'
)

datagen_test = ImageDataGenerator(rescale=1./255)

print("test_ds:")
test_ds = datagen_test.flow_from_directory(
    dataset_test,
    classes=labels,
    target_size=target_size,
    class_mode='categorical',
    shuffle=False
)

# Class weights (para dataset desbalanceado)
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_ds.classes),
    y=train_ds.classes
)
class_weights = dict(enumerate(class_weights))
print("Class weights:", class_weights)

# Red base preentrenada (Transfer Learning)
base_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(120, 120, 3)
)
# Se congelan los pesos convolucionales
base_model.trainable = False


model = Sequential()
model.add(base_model)

model.add(Conv2D(64, (3,3), padding="same", activation="relu", name="Conv2D1"))
model.add(Conv2D(64, (3,3), padding="same", activation="relu"))
model.add(MaxPool2D(pool_size=(2,2), strides=(2,2), name="MaxPool2D1"))

model.add(Conv2D(64, (3,3), padding="same", activation="relu", name="Conv2D2"))
model.add(MaxPool2D(pool_size=(2,2), strides=(2,2), name="MaxPool2D2"))

model.add(Flatten(name="Flatten"))
model.add(Dense(200, activation="relu", name="Dense1"))
model.add(Dropout(0.4))
model.add(Dense(train_ds.num_classes, activation="softmax", name="FinalStage"))

# Compilamos el modelo
model.compile(loss='categorical_crossentropy', optimizer=SGD(0.005), metrics=['accuracy'])
model.summary()

# Entrenamos el modelo
print("[INFO]: Entrenando la red...")
H = model.fit(train_ds, epochs=epochs, validation_data=val_ds, class_weight=class_weights, verbose=1)

# Gráfica
plt.style.use("ggplot")
plt.figure()
plt.plot(np.arange(0, epochs), H.history["loss"], label="train_loss")
plt.plot(np.arange(0, epochs), H.history["val_loss"], label="val_loss")
plt.plot(np.arange(0, epochs), H.history["accuracy"], label="train_acc")
plt.plot(np.arange(0, epochs), H.history["val_accuracy"], label="val_acc")
plt.title("Training Loss and Accuracy")
plt.xlabel("Epoch #")
plt.ylabel("Loss/Accuracy")
plt.legend()
plt.show()

# Almacenamos el modelo empleando la funcion model.save de Keras
model.save("./myCNN.h5")