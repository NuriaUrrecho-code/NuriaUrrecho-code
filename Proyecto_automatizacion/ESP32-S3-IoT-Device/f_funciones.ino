#include <ESP32Servo.h>


Servo servo_chocolate;
Servo servo_fresa;
Servo servo_vainilla;



// FUNCIONES PARA COLA CIRULAR

  // Añade una nueva tarea a la cola circular si hay espacio disponible.
  // Devuelve true si la tarea fue añadida, false si la cola está llena.

      bool agregarTarea(const String& tipo,
                        const String& nombre,
                        const String& sabor,
                        int cantidad) {
        Tarea t{ tipo, nombre, sabor, cantidad };
        if (xQueueSend(colaTareas, &t, pdMS_TO_TICKS(10)) == pdTRUE) {
          return true;
        } else {
          Serial.println("⚠️ Cola de tareas llena");
          return false;
        }
      }
    void anyadirSaborCantidad(ColaPedidos* ctx, const String& sabor, int cantidad) {
      if (*ctx->tamanyoS < MAX_PEDIDOS && *ctx->tamanyoC < MAX_PEDIDOS) {
        ctx->sabores[*ctx->finS] = sabor;
        ctx->cantidades[*ctx->finC] = cantidad;

        *ctx->finS = (*ctx->finS + 1) % MAX_PEDIDOS;
        *ctx->tamanyoS += 1;

        *ctx->finC = (*ctx->finC + 1) % MAX_PEDIDOS;
        *ctx->tamanyoC += 1;
      } else {
        Serial.println("⚠️ Cola de sabores o cantidades llena.");
      }
    }



  // Ejecuta una tarea recibida (según su tipo y valor).

    void Task_ProcesarTareas(void* pvParameters) {
      ColaPedidos* ctx = (ColaPedidos*)pvParameters;

      Tarea tarea;
      for (;;) {
        // Bloquea hasta que haya algo que procesar
        if (xQueueReceive(colaTareas, &tarea, portMAX_DELAY) == pdTRUE) {
          if (tarea.tipo == "nuevo_pedido") {
            // Protege acceso a pedidoActual
            if (xSemaphoreTake(xMutexPedido, portMAX_DELAY)) {
              pedidoActual.nombre   = tarea.nombre;
              pedidoActual.sabor    = tarea.sabor;
              pedidoActual.cantidad = tarea.cantidad;
              anyadirSaborCantidad(ctx, pedidoActual.sabor, pedidoActual.cantidad);
              xSemaphoreGive(xMutexPedido);
            }
            // Log y envío
            log_i("📦 Pedido: %s pide %s x%d",
                  tarea.nombre.c_str(),
                  tarea.sabor.c_str(),
                  tarea.cantidad);

            StaticJsonDocument<128> doc;
            doc["evento"]   = "nuevo_pedido";
            doc["nombre"]   = pedidoActual.nombre;
            doc["sabor"]    = pedidoActual.sabor;
            doc["cantidad"] = pedidoActual.cantidad;
            char buffer[128];
            serializeJson(doc, buffer);
            enviarMensajePorTopic(TOPIC_ENVIAR, buffer);
          }
          else {
            Serial.printf("❓ Tarea desconocida: %s\n",
                          tarea.tipo.c_str());
          }
        }
      }
    }


  // Si es un JSON válido con campos 'tipo' y 'valor', lo añade a la cola de tareas.
    void recibirJson_ColaTareas(char* topic, String incomingMessage) {
      if (strcmp(topic, TOPIC_RECIBIR) == 0) {
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, incomingMessage);

        if (error) {
          warnln("Error al parsear JSON");
          return;
        }

        if (doc.containsKey("evento")) {
          String tipo = doc["evento"].as<String>();

          if (tipo == "nuevo_pedido") {
            if (!doc.containsKey("sabor") || !doc.containsKey("cantidad")) {
              warnln("JSON incompleto para nuevo_pedido");
              return;
            }

            String nombre = doc.containsKey("nombre") ? doc["nombre"].as<String>() : "anonimo";
            nombre = generarNombreConContador(nombre);
            String sabor = doc["sabor"].as<String>();
            int cantidad = doc["cantidad"];

            agregarTarea(tipo, nombre, sabor, cantidad);
          }

          // eventos como fin_produccion, defectuoso_detectado, etc.
          else if (tipo == "fin_produccion") {
            Serial.println("✅ Tarea: fin_produccion → lanzando semáforo");

            if (xSemaforoFinProduccion != NULL) {
              xSemaphoreGive(xSemaforoFinProduccion);
            } 
            else {
              Serial.println("❌ Semáforo no inicializado");
            } 
          }
        }else {
          warnln("JSON no tiene campo 'evento'");
        }
      }
    }
    
    // Función que reemplaza espacios por '_' y añade un contador creciente
      String generarNombreConContador(String texto) {
        static unsigned long contador = 0;  // preserva el valor entre llamadas
        contador++;                         // incrementa en cada llamada

        // Reemplaza todos los espacios por guiones bajos
        texto.toLowerCase(); 
        texto.replace(' ', '_');

        // Añade el número actual
        
        texto += String(contador);

        return texto;
      }
    

