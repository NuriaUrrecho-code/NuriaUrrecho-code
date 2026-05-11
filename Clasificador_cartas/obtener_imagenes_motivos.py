import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import cv2
import os
from clases_cartas import Card, Motif


filecard = 'testCards.npz'  # y 'testCards.npz'
cards = []
motifs = []

BASE_DIR = './Motifs_test/' # y './Motifs_test/' 

# Diccionario de los nombres de carpetas
LABEL_MAP = {
    '0': '000', '2': '002', '3': '003', '4': '004', '5': '005', '6': '006', 
    '7': '007', '8': '008', '9': '009', 'A': '00A', 'J': '00J', 'K': '00K',
    'Q': '00Q', 'corazones': 'corazones', 'picas': 'picas', 'rombos': 'rombos',
    'treboles': 'treboles', 'variados': 'variados',  
}
 
# Crear la estructura de cartas
npzfile = np.load(filecard, allow_pickle=True)
cards = npzfile['Cartas']
le = len(cards)
j=1000

for i in range(0,le):
    print('carta[',i,']')
    mots = cards[i].motifs
    ll = len(mots)
    for m in mots:
        cnt = m.contour
        x,y,w,h = cv2.boundingRect(cnt)
        img = cards[i].colorImage
        
        # Recorte de la imagen del motivo (ROI)
        roi_color = img[int(y):int(y+h), int(x):int(x+w)].copy() 
        img_motif = cv2.cvtColor(roi_color, cv2.COLOR_BGR2RGB)
        
        # 1. Obtiene la etiqueta original
        original_label = str(m.motifLabel)

        # 2. Mapea la etiqueta original al nombre de carpeta requerido
        folder_name = LABEL_MAP.get(original_label, original_label)
        
        # 3. La etiqueta para el nombre del archivo debe ser el nombre de la carpeta 
        label_for_file = folder_name
        
        # Crea el directorio de salida si no existe
        output_dir = os.path.join(BASE_DIR, folder_name) 
        os.makedirs(output_dir, exist_ok=True) # Crea la subcarpeta si no existe
        
        # Imagen original (0 grados)
        name = output_dir + '/' + label_for_file + '_' + str(j) + '.png' 
        print(name,' ',w,h)
        image = Image.fromarray(img_motif)
        image.save(name)
        j = j+1

        # Motivo girado 90º
        img_rot90 = np.rot90(img_motif, k=1) 
        name_90 = output_dir + '/' + label_for_file + '_' + str(j) + '.png'
        print(name_90,' ',w,h)
        image_90 = Image.fromarray(img_rot90)
        image_90.save(name_90)
        j = j+1

        # Motivo girado 180º
        img_rot180 = np.rot90(img_motif, k=2) 
        name_180 = output_dir + '/' + label_for_file + '_' + str(j) + '.png'
        print(name_180,' ',w,h)
        image_180 = Image.fromarray(img_rot180)
        image_180.save(name_180)
        j = j+1
        
        # Motivo girado 270º
        img_rot270 = np.rot90(img_motif, k=3) 
        name_270 = output_dir + '/' + label_for_file + '_' + str(j) + '.png'
        print(name_270,' ',w,h)
        image_270 = Image.fromarray(img_rot270)
        image_270.save(name_270)
        j = j+1