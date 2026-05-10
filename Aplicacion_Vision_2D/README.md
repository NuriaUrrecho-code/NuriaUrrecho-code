# Proyecto 1 - Aplicacion

Aplicacion Python para deteccion, seguimiento y posicionamiento planar de mandarinas con una sola camara.

El proyecto incluye:
- calibracion intrinseca de camara con tablero de ajedrez;
- calibracion del plano de trabajo mediante homografia;
- correccion de altura automatica a partir de la pose estimada;
- deteccion automatica por color en el primer frame;
- seguimiento en tiempo real con tracker KCF;
- publicacion de posiciones por MQTT.

## Requisitos

- Python 3.10 o superior
- Una camara accesible desde OpenCV
- OpenCV con modulo de tracking disponible

Librerias necesarias:
- `opencv-python`
- `numpy`
- `paho-mqtt`

Si la instalacion de OpenCV no incluye trackers modernos, puede ser necesario usar:
- `opencv-contrib-python`

## Requisitos tecnicos para que la app se vea bien en la terminal

Para que el menu principal salga con el formato correcto y no en modo reducido, conviene cumplir estas condiciones:

- Ejecutar la app desde una terminal real, no desde una salida embebida sin TTY.
- Tener `stdin` y `stdout` conectados a un terminal interactivo.
- Usar una terminal con soporte para `curses` y colores ANSI.
- Usar codificacion UTF-8 para que se vea bien el titulo, las tildes y el dibujo ASCII/Unicode de la portada.
- Usar una fuente monoespaciada en la terminal.
- Tener una ventana de terminal suficientemente grande; recomendado al menos `100x30` columnas x filas.
- Ejecutar la app localmente con acceso a interfaz grafica, porque OpenCV abre ventanas para la camara, la mascara, la seleccion de puntos y la seleccion manual de ROI.

Entornos recomendados:

- macOS: `Terminal` o `iTerm2`
- Linux: `gnome-terminal`, `konsole`, `xterm` o similares
- Windows: `Windows Terminal` o PowerShell moderno, siempre que OpenCV pueda abrir ventanas

Entornos en los que el menu puede verse peor o entrar en modo alternativo:

- salidas de IDEs que no exponen un TTY real;
- notebooks;
- sesiones remotas sin reenvio grafico;
- terminales muy estrechas;
- shells o consolas sin soporte correcto para UTF-8.

Si no hay un TTY compatible, la app no usa el menu bonito con `curses` y cambia automaticamente a un menu numerico mas simple.

### Que instalar si no se ve bien o si falta alguna dependencia

Para ejecutar la app correctamente, normalmente hace falta tener instalado:

- `numpy`
- `opencv-contrib-python`
- `paho-mqtt`

Instalacion recomendada:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy opencv-contrib-python paho-mqtt
```

Si se ejecuta en Windows y el menu de terminal no funciona bien, puede hacer falta instalar tambien:

```bash
pip install windows-curses
```

En macOS y Linux normalmente no hace falta instalar nada extra para `curses`, pero si la terminal no soporta bien UTF-8, colores o TTY interactivo, el menu avanzado no se mostrara correctamente y la app usara el modo numerico simple.

## Instalacion

Desde la carpeta `Proyecto1/aplicacion`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy opencv-contrib-python paho-mqtt
```

Si ya tienes un entorno creado, basta con activarlo e instalar las dependencias que falten.

## Estructura

- `app.py`: menu principal de la aplicacion
- `main_position.py`: deteccion, seguimiento, posicionamiento y MQTT
- `app_state.py`: configuracion persistente y estado
- `calibration/capture_calibration_images.py`: captura imagenes del tablero
- `calibration/camera_calibration.py`: calcula `K.npy` y `dist.npy`
- `calibration/select_points.py`: seleccion manual de 4 puntos del plano
- `calibration/homography.py`: calcula `H.npy`
- `state/config.json`: configuracion guardada por la app

## Ejecucion

Lanzar la aplicacion principal:

```bash
python3 app.py
```

La aplicacion abre un menu desde el que se puede:
- elegir la camara;
- capturar imagenes de calibracion;
- calibrar la camara;
- seleccionar los 4 puntos del plano;
- calcular la homografia;
- ejecutar la deteccion y el posicionamiento.

## Flujo recomendado

1. Ejecutar `python3 app.py`
2. Entrar en `Buscar y elegir camara`
3. Entrar en `Capturar imagenes de calibracion`
4. Entrar en `Calibrar camara`
5. Entrar en `Seleccionar 4 puntos del plano`
6. Entrar en `Calcular homografia`
7. La app usa siempre deteccion automatica en el primer frame con tracker KCF
8. Entrar en `Ejecutar deteccion y posicionamiento`

## Modos de funcionamiento

La entrega final queda fijada a un unico modo de funcionamiento:

- correccion de altura automatica con altura estimada por pose;
- deteccion automatica por color en el primer frame;
- inicializacion automatica de cajas a partir de la deteccion;
- seguimiento posterior con tracker `KCF`.

No se usan variaciones de deteccion manual, seguimiento continuo ni seleccion interactiva de tracker en la version final.

## Configuracion

La configuracion persistente se guarda en:

```text
state/config.json
```

Valores relevantes:
- `camera_index`
- `hsv_lower`
- `hsv_upper`
- `camera_height_cm`
- `height_correction_mode`
- `object_radius_cm`
- `mqtt_broker`
- `mqtt_port`
- `mqtt_topic`
- `detection_mode`
- `tracking_mode`
- `opencv_tracker`

En la version final estos valores quedan fijados por codigo a:
- `height_correction_mode = pose_estimated_height`
- `detection_mode = automatic`
- `tracking_mode = first_frame`
- `opencv_tracker = kcf`

## MQTT

Si `paho-mqtt` esta instalado y el broker es accesible, la app publica posiciones en el topic configurado.

Formato del payload:

```json
{
  "id": "mandarina_1",
  "x": 12.34,
  "y": 5.67,
  "z": 2.5
}
```

## Tests

Se ha incluido un test minimo para funciones geometricas puras:

```bash
python3 -m unittest tests/test_geometry.py
```

## Notas

- Si no aparece ninguna camara, revisa el indice configurado.
- Si la deteccion automatica falla, ajusta el rango HSV en `state/config.json`.
- Si el seguimiento en primer frame no funciona, comprueba que tu instalacion de OpenCV tenga disponible `KCF`.
