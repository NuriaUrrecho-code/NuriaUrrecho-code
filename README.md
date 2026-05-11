# Visor y reconocedor de cartas

Proyecto de vision por computador para detectar cartas de poker en imagenes, segmentar sus motivos internos y clasificarlos para identificar el palo y la figura de cada carta.

El trabajo combina tecnicas clasicas de procesado de imagen con modelos de aprendizaje automatico. Primero se localizan las cartas dentro de fotografias, despues se extraen los motivos de cada carta, se etiquetan manualmente y finalmente se entrenan clasificadores para reconocerlos.

## Que hace el proyecto

- Detecta cartas en fotografias mediante umbralizacion, componentes conectadas y contornos.
- Recorta cada carta encontrada y guarda su informacion en objetos `Card`.
- Segmenta los motivos internos de la carta, como palos y numeros/letras.
- Extrae caracteristicas geometricas de cada motivo: area, perimetro, momentos de Hu, centroide, circularidad, relacion de aspecto, solidez, densidad, etc.
- Permite etiquetar manualmente los motivos con una interfaz de `tkinter`.
- Entrena y evalua un clasificador kNN sobre las caracteristicas extraidas.
- Genera imagenes de motivos para entrenar una CNN.
- Entrena una red convolucional basada en MobileNetV2 para clasificacion por imagen.

## Estructura principal

```text
.
|-- clases_cartas.py              # Clases Card y Motif
|-- segmentar_cartas.py           # Detecta cartas y motivos desde imagenes JPG
|-- etiquetar_cartas_OK.py        # Interfaz grafica para etiquetar motivos
|-- preprocesar_npz.py            # Normaliza las caracteristicas de train/test
|-- modelo_kNN.py                 # Entrena y evalua el clasificador kNN
|-- obtener_imagenes_motivos.py   # Exporta recortes de motivos como PNG
|-- my_CNN.py                     # Entrena una CNN con los motivos exportados
|-- PL6.py                        # Version de practica/desarrollo del pipeline
|-- trainCards.npz                # Cartas y motivos del conjunto de entrenamiento
|-- testCards.npz                 # Cartas y motivos del conjunto de test
|-- cartas.npz                    # Dataset intermedio
|-- myCNN.h5                      # Modelo CNN entrenado
|-- images/                       # Fotografias originales
|-- Motifs_train/                 # Motivos recortados para entrenamiento CNN
`-- Motifs_test/                  # Motivos recortados para test CNN
```

## Requisitos

El proyecto esta hecho en Python y usa principalmente:

- `opencv-python`
- `numpy`
- `matplotlib`
- `Pillow`
- `scikit-learn`
- `tensorflow`

Instalacion recomendada:

```bash
pip install opencv-python numpy matplotlib pillow scikit-learn tensorflow
```

`tkinter` se usa para las ventanas de seleccion de carpetas y etiquetado. En muchas instalaciones de Python ya viene incluido.

## Flujo de funcionamiento

### 1. Segmentar cartas desde imagenes

```bash
python segmentar_cartas.py
```

El programa abre un selector de carpetas. Al elegir una carpeta con imagenes `.jpg`, recorre las fotos, detecta las cartas y extrae los motivos internos.

Segun el nombre de la carpeta seleccionada, guarda el resultado en:

- `trainCards.npz`, si la carpeta contiene `train` en el nombre.
- `testCards.npz`, si la carpeta contiene `test` en el nombre.
- `cards.npz`, en cualquier otro caso.

Cada `.npz` contiene una lista de objetos `Card`, y cada carta contiene sus motivos `Motif` con las caracteristicas calculadas.

### 2. Etiquetar motivos

```bash
python etiquetar_cartas_OK.py
```

Este script abre una interfaz grafica para revisar los motivos detectados y asignarles una etiqueta. Las etiquetas posibles incluyen los palos:

- `Rombos`
- `Picas`
- `Corazones`
- `Treboles`

Y las figuras:

- `0`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `A`, `J`, `Q`, `K`

Tambien existe la clase `Others` para motivos que no corresponden a una figura o palo util.

Al salir, el programa vuelve a guardar el archivo `.npz` con las etiquetas actualizadas.

> Nota: en el script se indica el archivo a etiquetar mediante la variable `filecard`. Por defecto aparece como `testCards.npz`, pero se puede cambiar a `trainCards.npz`.

### 3. Preprocesar caracteristicas

```bash
python preprocesar_npz.py
```

Este paso normaliza las caracteristicas de los motivos usando el conjunto de entrenamiento como referencia. Aplica un recorte suave de outliers y escala las caracteristicas usando mediana e IQR.

El script sobrescribe:

- `trainCards.npz`
- `testCards.npz`

con las caracteristicas ya normalizadas.

### 4. Entrenar y evaluar kNN

```bash
python modelo_kNN.py
```

Este modelo usa las caracteristicas numericas extraidas de cada motivo. El script:

1. Carga `trainCards.npz`.
2. Usa los motivos etiquetados para entrenar un kNN de OpenCV.
3. Carga `testCards.npz`.
4. Predice la clase de cada motivo de test.
5. Muestra tasa de acierto, `classification_report`, matriz de confusion y MCC.

El clasificador se entrena con `k=1` en la fase de prediccion.

### 5. Exportar imagenes de motivos

```bash
python obtener_imagenes_motivos.py
```

Este script recorta cada motivo etiquetado y lo guarda como imagen `.png`. Tambien genera versiones rotadas a 90, 180 y 270 grados para aumentar el numero de muestras.

Las imagenes se organizan en carpetas por clase dentro de:

- `Motifs_train/`
- `Motifs_test/`

La variable `filecard` indica de que `.npz` se leen los datos y `BASE_DIR` indica donde se guardan los recortes.

### 6. Entrenar la CNN

```bash
python my_CNN.py
```

Este script entrena una red neuronal convolucional para clasificar los motivos directamente a partir de imagenes. Usa:

- `Motifs_train/` como conjunto de entrenamiento y validacion.
- `Motifs_test/` como conjunto de prueba.
- `ImageDataGenerator` para aumento de datos.
- `MobileNetV2` preentrenada como base.
- Capas convolucionales y densas adicionales para adaptar el modelo al problema.

Al finalizar guarda el modelo en:

```text
myCNN.h5
```

## Como se representa una carta

La clase `Card` guarda la informacion principal de cada carta:

- identificador de carta
- palo y figura reales
- palo y figura predichos
- bounding box
- angulo de rotacion
- imagen en gris
- imagen en color
- lista de motivos detectados

La clase `Motif` representa cada simbolo o componente encontrado dentro de la carta:

- etiqueta real
- etiqueta predicha
- area
- contorno
- perimetro
- momentos
- momentos de Hu
- centroide
- caracteristicas numericas usadas por el clasificador

## Resultado esperado

El objetivo final es que, a partir de imagenes de cartas, el sistema sea capaz de detectar cada carta, separar los simbolos relevantes y clasificar sus motivos para reconocer que carta es.

El proyecto permite comparar dos enfoques:

- kNN usando caracteristicas geometricas extraidas con OpenCV.
- CNN usando imagenes recortadas de los motivos.

## Notas

- Los scripts estan pensados para ejecutarse desde la raiz del proyecto.
- Algunas rutas y archivos de entrada se configuran directamente dentro de cada script mediante variables como `filecard` o `BASE_DIR`.
- El proyecto contiene datos ya generados (`.npz`, motivos exportados y modelo `.h5`), por lo que se puede estudiar el flujo sin repetir todo el proceso desde cero.
