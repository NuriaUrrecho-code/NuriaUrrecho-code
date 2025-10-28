void on_setup() {
    Serial.begin(115200);
    delay(500); // Deja que arranque bien

// Set up IO
    // Dispensadores 
      servo_chocolate.attach(PIN_SERVO_CHOCOLATE);
      servo_fresa.attach(PIN_SERVO_FRESA);
      servo_vainilla.attach(PIN_SERVO_VAINILLA);
      servo_chocolate.write(0);
      servo_fresa.write(0);
      servo_vainilla.write(0);
    
    // Cinta
        pinMode(PIN_CINTA, OUTPUT);

    // LED camara
        pinMode(PIN_LED_CAM, OUTPUT);
      
    // Boton
        pinMode(PIN_PULSADOR, INPUT_PULLUP);
        attachInterrupt(digitalPinToInterrupt(PIN_PULSADOR), ISR_Pulsador, FALLING);

    // Variables locales para colas de sabores y cantidades
      static String colaSabores[MAX_PEDIDOS];
      static int colaCantidad[MAX_PEDIDOS];

      static int frente = 0, fin = 0, tamanyo = 0;
      static int frenteC = 0, finC = 0, tamanyoC = 0;

    // Crear la estructura ColaPedidos
      ColaPedidos* contextoColas = new ColaPedidos {
        .sabores   = colaSabores,
        .cantidades = colaCantidad,

        .frenteS  = &frente,
        .finS     = &fin,
        .tamanyoS = &tamanyo,

        .frenteC  = &frenteC,
        .finC     = &finC,
        .tamanyoC = &tamanyoC,

        .mutex = xSemaphoreCreateMutex()
      };

    
    
        
        
// Set up Tareas
    // Crear semáforos
        xMutexSabor = xSemaphoreCreateMutex();
        xMutexPedido = xSemaphoreCreateMutex();
        xSemaforoFinProduccion = xSemaphoreCreateBinary();
    //Camara
        setup_cam();

    // Crear tareas
        // Dispensadores
        xTaskCreatePinnedToCore(TareaControlDispensador,"Dispensador",10000, contextoColas, 1, NULL, 0);

        // Boton defectuoso
       xTaskCreatePinnedToCore(TareaPulsador, "Pulsador", 4096, NULL, 1, NULL, 1);

    // Crear la cola

  colaTareas = xQueueCreate(MAX_PEDIDOS, sizeof(Tarea));

  if (!colaTareas) {
    Serial.println("❌ Error creando la cola de tareas");
    while (true) vTaskDelay(portMAX_DELAY);
  }

  // Crear mutex
  xMutexPedido = xSemaphoreCreateMutex();
  if (!xMutexPedido) {
    Serial.println("❌ Error creando el mutex");
    while (true) vTaskDelay(portMAX_DELAY);
  }

  // Crear tarea que procesa la cola
  xTaskCreatePinnedToCore(
    Task_ProcesarTareas,   // función
    "ProcTareas",          // nombre
    4096,                  // stack
    contextoColas,               // parámetro
    1,                     // prioridad
    nullptr,               // handle
    0                      // core ESP32
  );

}