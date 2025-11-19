#include <ESPmDNS.h>
#include <WiFi.h>
#include <WebServer.h>

//Configuración WiFi - RED VULNERABLE

/*
const char* ssid = "Home_Secure_Network";
const char* password = "password123";
*/


const char* ssid = "Red_Test_IoT";
const char* password = "Password1";

WebServer server(80);

// Credenciales VULNERABLES
const char* www_username = "admin";
const char* www_password = "123456";

// Estado dispositivos sala
bool tvStatus = false;
bool luzStatus = false;
bool aireStatus = false;
bool lamparaStatus = false;
int temperatura = 22;
String colorLampara = "blanco";

void handleRoot() {
  if (!server.authenticate(www_username, www_password)) {
    return server.requestAuthentication();
  }
  
  String html = "<!DOCTYPE html><html><head>";
  html += "<title>Control Sala - SmartHome</title>";
  html += "<style>";
  html += "body { font-family: Arial; margin: 40px; background: #f0f0f0; }";
  html += ".device { background: white; padding: 20px; margin: 10px; border-radius: 10px; }";
  html += ".on { color: green; font-weight: bold; }";
  html += ".off { color: red; }";
  html += "button { padding: 10px; margin: 5px; cursor: pointer; }";
  html += ".message { background: #e3f2fd; padding: 10px; margin: 10px; border-radius: 5px; }";
  html += "</style></head><body>";
  
  html += "<h1>Control de Sala - SmartHome</h1>";
  html += "<p>Bienvenido al sistema de automatizacion del hogar</p>";
  
  html += "<div class='message' id='mensaje'></div>";
  
  // Televisor
  html += "<div class='device'>";
  html += "<h2>Televisor Samsung</h2>";
  html += "<p>Estado: <span id='tvEstado' class='";
  html += tvStatus ? "on'>ENCENDIDO" : "off'>APAGADO";
  html += "</span></p>";
  html += "<button onclick=\"controlDispositivo('tv', 'on')\">Encender TV</button>";
  html += "<button onclick=\"controlDispositivo('tv', 'off')\">Apagar TV</button>";
  html += "</div>";

  // Luz Principal
  html += "<div class='device'>";
  html += "<h2>Luz Principal</h2>";
  html += "<p>Estado: <span id='luzEstado' class='";
  html += luzStatus ? "on'>ENCENDIDA" : "off'>APAGADA";
  html += "</span></p>";
  html += "<button onclick=\"controlDispositivo('luz', 'on')\">Encender Luz</button>";
  html += "<button onclick=\"controlDispositivo('luz', 'off')\">Apagar Luz</button>";
  html += "</div>";

  // Aire Acondicionado
  html += "<div class='device'>";
  html += "<h2>Aire Acondicionado</h2>";
  html += "<p>Estado: <span id='aireEstado' class='";
  html += aireStatus ? "on'>ENCENDIDO" : "off'>APAGADO";
  html += "</span></p>";
  html += "<p>Temperatura: <span id='temperatura'>";
  html += String(temperatura);
  html += "</span>C</p>";
  html += "<button onclick=\"controlDispositivo('aire', 'on')\">Encender Aire</button>";
  html += "<button onclick=\"controlDispositivo('aire', 'off')\">Apagar Aire</button>";
  html += "<br>";
  html += "<input type='number' id='tempInput' value='";
  html += String(temperatura);
  html += "' min='16' max='30'>";
  html += "<button onclick=\"cambiarTemperatura()\">Cambiar Temp</button>";
  html += "</div>";

  // Lámpara RGB
  html += "<div class='device'>";
  html += "<h2>Lampara RGB</h2>";
  html += "<p>Estado: <span id='lamparaEstado' class='";
  html += lamparaStatus ? "on'>ENCENDIDA" : "off'>APAGADA";
  html += "</span></p>";
  html += "<p>Color: <span id='colorLampara'>";
  html += colorLampara;
  html += "</span></p>";
  html += "<button onclick=\"controlDispositivo('lampara', 'on')\">Encender Lampara</button>";
  html += "<button onclick=\"controlDispositivo('lampara', 'off')\">Apagar Lampara</button>";
  html += "<br>";
  html += "<select id='colorSelect'>";
  html += "<option value='blanco'>Blanco</option>";
  html += "<option value='rojo'>Rojo</option>";
  html += "<option value='azul'>Azul</option>";
  html += "<option value='verde'>Verde</option>";
  html += "</select>";
  html += "<button onclick=\"cambiarColor()\">Cambiar Color</button>";
  html += "</div>";

  // JavaScript
  html += "<script>";
  html += "function controlDispositivo(dispositivo, accion) {";
  html += "var formData = new FormData();";
  html += "formData.append('action', accion);";
  html += "fetch('/' + dispositivo, {";
  html += "method: 'POST',";
  html += "body: formData";
  html += "})";
  html += ".then(response => response.text())";
  html += ".then(data => {";
  html += "document.getElementById('mensaje').innerHTML = data;";
  html += "setTimeout(() => { location.reload(); }, 1000);";
  html += "})";
  html += ".catch(error => {";
  html += "document.getElementById('mensaje').innerHTML = 'Error: ' + error;";
  html += "});";
  html += "}";
  
  html += "function cambiarTemperatura() {";
  html += "var temp = document.getElementById('tempInput').value;";
  html += "var formData = new FormData();";
  html += "formData.append('action', 'temp');";
  html += "formData.append('temp', temp);";
  html += "fetch('/aire', {";
  html += "method: 'POST',";
  html += "body: formData";
  html += "})";
  html += ".then(response => response.text())";
  html += ".then(data => {";
  html += "document.getElementById('mensaje').innerHTML = data;";
  html += "setTimeout(() => { location.reload(); }, 1000);";
  html += "});";
  html += "}";
  
  html += "function cambiarColor() {";
  html += "var color = document.getElementById('colorSelect').value;";
  html += "var formData = new FormData();";
  html += "formData.append('action', 'color');";
  html += "formData.append('color', color);";
  html += "fetch('/lampara', {";
  html += "method: 'POST',";
  html += "body: formData";
  html += "})";
  html += ".then(response => response.text())";
  html += ".then(data => {";
  html += "document.getElementById('mensaje').innerHTML = data;";
  html += "setTimeout(() => { location.reload(); }, 1000);";
  html += "});";
  html += "}";
  
  html += "document.getElementById('colorSelect').value = '";
  html += colorLampara;
  html += "';";
  html += "</script>";
  
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handleTV() {
  if (server.method() == HTTP_POST) {
    String action = server.arg("action");
    if (action == "on") {
      tvStatus = true;
      server.send(200, "text/plain", "TV encendida");
    } else if (action == "off") {
      tvStatus = false;
      server.send(200, "text/plain", "TV apagada");
    }
  }
}

void handleLuz() {
  if (server.method() == HTTP_POST) {
    String action = server.arg("action");
    if (action == "on") {
      luzStatus = true;
      server.send(200, "text/plain", "Luz encendida");
    } else if (action == "off") {
      luzStatus = false;
      server.send(200, "text/plain", "Luz apagada");
    }
  }
}

void handleAire() {
  if (server.method() == HTTP_POST) {
    String action = server.arg("action");
    if (action == "on") {
      aireStatus = true;
      server.send(200, "text/plain", "Aire acondicionado encendido");
    } else if (action == "off") {
      aireStatus = false;
      server.send(200, "text/plain", "Aire acondicionado apagado");
    } else if (action == "temp") {
      temperatura = server.arg("temp").toInt();
      server.send(200, "text/plain", "Temperatura cambiada a: " + String(temperatura) + "C");
    }
  }
}

void handleLampara() {
  if (server.method() == HTTP_POST) {
    String action = server.arg("action");
    if (action == "on") {
      lamparaStatus = true;
      server.send(200, "text/plain", "Lampara encendida");
    } else if (action == "off") {
      lamparaStatus = false;
      server.send(200, "text/plain", "Lampara apagada");
    } else if (action == "color") {
      colorLampara = server.arg("color");
      server.send(200, "text/plain", "Color cambiado a: " + colorLampara);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  // Conectar a WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConectado! IP: " + WiFi.localIP().toString());
  
  // Inicializar mDNS CORREGIDO
  if (!MDNS.begin("controlsala")) {
    Serial.println("Error iniciando mDNS!");
  } else {
    Serial.println("mDNS iniciado correctamente");
    MDNS.addService("http", "tcp", 80);
  }

  // Configurar endpoints
  server.on("/", handleRoot);
  server.on("/tv", handleTV);
  server.on("/luz", handleLuz);
  server.on("/aire", handleAire);
  server.on("/lampara", handleLampara);
  
  server.begin();
  Serial.println("Servidor HTTP iniciado");
  Serial.println("====================================");
  Serial.println("URLs de acceso:");
  Serial.println("1. Dominio: http://controlsala.local");
  Serial.println("2. IP: http://" + WiFi.localIP().toString());
  Serial.println("====================================");
  Serial.println("Credenciales: admin / 88888888");
  Serial.println("Sistema de Control de Sala listo");
}

void loop() {
  server.handleClient();
  delay(10);
}