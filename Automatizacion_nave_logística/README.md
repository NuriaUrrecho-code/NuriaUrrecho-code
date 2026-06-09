# 🚛 WAREFLOW

### 🏆 Primer Premio Feria de Proyectos 2026 – ETSINF UPV

Proyecto de automatización de una nave logística de productos de alimentación orientada al abastecimiento de supermercados.

Este trabajo fue reconocido con el **🥇 Primer Premio de la Feria de Proyectos 2026 de la ETSINF UPV**, otorgado por un jurado de expertos en **Robótica y Automatización Industrial**.

Además de la simulación logística completa, el proyecto incorpora una **aplicación de visión 3D para control de calidad de pallets**, desarrollada sobre una **cinta transportadora 100% impresa en 3D** y utilizando **dos webcams** para reconstrucción estéreo e inspección visual.

---

# 📦 Descripción del proyecto

WAREFLOW reproduce el funcionamiento de una nave de distribución encargada de abastecer supermercados mediante la expedición de pallets completos correspondientes a pedidos de tienda.

Cada pedido está compuesto por **12 líneas de producto**, y la instalación gestiona de forma automática todo el flujo logístico:

✅ Recepción de mercancía
✅ Descarga de pallets de reposición
✅ Almacenamiento e inventario
✅ Preparación de pedidos
✅ Paletizado y despaletizado
✅ Coordinación de AGVs
✅ Gestión de camiones
✅ Expedición de pedidos completos

El objetivo es suministrar únicamente los productos demandados, consolidar pedidos de forma eficiente y mantener niveles adecuados de inventario minimizando movimientos innecesarios de reposición.

---

# 🏭 Arquitectura logística

La nave está dividida en dos subsistemas principales:

## 🌡️ Productos Frescos

Zona refrigerada destinada al almacenamiento y preparación de productos frescos.

Características:

* 🚗 Transporte mediante AGVs.
* 🔀 Red logística con cruces y puntos críticos.
* 🚦 Control de ocupación y prioridades.
* ❄️ Operación en entorno refrigerado.

---

## 📦 Productos Secos

Zona de temperatura ambiente destinada a productos no perecederos.

Características:

* 🏗️ Sistema ASRS de almacenamiento.
* 🎛️ Transporte mediante cintas.
* 📥 Despaletizado automático.
* 📤 Consolidación y expedición de pedidos.

---

# 🎯 Qué resuelve

WAREFLOW permite estudiar y validar:

* 🤖 Automatización del abastecimiento de supermercados.
* 📈 Comportamiento operativo de una nave logística completa.
* 🔄 Coordinación entre almacenamiento, transporte y expedición.
* 🌡️ Gestión diferenciada de productos secos y frescos.
* 🚗 Circulación y control de AGVs.
* 🚛 Operativa logística de camiones.
* 👁️ Validación física mediante visión 3D para control de calidad.

---

# ⚙️ Funcionalidades principales

* 📋 Generación automática de órdenes.
* 🎲 Simulación de demanda mediante selección ponderada de referencias.
* 📦 Gestión de inventario y reposición.
* 🏗️ Paletizado y despaletizado automático.
* 🚗 Coordinación de AGVs.
* 🚛 Gestión de llegadas y salidas de camiones.
* 🏭 Lógica de planta y control de procesos.
* 📊 Simulación integral de operaciones logísticas.

---

# 👁️ Sistema de visión 3D

Como complemento a la simulación, el proyecto incorpora una demostración física de control de calidad.

### Componentes

* 🖨️ Cinta transportadora impresa en 3D.
* 📷 Cámara estéreo formada por dos webcams.
* 📦 Simulación de inspección de pallets.
* ✅ Validación previa a la expedición.

Esta parte aporta una capa adicional de realismo y permite validar procesos de inspección industrial en un entorno físico.

---

# 📂 Estructura del repositorio

```text
WAREFLOW/
│
├── lista_ordenes.py
├── lista_ordenes_fresco.py
├── nave.fsm
├── vision_calidad.jpeg
└── memoria_tecnica.pdf
```

### Archivos principales

| Archivo                   | Descripción                                 |
| ------------------------- | ------------------------------------------- |
| `lista_ordenes.py`        | Generador de órdenes para productos secos   |
| `lista_ordenes_fresco.py` | Generador de órdenes para productos frescos |
| `nave.fsm`                | Modelo completo de simulación en FlexSim    |
| `vision_calidad.jpeg`     | Imagen de la aplicación de visión           |
| `memoria_tecnica.pdf`     | Memoria técnica del proyecto                |

---

# 📋 Generación de órdenes

Los generadores de pedidos siguen las siguientes reglas:

* 📌 12 líneas por orden.
* 🚫 Sin productos repetidos dentro del mismo pedido.
* ⚖️ Selección ponderada de referencias para simular demanda real.
* 📦 Catálogos independientes para seco y fresco.

Esto permite reproducir patrones de consumo más cercanos a un entorno logístico real.

---

# 🛠️ Tecnologías utilizadas

* 🐍 Python
* 🏭 FlexSim
* 📊 Simulación de procesos logísticos
* 👁️ Visión 3D estéreo
* 📷 Dos webcams para captura simultánea
* 🖨️ Fabricación aditiva (impresión 3D)
* 🚗 Sistemas AGV
* 📦 Automatización intralogística

---

# 📸 Proyecto premiado

🥇 **Primer Premio Feria de Proyectos ETSINF UPV 2026**

El proyecto fue reconocido por su combinación de:

* Simulación logística avanzada.
* Automatización industrial.
* Coordinación de AGVs.
* Modelado de almacenes automáticos.
* Aplicación práctica de visión artificial 3D.

---

> 🚀 WAREFLOW combina simulación industrial, automatización logística y visión artificial para reproducir de forma realista el funcionamiento de un centro de distribución moderno.
