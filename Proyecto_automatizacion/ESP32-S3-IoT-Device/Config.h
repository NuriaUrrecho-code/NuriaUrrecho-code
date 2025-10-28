// COMM BAUDS
#define BAUDS 115200

#define LOGGER_ENABLED            // Comentar para deshabilitar el logger por consola serie

#define LOG_LEVEL TRACE           // nivells en c_logger: TRACE, DEBUG, INFO, WARN, ERROR, FATAL, NONE

// DEVICE
//#define DEVICE_ESP_ID             "54CE0361420"   // ESP32 ID
#define DEVICE_GIIROB_PR2_ID      "06" //"giirobpr2_00"

// WIFI

//#define NET_SSID                  "UPV-PSK"
//#define NET_PASSWD                "giirob-pr2-2023"

//#define NET_SSID                  "MiFibra-9696" // Mi casa (Pablo)
//#define NET_PASSWD                "5GHQr7KD"     // Mi casa (Pablo)

//#define NET_SSID                  "MiFibra-49A3" // Mi casa (Pablo)
//#define NET_PASSWD                "MNcGX4HC"     // Mi casa (Pablo)

#define NET_SSID                  "iPhonePablo"
#define NET_PASSWD                "pablomola"

// MQTT

//#define MQTT_SERVER_IP            "mqtt.dsic.upv.es"
#define MQTT_SERVER_PORT          1883
#define MQTT_USERNAME             "giirob"    // Descomentar para conexión al broker MQTT (user/passwd)
#define MQTT_PASSWORD             "UPV2024"

// BROKER PUBLICO MQTT
#define MQTT_SERVER_IP            "broker.emqx.io"




// MQTT topics

  #define TOPIC_ENVIAR   "richi5/giirob/esp32/enviar"
  #define TOPIC_RECIBIR  "richi5/giirob/esp32/recibir"    // TODO: topic ejemplo ejercicio inicial

// IO
  // Servos
    // Revisar pines
  #define PIN_SERVO_CHOCOLATE        1  
  #define PIN_SERVO_FRESA            2
  #define PIN_SERVO_VAINILLA        42

  #define ANGULO_SERVO             180  // Ajustar con Nuria

  // Cinta
  #define PIN_CINTA                 41
  #define DELAY_CHOCOLATE         2300
  #define DELAY_FRESA             2300
  #define DELAY_VAINILLA          2300
  #define PIN_LED_CAM                3


  // Boton
  #define PIN_PULSADOR              46
  volatile bool pulsador_presionado = false;


// ESTRUCTURAS 

  #define MAX_TAREAS 10

  typedef struct {
    String tipo;
    String nombre;
    String sabor;
    int cantidad;
  } Tarea;

  struct Pedido {
    String nombre;
    String sabor;
    int cantidad;
  };
  Pedido pedidoActual;
  SemaphoreHandle_t xMutexPedido;

// Control dispensador
  // Variables globales
    String saborPedido = "";
    SemaphoreHandle_t xMutexSabor;
    SemaphoreHandle_t xSemaforoFinProduccion;
    static QueueHandle_t    colaTareas    = nullptr;
    
  // Cola sabores y cantidad
    #define MAX_PEDIDOS 10

    struct ColaPedidos {
      String* sabores;
      int* cantidades;

      int* frenteS;
      int* finS;
      int* tamanyoS;

      int* frenteC;
      int* finC;
      int* tamanyoC;

      SemaphoreHandle_t mutex;
    };
