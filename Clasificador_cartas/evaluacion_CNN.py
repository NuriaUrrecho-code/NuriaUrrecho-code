import os
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay, matthews_corrcoef
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model

target_size = (120, 120)
dataset_path = "./Motifs_train/"
min_num_samples = 5 

dirs = os.listdir(dataset_path)
num_samples = [len(files) for r, d, files in os.walk(dataset_path)]
num_samples = num_samples[1:] 

# Labels filtrados según el número mínimo de muestras
labels = [j for (i, j) in zip(num_samples, dirs) if i >= min_num_samples]
print("Classes the model was trained on:", labels)

# Generador de datos para el test
datagen_test = ImageDataGenerator(rescale=1./255)

print("test_ds:")
test_ds = datagen_test.flow_from_directory(
    "./Motifs_test/",
    classes=labels,
    target_size=target_size,
    class_mode='categorical',
    batch_size=32, 
    shuffle=False
)

# Cargar red ya entrenada
model = load_model("./myCNN.h5")
model.summary()

# Evaluamos con las muestras de test
results = model.evaluate(test_ds)
print("test loss, test acc:", results)

# Generar predicciones
print("\nGenerate predictions")
predictions = model.predict(test_ds, verbose=1)
print("Predictions shape:", predictions.shape)

# Obtenemos el report
pred = np.argmax(predictions, axis=1)
class_ = test_ds.classes
print(classification_report(class_, pred, target_names=labels))
print("\nConfusion Matrix:")
cm = confusion_matrix(class_, pred)
print(cm)
mcc = matthews_corrcoef(class_, pred)
print(f"\nMCC: {mcc:.4f}")

# Confusion matrix gráficamente
cm_display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
cm_display.plot()
plt.xticks(rotation=90)
plt.show()