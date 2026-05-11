import cv2
import os
import numpy as np
from clases_cartas import Card, Motif
import warnings
from sklearn import metrics


FIGURES = ('0','A','2','3','4','5','6','7','8','9','J','Q','K') # Se accede mediantge Carta.FIGURES[i]
SUITS = ('Rombos','Picas','Corazones','Treboles')
MOTIF_LABELS = ('Rombos','Picas','Corazones','Treboles','0','2','3','4','5','6','7','8','9','A','J','Q','K','Others')   

filecard = 'trainCards.npz'

npzfile = np.load(filecard, allow_pickle=True) 
cards = npzfile['Cartas']
llen = cards.size

# Listas vacias
samples = []     # Lista de características de cada muestra
responses = []   # Lista de etiqueta real de cada muestra


############## TRAINING ############################
j=0
for i in range(0,llen):   # para todas las cartas
    motifs = cards[i].motifs
    for mot in motifs:
        lbl = mot.motifLabel
        if lbl == 'i':
            continue       # si el motivo no está etiquetado se descarta
        idx = MOTIF_LABELS.index(lbl)    # etiqueta real del motivo
        responses.append(idx)
        j +=1
        print(j, idx, lbl)       
        # Añadir a samples todas las características del motivo que consideremos oportunas.
        # Ojo que debe ser una fila o vector de números reales
        feat = np.array(mot.features, dtype=np.float32).flatten()   # A completar
        samples.append(feat)


# Convertir las listas en arrays
sampl = np.asarray(samples).astype(np.float32)
resp = np.asarray(responses, dtype=np.int32)

# Creación del modelo kNN
knn = cv2.ml.KNearest_create()
# Entrenar el modelo kNN
knn.train(sampl, cv2.ml.ROW_SAMPLE, resp)


######## TEST ##########

filecardTest = 'testCards.npz'
npzfileT = np.load(filecardTest, allow_pickle=True) 
cardsTest = npzfileT['Cartas']
llenTest = cardsTest.size

samplesTest = []
responsesTest = []

j=0
for i in range(0,llenTest):   # para todas las cartas
    motifs = cardsTest[i].motifs
    for mot in motifs:
       
        lbl = mot.motifLabel
        if lbl == 'i':    # si el motivo no está etiquetado se le pone 'Others'
            lbl = 'Others'
        idx = MOTIF_LABELS.index(lbl)
        responsesTest.append(idx)
        j +=1
        print(j, idx, lbl)
        # Añadir a samplesTest todas las características del motivo que consideremos oportunas.
        # Ojo que debe ser una fila o vector de números reales
        feat = np.array(mot.features, dtype=np.float32).flatten()  # A completar
        samplesTest.append(feat)
     
                
# Convertir las listas en arrays
samplTest = np.asarray(samplesTest).astype(np.float32)
respTest = np.asarray(responsesTest)

# Predicción con k=1
ret, results, neighbours ,dist = knn.findNearest(samplTest, k=1)  # A completar por el alumno

# Visualización de resultados
le = len(results)
j=0
pred = np.zeros(le)
real = np.zeros(le)

for i in range(0,le):
    pred[i] = int(results[i][0])
    real[i] = respTest[i]
    pred_str = MOTIF_LABELS[int(results[i][0])]
    real_str = MOTIF_LABELS[respTest[i]]
    print(f"result: {pred_str}  real:  {real_str}" )
    if pred[i]==real[i]:
        j+=1

print(f'\nTasa aciertos:    {j/le}\n')


# VISUALIZACIÓN
from sklearn.metrics import confusion_matrix, classification_report, matthews_corrcoef

# Obtenemos el report
labels = sorted(list(set(int(x) for x in real) | set(int(x) for x in pred)))
CLS_REP=classification_report(real, pred, labels=labels, target_names=MOTIF_LABELS, zero_division=0)
print('Classification report:\n', CLS_REP) 
CONF_MAT = confusion_matrix(real,pred)
print('Confusion Matrix:\n', CONF_MAT)
MCC = matthews_corrcoef(real, pred)
print('\nMCC: ', MCC)

import matplotlib.pyplot as plt
cm_display = metrics.ConfusionMatrixDisplay(confusion_matrix=CONF_MAT, display_labels=MOTIF_LABELS)
cm_display.plot(xticks_rotation='vertical')
plt.show()