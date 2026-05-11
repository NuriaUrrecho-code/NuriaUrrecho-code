import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import cv2
from tkinter import filedialog
import os
import random as rng

window_original = 'Original_image'
window_threshold = 'Thresholded_image'
window_labels= 'Lables image'
window_roi = 'ROI'
window_roi_color = 'ROI Color'
window_inverted = 'Inverted (255 - thresh1)'
window_segmented = 'Segmented Card'
window_motifs = 'Motifs in Card'
#cv2.namedWindow(window_inverted, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
cv2.namedWindow(window_original,cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
#cv2.namedWindow(window_threshold,cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
cv2.namedWindow(window_roi,cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
cv2.namedWindow(window_roi_color,cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
cv2.namedWindow(window_segmented, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
cv2.namedWindow(window_motifs, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)


low_H = 155

#CAMBIO EJ5: Definición de la clase Card
class Card:
    # Suits. Palos de las cartas de póker
    DIAMONDS = 'Diamonds' # Rombos
    SPADES = 'Spades' # Picas
    HEARDS = 'Hearts' # Corazones
    CLUBS ='Clubs' # Tréboles
    # Figuras y cifras de las cartas de póker
    FIGURES = ('0','A','2','3','4','5','6','7','8','9','J','Q','K') # Se accede mediantge Carta.FIGURES[i]

    def __init__(self): # Constructor
        self.cardId = 0
        self.realSuit = ''
        self.realFigure = ''
        self.predictedSuit = ''
        self.predictedFigure = ''
        bboxType = [('x', np.intc),('y',np.intc),('width',np.intc),('height',np.intc)]
        self.boundingBox = np.zeros(1, dtype=bboxType).view(np.recarray)
        self.angle = 0.0
        self.grayImage = np.empty([0,0], dtype=np.uint8)
        self.colorImage = np.empty([0,0,0], dtype=np.uint8)
        self.motifs = []  # Lista de motivos (bounding boxes) encontrados en la carta
        self.motifsImage = np.empty((0,0,0), dtype=np.uint8)  # Imagen con contornos dibujados
        self.cardMask = np.empty((0,0), dtype=np.uint8)  # Máscara binaria de la carta


    def __repr__(self): # Para imprimir el contenido
        rep = f"Card number: {str(self.cardId)} -- Real Suit/Figure: {self.realSuit} / {self.realFigure} -- Predicted Suit/Figure: {self.predictedSuit} / {self.predictedFigure}"
        bb = f"Bounding Box: {str(self.boundingBox)} Rect angle: {str(self.angle)}"
        ims = f"Gray image: {str(self.grayImage.shape)} Color image: {str(self.colorImage.shape)}"
        new_line = "\n"
        return rep + new_line + bb + new_line + ims


class Motif:
    
    MOTIF_LABELS = ('Diamonds','Spades','Hearts','Clubs','0','2','3','4','5','6','7','8','9','A','J','Q','K','Others')
    
    def _init_(self):  # Constructor
        self.motifId = 0
        self.motifLabel = 'i'
        self.motifPredictedLabel = 'iii'
        self.area = 0.0
        self.contour = []
        self.perimeter = 0.0
        self.features = []
        self.moments = []
        self.huMoments = []
        self.centroid = []
        self.circleCenter = []
        self.circleRadious = 0.0
        self.fitEllipse = None
        
    def _repr_(self):
        rep = f"Motif number: {str(self.motifId)} --  Motif Label:  {self.motifLabel} -- Predicted Motif Label: {self.motifPredictedLabel}"
        bb = f"Area: {str(self.area)}   Perimeter: {str(self.perimeter)}"
        ims = f"Contour: {self.contour}  Features:  {str(self.features)}"
        _new_line = "\n"
        return rep + _new_line + bb + _new_line + ims


# CONVERSIÓN DE ETIQUETAS A COLORES
def label2rgb(label_img):
    label_hue = np.uint8(179*(label_img)/np.max(label_img))
    blank_ch = 255*np.ones_like(label_hue)
    labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])
    # Converting cvt to BGR
    labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)
    # set bg label to black
    labeled_img[label_img==0] = 0
    return labeled_img

def segmentar_objetos_carta(card: Card):
    if card.grayImage.size == 0:
        card.motifs = []
        card.motifsImage = np.empty((0,0,0), dtype=np.uint8)
        return card.motifs

    # Umbralización para resaltar los símbolos negros sobre el fondo blanco
    _, thresh = cv2.threshold(card.grayImage, low_H, 255, cv2.THRESH_BINARY_INV)

    # Componentes conectadas en la carta
    (totalLabels, label_ids_local, values, centroids) = cv2.connectedComponentsWithStats(
        thresh, 4, cv2.CV_32S
    )

    # Lienzo blanco para mostrar solo la carta y los motivos
    display_img = np.full_like(card.colorImage, 255)

    motifs = []
    min_area = 150  # Filtrado de ruido

    for i in range(1, totalLabels):
        area = values[i, cv2.CC_STAT_AREA]
        if area < min_area:
            continue

        x = int(values[i, cv2.CC_STAT_LEFT])
        y = int(values[i, cv2.CC_STAT_TOP])
        w = int(values[i, cv2.CC_STAT_WIDTH])
        h = int(values[i, cv2.CC_STAT_HEIGHT])

        bbox = {
            'x': x,
            'y': y,
            'width': w,
            'height': h,
            'area': int(area),
        }
        motifs.append(bbox)

        # Contorno del componente y su bounding box sobre fondo blanco
        componentMask = (label_ids_local == i).astype("uint8") * 255
        color = (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))
        display_img[componentMask > 0] = color
        contours, _ = cv2.findContours(componentMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(display_img, contours, -1, (0, 0, 255), 2)
        cv2.rectangle(display_img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # CAMBIO EJ8: características del motivo
        contours = contours[0]                                   
        moments = cv2.moments(contours)                              
        huMoments = cv2.HuMoments(moments).flatten()                 
        contour_area = cv2.contourArea(contours)                      
        perimeter = cv2.arcLength(contours, True)                 
        cx = int(moments['m10'] / moments['m00'])                
        cy = int(moments['m01'] / moments['m00'])                
        
        # Color medio del motivo dentro del roi_color
        mask_local = componentMask[y:y+h, x:x+w]
        roi_local = card.colorImage[y:y+h, x:x+w]
        mean_color = cv2.mean(roi_local, mask_local)[:3]   

        features = np.array([contour_area, perimeter, cx, cy, *huMoments, *mean_color], dtype=float)
        bbox["features"] = features


    card.motifs = motifs

    # Recortar al tamaño de la carta usando la máscara
    if card.cardMask.size > 0 and np.any(card.cardMask):
        ys, xs = np.nonzero(card.cardMask)
        y_min, y_max = ys.min(), ys.max()
        x_min, x_max = xs.min(), xs.max()
        card.motifsImage = display_img[y_min:y_max+1, x_min:x_max+1]
    else:
        card.motifsImage = display_img
    return card.motifs

# SELECCIÓN DE CARPETA
folders = '../images'
path = filedialog.askdirectory(initialdir=folders, title="Seleccione una carpeta")

# Hacemos una lista vacía de cartas 'Cards' para ir añadiendo items mediante Cards.append(Card)
Cards = []
icard = 0

for root,  dirs, files in os.walk(path, topdown=False):
    for name in files:
        if not(name.endswith('.jpg')):
            continue
        filename = os.path.join(root, name)
        img = cv2.imread(filename)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imshow(window_original,img)

        cartas_img = 0
        
        # CAMBIO EJ2: THRESH_BINARY en lugar de THRESH_BINARY_INV
        fret,thresh1 = cv2.threshold(img_gray,low_H,255,cv2.THRESH_BINARY_INV)
        # CAMBIO EJ2: Obtener las componentes conectadas de 255-thresh1
        (totalLabels, label_ids, values, centroid) = cv2.connectedComponentsWithStats(255-thresh1, 4, cv2.CV_32S)
        
        output = np.zeros(img_gray.shape, dtype="uint8")
        # Bucle para cada objeto 'i'
        for i in range(1, totalLabels):
            area = values[i, cv2.CC_STAT_AREA]
   
            if (area > 300000):  # Filtro de tamaño   NUEVA CARTA
                cartas_img +=1
                # CAMBIO EJ3: Inicalizar output
                output = np.zeros(img_gray.shape, dtype="uint8")
                componentMask = (label_ids == i).astype("uint8") * 255
                output = cv2.bitwise_or(output, componentMask)
                print(f"Área: {area}")
                
                # A completar: Contornos del objeto 'i' con área mayor que el mínimo indicado
                # CAMBIO EJ3:
                contours, jerarquia = cv2.findContours(output, cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE)
                
                # CBounding box del objeto 'i'
                x1 = values[i, cv2.CC_STAT_LEFT]
                y1 = values[i, cv2.CC_STAT_TOP]
                w = values[i, cv2.CC_STAT_WIDTH]
                h = values[i, cv2.CC_STAT_HEIGHT]
                
                roi = img_gray[int(y1):int(y1+h), int(x1):int(x1+w)].copy()
                rows, cols = roi.shape[:2]

                # CAMBIO EJ4: Obtener el mismo fragmento pero de la imagen original en color
                roi_color = img[int(y1):int(y1+h), int(x1):int(x1+w)].copy()
                rows, cols = roi_color.shape[:2]

                # CAMBIO EJ6: Aplicar rotación al roi               
                if len(contours) > 0:
                    # Obtener rectángulo mínimo del contorno
                    minRect = cv2.minAreaRect(contours[0])
                    (center, size, angle) = minRect
                    
                    # Ajustar el ángulo para que esté entre -45 y 45 grados
                    if angle < -45:
                        angle += 90
                    elif angle > 45:
                        angle -= 90
                    
                    print(f"Ángulo ajustado {angle:.2f} grados")    

                    # Usar el centro del rectángulo mínimo como centro de rotación
                    center = (cols / 2, rows / 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1)

                    # Nuevo tamaño tras rotación
                    sin = np.abs(rotation_matrix[0, 1])
                    cos = np.abs(rotation_matrix[0, 0])

                    cols_1 = int((rows * sin) + (cols * cos))
                    rows_1 = int((rows * cos) + (cols * sin))

                    # Ajustar la matriz de rotación para tener en cuenta el desplazamiento
                    rotation_matrix[0, 2] += (cols_1 / 2) - center[0]
                    rotation_matrix[1, 2] += (rows_1 / 2) - center[1]

                    # Aplicar la rotación
                    roi_rotated = cv2.warpAffine(roi, rotation_matrix, (cols_1, rows_1),flags=cv2.INTER_CUBIC)
                    roi_rotated_color = cv2.warpAffine(roi_color, rotation_matrix, (cols_1, rows_1),flags=cv2.INTER_CUBIC)
                    mask_rotated = cv2.warpAffine(componentMask[int(y1):int(y1+h), int(x1):int(x1+w)], rotation_matrix, (cols_1, rows_1),flags=cv2.INTER_CUBIC)
                        
                    # Poner la carta en vertical
                    if rows < cols:
                        roi_rotated = cv2.rotate(roi_rotated, cv2.ROTATE_90_CLOCKWISE)
                        roi_rotated_color = cv2.rotate(roi_rotated_color, cv2.ROTATE_90_CLOCKWISE)
                        mask_rotated = cv2.rotate(mask_rotated, cv2.ROTATE_90_CLOCKWISE)


                # CAMBIO EJ7: Imagen segmentada
                seg_card = np.full_like(roi_rotated_color, 255)
                seg_card[mask_rotated > 0] = (0, 215, 255)  # Amarillo suave
                cv2.rectangle(seg_card, (0, 0), (cols_1-1, rows_1-1), (0, 0, 255), 2)   

                # Dibujar el bounding box en la imagen original para visualización
                cv2.rectangle(img, (x1, y1), (x1+w, y1+h), (0, 255, 0), 3)
                cv2.putText(img, f'Carta {icard}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # Dibujar el rectángulo mínimo rotado
                if len(contours) > 0:
                    box_points = cv2.boxPoints(minRect)
                    box_points = np.int32(box_points)
                    cv2.drawContours(img, [box_points], 0, (255, 0, 0), 2)

                # CAMBIO EJ5: Crear y apuntar los datos de la carta (estructura básica por ahora)
                card = Card()
                card.cardId = icard
                card.boundingBox.x = x1
                card.boundingBox.y = y1
                card.boundingBox.width = w
                card.boundingBox.height = h
                card.grayImage = roi_rotated
                card.colorImage = roi_rotated_color
                card.angle = angle
                card.cardMask = mask_rotated

                # Añadir la carta a la lista de cartas
                Cards.append(card)
                icard += 1

        print(f'Cartas detectadas en esta imagen: {cartas_img}')
        print(f'Total acumulado de cartas: {icard}\n')

        segmentar_objetos_carta(card)
        
        key = -1
        while (key == -1):
            key = cv2.pollKey()
            cv2.imshow(window_original, img)
            #cv2.imshow(window_roi, roi_color)
            #cv2.imshow(window_threshold, output)
            cv2.imshow(window_segmented, seg_card) 
            cv2.imshow(window_motifs, card.motifsImage)
            
        if key == ord('q') or key == 27:    # 'q' o ESC para acabar
            break

# Guardar las cartas en un archivo 'cartas.npz'
if Cards:
    np.savez('cartas.npz', Cartas=Cards)
    print(f"Se guardaron {len(Cards)} cartas en 'cartas.npz'")
    file_size = os.path.getsize('cartas.npz')
    print(f"Tamaño del archivo 'cartas.npz': {file_size} bytes ({file_size/1024:.2f} KB)")
else:
    print("No se encontraron cartas para guardar")

cv2.destroyAllWindows()