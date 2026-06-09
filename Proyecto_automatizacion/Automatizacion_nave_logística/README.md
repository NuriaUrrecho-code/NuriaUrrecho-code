# WAREFLOW

Proyecto de automatización de una nave logística de productos de alimentación orientada al abastecimiento de supermercados.

Este trabajo fue reconocido con el **Primer Premio de la Feria de Proyectos 2026 de la ETSINF UPV**, entregado por expertos en Robótica.

Además de la simulación logística, el proyecto incorpora una **aplicación de visión 3D** para simular el control de calidad de los pallets. Esta parte se implementó sobre una **cinta 100% impresa en 3D** y **dos webcams**, reproduciendo un escenario de inspección cercano a una instalación real.

## De qué va el proyecto

La instalación modela una nave de distribución que abastece supermercados mediante la expedición de pallets completos correspondientes a pedidos de tienda.

Cada pedido está compuesto por **12 líneas de producto** y la nave gestiona todo el flujo logístico asociado:

- recepción y descarga de pallets de reposición,
- almacenamiento y actualización de inventario,
- preparación de pedidos,
- paletizado y despaletizado,
- gestión de AGVs,
- logística de camiones,
- expedición final de pallets completos.

El sistema se divide en dos grandes subsistemas:

- **Productos secos**: zona a temperatura ambiente, con transporte interno apoyado en ASRS, cintas y lógica de consolidación.
- **Productos frescos**: zona refrigerada, donde el transporte entre almacenamiento y paletizado se realiza mediante AGVs a través de una red con puntos críticos de cruce y control de ocupación.

La idea de fondo es sencilla: extraer solo lo que pide la demanda, agruparlo de forma ordenada y mantener el inventario en niveles suficientes sin disparar movimientos innecesarios de recarga. La dificultad está en coordinar ese flujo en dos entornos distintos, con restricciones térmicas, físicas y operativas diferentes.

## Qué resuelve

- Automatización del abastecimiento de supermercados.
- Simulación del comportamiento de una nave logística completa.
- Coordinación entre almacenamiento, manipulación y expedición.
- Gestión diferenciada de productos secos y frescos.
- Control del movimiento de AGVs y de la circulación de camiones.
- Validación de una solución industrial con una parte física de visión 3D.

## Características principales

- Generación automática de órdenes de compra/preparación.
- Selección ponderada de referencias para simular demanda.
- Gestión de inventario y reposición.
- Modelado de paletizado y despaletizado.
- Coordinación de recursos de transporte y manipulación.
- Bloque específico para control de productos y lógica de planta.

## Parte de visión 3D

La demostración incluye una aplicación de visión 3D para control de calidad de pallets:

- cinta transportadora impresa en 3D,
- dos webcams para la captura estéreo,
- simulación del proceso de inspección antes de la expedición.

Esta parte complementa la simulación de la nave y refuerza la validación práctica del proyecto.

## Estructura del repositorio

- `lista_ordenes.py`: generador de órdenes para productos de seco.
- `lista_ordenes_fresco.py`: generador de órdenes para productos frescos.
- `nave.fsm`: modelo de simulación de la nave.
- `vision_calidad.jpeg`: imagen relacionada con la aplicación de visión de calidad.
- `memoria_tecnica.pdf`: memoria técnica completa del proyecto.

## Generación de órdenes

Los scripts de órdenes generan pedidos con estas reglas:

- 12 líneas por orden.
- productos sin repetición dentro de la orden.
- ponderación en la elección de referencias para modelar distinta frecuencia de aparición.

En el caso de seco y fresco se usan listas de productos distintas para reflejar las diferencias entre ambas zonas de la nave.

## Tecnología utilizada

- Python
- Simulación de procesos logísticos
- FlexSim para la modelización de la nave
- Visión 3D con dos webcams
- Cinta física impresa en 3D para la demo de control de calidad