# 🏭 Planta de Bollos Automatizada

¡Bienvenido/a al proyecto de la **Planta de Bollos Automatizada**!  
Este proyecto combina **robótica, automatización e interacción IoT** para simular una línea industrial de producción de bollos 🍩, desde la solicitud hasta la entrega, con una experiencia visual y física integrada.

---

## 🎯 Objetivo del proyecto

El propósito de este proyecto es **automatizar una planta de producción de bollos** con una **interfaz interactiva** para el usuario y una **optimización continua del proceso industrial**.

A través de una arquitectura modular, se integran distintas tecnologías que trabajan en conjunto para representar tanto la **parte física** (Arduino + cinta 3D) como la **parte digital y robótica** (RoboDK + MQTTX).

---

## ⚙️ Estructura del proyecto

El sistema se compone de **tres módulos principales**:

### 1️⃣ Módulo Arduino + MQTTX  
📡 Se encarga de la **comunicación y control interactivo**.  
- El usuario puede **solicitar un bollo** indicando su sabor a través de **MQTTX**.  
- Arduino recibe el mensaje y **activa la cinta** que inicia el proceso físico.  
- Los datos de producción se sincronizan en tiempo real con el entorno digital.

### 2️⃣ Módulo RoboDK  
🤖 Simula la **planta virtual de producción**.  
- Muestra los **procesos automáticos** que realiza la planta en paralelo al sistema físico.  
- Los movimientos de robots y cintas se actualizan en función de las órdenes recibidas.  
- Permite visualizar el flujo completo de la producción de manera precisa y didáctica.

### 3️⃣ Cinta física 3D  
🧱 Fabricada con **impresora 3D**, representa la **línea real de transporte de bollos**.  
- Movida mediante **servos controlados por Arduino**.  
- Reproduce de forma física lo que ocurre en la simulación de RoboDK.  
- Diseñada para una **experiencia educativa e interactiva**.

---

## 🧩 Tecnologías utilizadas

<p align="left">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/arduino/arduino-original.svg" width="20" height="20"/> Arduino  
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="20" height="20"/> Python  
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mqtt/mqtt-original.svg" width="20" height="20"/> MQTTX 
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/blender/blender-original.svg" width="20" height="20"/> Blender / Diseño 3D  
  <img src="https://upload.wikimedia.org/wikipedia/commons/8/83/RoboDK_logo.svg" width="20" height="20"/> RoboDK
</p>

---

## 🏗️ Funcionamiento general

1. El usuario **envía un pedido de bollo** (por ejemplo, “Chocolate” 🍫 o “Vainilla” 🍦) desde **MQTTX**.  
2. Arduino **recibe el mensaje** y **activa los servomotores** de la cinta 3D.  
3. Simultáneamente, **RoboDK refleja el proceso virtualmente**, mostrando la planta operando.  
4. El sistema **mantiene la producción continua (non-stop)**, maximizando el rendimiento sin pausas.  

---

## ⚡ Enfoque industrial

Más allá del aspecto interactivo, este proyecto se ha diseñado con una **visión industrial aplicada**:  
- Los procesos se ejecutan **de forma totalmente automática y sin interrupciones**.  
- La **planta virtual y física** trabajan en sincronía, simulando la lógica de una línea productiva real.  
- Se busca **optimizar tiempos, flujos y rendimiento**, manteniendo la producción al 100%.

---

## 🧠 Aprendizajes y aportes

- Integración de **hardware, software y simulación robótica**.  
- Control en tiempo real mediante **mensajería MQTT**.  
- Diseño y montaje de **mecánica impresa en 3D**.  
- Sincronización entre entornos **virtuales y físicos** para una experiencia inmersiva.  

---