// FUNCIONES CONTROL ENTRADAS Y SALIDAS
  // Funciones servos
    //Funcionamiento de los servos

      void activar_servo(String sabor) {
        Servo* servo_ptr = nullptr;

        if (sabor == "chocolate") servo_ptr = &servo_chocolate;
        else if (sabor == "fresa") servo_ptr = &servo_fresa;
        else if (sabor == "vainilla") servo_ptr = &servo_vainilla;
        else {
          Serial.println("⚠️ Sabor no reconocido");
          
        }
        //Movimiento servo
        
          
            servo_ptr->write(180);  
            //delay(10);             
          
            delay(500);
          
          
            servo_ptr->write(0);  
            //delay(10);             
          
          
        
        
      }
    // Activar servos
        void activarServoChocolate(int cant) {
          digitalWrite(PIN_CINTA, HIGH);
          for (int i = 0; i < cant; i++){
              activar_servo("chocolate");
              delay(1000);
          }
                    
          delay(DELAY_CHOCOLATE);
          digitalWrite(PIN_CINTA, LOW);
        }

        void activarServoFresa(int cant) {
          digitalWrite(PIN_CINTA, HIGH);
          for (int i = 0; i < cant; i++){
              activar_servo("fresa");
              delay(1000);
          }
                    
          delay(DELAY_FRESA);
          digitalWrite(PIN_CINTA, LOW);
        }

        void activarServoVainilla(int cant) {
          digitalWrite(PIN_CINTA, HIGH);
          for (int i = 0; i < cant; i++){
              activar_servo("vainilla");
              delay(1000);
          }
                    
          delay(DELAY_VAINILLA);
          digitalWrite(PIN_CINTA, LOW);
        }



// TAREAS

  //Tarea control dispensador
    void TareaControlDispensador(void *pvParameters) {
      ColaPedidos* ctx = (ColaPedidos*)pvParameters;  // Acceso a la estructura

      for (;;) {
        log_i("🌀 Esperando semáforo de fin_producción...");

        if (xSemaphoreTake(xSemaforoFinProduccion, portMAX_DELAY)) {
          infoln("🟢 Semáforo recibido. Activando dispensador...");

          String sabor;
          int cant;

          if (xSemaphoreTake(ctx->mutex, portMAX_DELAY)) {
            // Extraemos sabor
            if (*ctx->tamanyoS > 0) {
              sabor = ctx->sabores[*ctx->frenteS];
              *ctx->frenteS = (*ctx->frenteS + 1) % MAX_PEDIDOS;
              *ctx->tamanyoS -= 1;
            } else {
              Serial.println("⚠️ Cola de sabores vacía.");
            }

            // Extraemos cantidad
            if (*ctx->tamanyoC > 0) {
              cant = ctx->cantidades[*ctx->frenteC];
              *ctx->frenteC = (*ctx->frenteC + 1) % MAX_PEDIDOS;
              *ctx->tamanyoC -= 1;
            } else {
              Serial.println("⚠️ Cola de cantidades vacía.");
            }

            xSemaphoreGive(ctx->mutex);
          } else {
            infoln("❌ Error al tomar el mutex del sabor");
            vTaskDelay(100 / portTICK_PERIOD_MS);
            continue;
          }

          if (sabor == "chocolate") {
            infoln("🍫 Activando servo de CHOCOLATE");
            activarServoChocolate(cant);
          } else if (sabor == "fresa") {
            infoln("🍓 Activando servo de FRESA");
            activarServoFresa(cant);
          } else if (sabor == "vainilla") {
            infoln("🍦 Activando servo de VAINILLA");
            activarServoVainilla(cant);
          } else {
            log_w("⚠️ Sabor desconocido: '%s'. No se activa ningún servo.", sabor.c_str());
          }

          vTaskDelay(100 / portTICK_PERIOD_MS);  // Pequeña pausa de seguridad
        }
      }
    }

  // Tarea paarda de emergencia
    void IRAM_ATTR ISR_Pulsador() {
      pulsador_presionado = true;
    }

    void TareaPulsador(void *pvParameters) {
      bool enviarStop = true;
      TickType_t xLastWakeTime = xTaskGetTickCount();
      const TickType_t periodo = pdMS_TO_TICKS(50);

      for (;;) {
        if (pulsador_presionado) {
          detachInterrupt(digitalPinToInterrupt(PIN_PULSADOR));
          pulsador_presionado = false;

          StaticJsonDocument<128> doc;
          doc["evento"] = enviarStop ? "stop" : "start";
          enviarStop = !enviarStop;

          char buffer[128];
          serializeJson(doc, buffer);
          infoln("🔴 Pulsador presionado (interrupción): enviando");
          enviarMensajePorTopic(TOPIC_ENVIAR, buffer);
          vTaskDelay(pdMS_TO_TICKS(200));  // Ligera pausa
          attachInterrupt(digitalPinToInterrupt(PIN_PULSADOR), ISR_Pulsador, FALLING);

        }

        vTaskDelayUntil(&xLastWakeTime, periodo);      
      }
    }




