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
const char* www_password = "101010";

// Estado dispositivos entrada/garage
bool puertaGarageStatus = false;
bool puertaPrincipalStatus = false;
bool luzGarageStatus = false;
bool alarmaStatus = false;
bool camaraStatus = false;

void handleRoot() {
  if (!server.authenticate(www_username, www_password)) {
    return server.requestAuthentication();
  }
  
  String html = "<!DOCTYPE html><html><head>";
  html += "<title>Control Entrada - SmartHome</title>";
  html += "<style>";
  html += "body { font-family: Arial; margin: 40px; background: #f0f0f0; }";
  html += ".device { background: white; padding: 20px; margin: 10px; border-radius: 10px; }";
  html += ".on { color: green; font-weight: bold; }";
  html += ".off { color: red; }";
  html += ".open { color: blue; font-weight: bold; }";
  html += ".closed { color: orange; }";
  html += "button { padding: 10px; margin: 5px; cursor: pointer; }";
  html += ".message { background: #e3f2fd; padding: 10px; margin: 10px; border-radius: 5px; }";
  html += ".security { background: #fff3e0; }";
  html += "</style></head><body>";
  
  html += "<h1>Control de Entrada y Garage - SmartHome</h1>";
  html += "<p>Sistema de seguridad y acceso del hogar</p>";
  
  html += "<div class='message' id='mensaje'></div>";
  
  // Puerta Principal
  html += "<div class='device security'>";
  html += "<h2>Puerta Principal</h2>";
  html += "<p>Estado: <span id='puertaPrincipalEstado' class='";
  html += puertaPrincipalStatus ? "open'>ABIERTA" : "closed'>CERRADA";
  html += "</span></p>";
  html += "<button onclick=\"controlDispositivo('puerta-principal', 'open')\">Abrir Puerta</button>";
  html += "<button onclick=\"controlDispositivo('puerta-principal', 'close')\">Cerrar Puerta</button>";
  html += "</div>";

  // Puerta Garage
  html += "<div class='device security'>";
  html += "<h2>Puerta de Garage</h2>";
  html += "<p>Estado: <span id='puertaGarageEstado' class='";
  html += puertaGarageStatus ? "open'>ABIERTA" : "closed'>CERRADA";
  html += "</span></p>";
  html += "<button onclick=\"controlDispositivo('puerta-garage', 'open')\">Abrir Garage</button>";
  html += "<button onclick=\"controlDispositivo('puerta-garage', 'close')\">Cerrar Garage</button>";
  html += "</div>";

  // Luz Garage
  html += "<div class='device'>";
  html += "<h2>Luz del Garage</h2>";
  html += "<p>Estado: <span id='luzGarageEstado' class='";
  html += luzGarageStatus ? "on'>ENCENDIDA" : "off'>APAGADA";
  html += "</span></p>";
  html += "<button onclick=\"controlDispositivo('luz-garage', 'on')\">Encender Luz</button>";
  html += "<button onclick=\"controlDispositivo('luz-garage', 'off')\">Apagar Luz</button>";
  html += "</div>";

  // Sistema de Alarma
  html += "<div class='device security'>";
  html += "<h2>Sistema de Alarma</h2>";
  html += "<p>Estado: <span id='alarmaEstado' class='";
  html += alarmaStatus ? "on'>ACTIVADA" : "off'>DESACTIVADA";
  html += "</span></p>";
  html += "<button onclick=\"controlDispositivo('alarma', 'on')\">Activar Alarma</button>";
  html += "<button onclick=\"controlDispositivo('alarma', 'off')\">Desactivar Alarma</button>";
  html += "</div>";

  // Cámara de Seguridad
  html += "<div class='device security'>";
  html += "<h2>Camara de Seguridad</h2>";
  html += "<p>Estado: <span id='camaraEstado' class='";
  html += camaraStatus ? "on'>GRABANDO" : "off'>APAGADA";
  html += "</span></p>";
  html += "<button onclick=\"controlDispositivo('camara', 'on')\">Encender Camara</button>";
  html += "<button onclick=\"controlDispositivo('camara', 'off')\">Apagar Camara</button>";
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
  html += "</script>";
  
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handlePuertaPrincipal() {
  if (server.method() == HTTP_POST) {
    String action = server.arg("action");
    if (action == "open") {
      puertaPrincipalStatus = true;
      server.send(200, "text/plain", "Puerta principal abierta");
    } else if (action == "close") {
      puertaPrincipalStatus = false;
      server.send(200, "text/plain", "Puerta principal cerrada");
    }
  }
}

void handlePuertaGarage() {
  if (server.method() == HTTP_POST) {
    String action = server.arg("action");
    if (action == "open") {
      puertaGarageStatus = true;
      server.send(200, "text/plain", "Puerta de garage abierta");
    } else if (action == "close") {
      puertaGarageStatus = false;
      server.send(200, "text/plain", "Puerta de garage cerrada");
    }
  }
}

void handleLuzGarage() {
  if (server.method() == HTTP_POST) {
    String action = server.arg("action");
    if (action == "on") {
      luzGarageStatus = true;
      server.send(200, "text/plain", "Luz del garage encendida");
    } else if (action == "off") {
      luzGarageStatus = false;
      server.send(200, "text/plain", "Luz del garage apagada");
    }
  }
}

void handleAlarma() {
  if (server.method() == HTTP_POST) {
    String action = server.arg("action");
    if (action == "on") {
      alarmaStatus = true;
      server.send(200, "text/plain", "Alarma activada");
    } else if (action == "off") {
      alarmaStatus = false;
      server.send(200, "text/plain", "Alarma desactivada");
    }
  }
}

void handleCamara() {
  if (server.method() == HTTP_POST) {
    String action = server.arg("action");
    if (action == "on") {
      camaraStatus = true;
      server.send(200, "text/plain", "Camara encendida - Grabando");
    } else if (action == "off") {
      camaraStatus = false;
      server.send(200, "text/plain", "Camara apagada");
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
  if (!MDNS.begin("controlentrada")) {
    Serial.println("Error iniciando mDNS!");
  } else {
    Serial.println("mDNS iniciado correctamente");
    MDNS.addService("http", "tcp", 80);
  }

  // Configurar endpoints
  server.on("/", handleRoot);
  server.on("/puerta-principal", handlePuertaPrincipal);
  server.on("/puerta-garage", handlePuertaGarage);
  server.on("/luz-garage", handleLuzGarage);
  server.on("/alarma", handleAlarma);
  server.on("/camara", handleCamara);
  
  server.begin();
  Serial.println("Servidor HTTP iniciado");
  Serial.println("====================================");
  Serial.println("URLs de acceso:");
  Serial.println("1. Dominio: http://controlentrada.local");
  Serial.println("2. IP: http://" + WiFi.localIP().toString());
  Serial.println("====================================");
  Serial.println("Sistema de Entrada y Garage listo");
}

void loop() {
  server.handleClient();
  delay(10);
}