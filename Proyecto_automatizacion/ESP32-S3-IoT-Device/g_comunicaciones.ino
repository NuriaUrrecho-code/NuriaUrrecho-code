void suscribirseATopics() {
  
  // Suscripciones a los topics MQTT
  mqtt_subscribe(TOPIC_ENVIAR);
  //mqtt_subscribe(TOPIC_ENVIAR_WEB);
  mqtt_subscribe(TOPIC_RECIBIR);

}

void alRecibirMensajePorTopic(char* topic, String incomingMessage) {
  recibirJson_ColaTareas(topic, incomingMessage);

}

// Publica un mensaje JSON en el topic de envío hacia RoboDK.
// El mensaje contiene un campo 'evento' y un 'valor'.
  void enviarJsonAControl(String evento) {
    StaticJsonDocument<128> doc;
    doc["evento"] = evento;

    char buffer[128];
    size_t len = serializeJson(doc, buffer);

    mqtt_publish(TOPIC_ENVIAR, buffer);
  }

void enviarMensajePorTopic(const char* topic, String outgoingMessage) {

    mqtt_publish(topic, outgoingMessage.c_str());

}





