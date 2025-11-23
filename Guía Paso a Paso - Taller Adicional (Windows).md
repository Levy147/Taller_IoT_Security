# **GUÍA PASO A PASO - TALLER ADICIONAL DE SEGURIDAD IoT (WSL)**

## **ÍNDICE**
1. [Preparación del Entorno WSL](#preparación-del-entorno-wsl)
2. [Configuración Inicial](#configuración-inicial)
3. [Fase 1: Reconocimiento](#fase-1-reconocimiento)
4. [Fase 2: Ataque y Compromiso](#fase-2-ataque-y-compromiso)
5. [Fase 3: Análisis y Explotación](#fase-3-análisis-y-explotación)
6. [Fase 4: Demostración de Botnet](#fase-4-demostración-de-botnet)
7. [Fase 5: Panel Web de Control](#fase-5-panel-web-de-control)
8. [Fase 6: Herramientas Defensivas](#fase-6-herramientas-defensivas)
9. [Ejercicios Adicionales](#ejercicios-adicionales)
10. [Solución de Problemas Comunes](#solución-de-problemas-comunes)
11. [Verificación Final](#verificación-final)

---

## **PREPARACIÓN DEL ENTORNO WSL**

### **Paso 1.1: Verificar Requisitos del Sistema**

Abre PowerShell como **Administrador** y ejecuta:

```powershell
# Verificar versión de Windows (debe ser Windows 10 versión 2004 o superior, o Windows 11)
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# Verificar si WSL ya está instalado
wsl --status
```

**Requisitos:**
- Windows 10 versión 2004 o superior, o Windows 11
- Al menos 4GB de RAM disponible
- Conexión a Internet
- Acceso de administrador

### **Paso 1.2: Instalar WSL**

En PowerShell como **Administrador**:

```powershell
# Instalar WSL con Ubuntu (versión más reciente)
wsl --install
```

**Después de ejecutar:**
1. Reinicia tu computadora cuando se te solicite
2. Al reiniciar, se abrirá automáticamente una ventana de Ubuntu
3. Crea un usuario y contraseña para Ubuntu (anótalos)

**Tiempo estimado:** 10-15 minutos (incluyendo reinicio)

### **Paso 1.3: Actualizar WSL**

Después del reinicio, abre **Ubuntu** desde el menú de inicio y ejecuta:

```bash
# Actualizar paquetes
sudo apt update
sudo apt upgrade -y
```

### **Paso 1.4: Instalar Herramientas Necesarias**

```bash
# Instalar herramientas necesarias
sudo apt install -y hydra nmap curl python3 python3-pip git wordlists

# Verificar instalación
python3 --version
nmap --version
hydra -h | head -5
```

**Resultado esperado:** Todas las herramientas deberían mostrar sus versiones.

### **Paso 1.5: Verificar Wordlist rockyou.txt**

```bash
# Verificar que rockyou.txt existe
ls -lh /usr/share/wordlists/rockyou.txt

# Si no existe, descargar manualmente
if [ ! -f /usr/share/wordlists/rockyou.txt ]; then
    cd /tmp
    wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt
    sudo mv rockyou.txt /usr/share/wordlists/
    cd ~
fi

# Verificar tamaño (debe ser ~133MB)
ls -lh /usr/share/wordlists/rockyou.txt
```

### **Paso 1.6: Instalar Bibliotecas Python**

**⚠️ IMPORTANTE:** En Ubuntu/Debian recientes, puede aparecer el error "externally-managed-environment". Usa el siguiente comando:

```bash
# Instalar dependencias Python con flags necesarios
# Si hay conflicto con blinker, usar --ignore-installed
pip3 install --break-system-packages --ignore-installed blinker requests flask scapy

# Si el comando anterior falla, instalar por separado:
pip3 install --break-system-packages requests
pip3 install --break-system-packages --ignore-installed blinker flask
pip3 install --break-system-packages scapy

# Verificar instalación
python3 -c "import requests; import flask; import scapy; print('Todas las bibliotecas instaladas correctamente')"
```

**Nota:** Los flags `--break-system-packages` y `--ignore-installed` son necesarios en Ubuntu/Debian recientes debido a PEP 668. Esto es seguro para entornos de taller/educativos.

**Alternativa con Entorno Virtual (Opcional):**
Si prefieres usar un entorno virtual (mejor práctica):

```bash
# Instalar python3-venv
sudo apt install -y python3-venv

# Crear entorno virtual
python3 -m venv ~/iot_taller_env

# Activar entorno virtual
source ~/iot_taller_env/bin/activate

# Instalar dependencias
pip install requests flask scapy

# Verificar
python -c "import requests; import flask; import scapy; print('OK')"
```

**⚠️ IMPORTANTE:** Si usas entorno virtual, debes activarlo cada vez que abras una nueva terminal:
```bash
source ~/iot_taller_env/bin/activate
```

### **Paso 1.7: Acceder a Archivos de Windows desde WSL**

Los archivos de Windows están disponibles en WSL en `/mnt/c/` o `/mnt/h/`:

```bash
# Ver tus archivos de Windows
ls /mnt/c/Users/TuUsuario/

# Navegar al directorio del taller (ajusta la ruta según tu ubicación)
cd /mnt/h/"Material para Taller"/Codigos\ Python

# O si está en C:
cd /mnt/c/Users/TuUsuario/"Material para Taller"/Codigos\ Python

# Verificar que todos los scripts están presentes
ls -la *.py
```

**Nota:** Reemplaza `TuUsuario` con tu nombre de usuario de Windows.

---

## **CONFIGURACIÓN INICIAL**

### **Paso 2.1: Navegar al Directorio del Proyecto**

```bash
# Navegar al directorio (ajusta la ruta según tu ubicación)
cd /mnt/h/"Material para Taller"/Codigos\ Python

# O si está en C:
cd /mnt/c/Users/TuUsuario/"Material para Taller"/Codigos\ Python

# Verificar scripts
ls -la *.py
```

**Resultado esperado:** Deberías ver los 6 scripts Python.

### **Paso 2.2: Verificar Conectividad de Red**

```bash
# Obtener tu dirección IP
hostname -I

# O más detallado
ip addr show | grep "inet " | grep -v 127.0.0.1

# Obtener la puerta de enlace
ip route | grep default
```

**Anota los siguientes datos:**
- Tu IP: `_________________`
- Rango de red: `_________________` (ejemplo: 192.168.86.0)
- Gateway: `_________________`

### **Paso 2.3: Configurar Dispositivos ESP32**

1. **Abrir Arduino IDE en Windows** (funciona normalmente desde Windows)
2. **Para ESP32 Simulador de Sala:**
   - Cargar: `Codigos IoT/ESP32_Simulador_de_Sala/ESP32_Simulador_de_Sala.ino`
   - Configurar credenciales WiFi:
     ```cpp
     const char* ssid = "TU_WIFI_SSID";
     const char* password = "TU_WIFI_PASSWORD";
     ```
   - Subir firmware al ESP32
   - Anotar IP asignada: `_________________` (típicamente 192.168.86.114)

3. **Para ESP32 Simulador de Entrada:**
   - Cargar: `Codigos IoT/ESP32_Simulador_de_Entrada/ESP32_Simulador_de_Entrada.ino`
   - Configurar las mismas credenciales WiFi
   - Subir firmware al ESP32
   - Anotar IP asignada: `_________________` (típicamente 192.168.86.115)

### **Paso 2.4: Verificar Conectividad con los ESP32**

```bash
# Probar conectividad
ping -c 4 192.168.86.114  # Reemplazar con IP real del ESP32 Sala
ping -c 4 192.168.86.115  # Reemplazar con IP real del ESP32 Entrada

# Probar acceso HTTP
curl -I http://192.168.86.114/
curl -I http://192.168.86.115/
```

**Resultado esperado:** 
- Ping exitoso (0% packet loss)
- Respuesta HTTP 401 (Unauthorized) - esto es correcto, significa que el dispositivo requiere autenticación

### **Paso 2.5: Verificar Credenciales por Defecto**

```bash
# Probar credenciales del ESP32 Sala (admin:123456)
curl -u admin:123456 http://192.168.86.114/

# Probar credenciales del ESP32 Entrada (user:12345)
curl -u user:12345 http://192.168.86.115/
```

**Resultado esperado:** Respuesta HTTP 200 (OK) con contenido HTML/JSON.

---

## **FASE 1: RECONOCIMIENTO**

### **Paso 3.1: Ejecutar Network Scanner**

```bash
# Asegúrate de estar en el directorio correcto
cd /mnt/h/"Material para Taller"/Codigos\ Python

# Ejecutar el scanner de red
python3 1-network_scanner.py
```

**¿Qué observar?**
- El script escaneará el rango de red automáticamente
- Verás progreso en tiempo real
- Identificará dispositivos activos y sus puertos abiertos
- Buscará específicamente dispositivos IoT

**Tiempo estimado:** 10-15 minutos

### **Paso 3.2: Verificar Resultados del Escaneo**

```bash
# Verificar que se generó el archivo de resultados
ls -lh scan_results.log

# Ver contenido del archivo (primeras líneas)
head -20 scan_results.log
```

**Resultado esperado:** 
- Archivo `scan_results.log` creado
- Debe contener información JSON con dispositivos encontrados
- Deberías ver tus ESP32 listados

### **Paso 3.3: Analizar Resultados**

```bash
# Ver resultados formateados
cat scan_results.log | python3 -m json.tool | less

# O simplemente ver el contenido
cat scan_results.log
```

**Preguntas para reflexión:**
- ¿Cuántos dispositivos se encontraron?
- ¿Qué puertos están abiertos?
- ¿Se identificaron correctamente los ESP32?
- ¿Hay otros dispositivos IoT en la red?

---

## **FASE 2: ATAQUE Y COMPROMISO**

### **Paso 4.1: Ejecutar Dictionary Attack**

```bash
# Ejecutar el ataque de diccionario
python3 2-real_dictionary_attack.py
```

**¿Qué observar?**
- El script primero descubrirá dispositivos IoT automáticamente
- Cargará la wordlist rockyou.txt
- Probará credenciales comunes en cada dispositivo
- Mostrará progreso en tiempo real con estadísticas

**Tiempo estimado:** 20-30 minutos (puede variar según velocidad de red)

**Nota importante:** Este proceso puede tomar tiempo. El script probará múltiples combinaciones de usuario/contraseña.

### **Paso 4.2: Verificar Credenciales Comprometidas**

```bash
# Verificar que se generó el archivo de dispositivos comprometidos
ls -lh compromised_devices.json

# Ver el contenido
cat compromised_devices.json | python3 -m json.tool
```

**Resultado esperado:**
- Archivo `compromised_devices.json` creado
- Debe contener las credenciales de los ESP32 comprometidos
- Formato JSON con IP, usuario y contraseña

### **Paso 4.3: Validar Credenciales Manualmente**

```bash
# Probar las credenciales encontradas (reemplazar con valores reales)
curl -u admin:123456 http://192.168.86.114/
curl -u user:12345 http://192.168.86.115/
```

**Resultado esperado:** Acceso exitoso a ambos dispositivos.

### **Paso 4.4: Reflexión sobre Seguridad**
**Preguntas para discusión:**
- ¿Por qué las contraseñas por defecto son peligrosas?
- ¿Cuánto tiempo tomó comprometer los dispositivos?
- ¿Qué medidas podrían prevenir este ataque?

---

## **FASE 3: ANÁLISIS Y EXPLOTACIÓN**

### **Paso 5.1: Ejecutar IoT Analyzer**

```bash
# Ejecutar el analizador de vulnerabilidades
python3 3-iot_analyzer.py
```

**¿Qué observar?**
- El script leerá el archivo `compromised_devices.json`
- Probará credenciales por defecto
- Escaneará endpoints sin autenticación
- Intentará explotar controles remotos
- Generará un reporte de vulnerabilidades

**Tiempo estimado:** 20-25 minutos

### **Paso 5.2: Revisar Reporte de Vulnerabilidades**

```bash
# Ver el reporte generado
cat vulnerability_report.txt

# O abrir en un editor
nano vulnerability_report.txt
```

**Resultado esperado:**
- Archivo `vulnerability_report.txt` con análisis detallado
- Lista de vulnerabilidades encontradas
- Recomendaciones de seguridad

### **Paso 5.3: Probar Explotación Manual**

```bash
# Controlar dispositivos usando las credenciales comprometidas

# ESP32 Sala - Encender TV
curl -u admin:123456 -X POST http://192.168.86.114/control/tv -d "state=on"

# ESP32 Sala - Encender luces
curl -u admin:123456 -X POST http://192.168.86.114/control/lights -d "state=on"

# ESP32 Entrada - Abrir puerta
curl -u user:12345 -X POST http://192.168.86.115/control/door -d "state=open"

# ESP32 Entrada - Desactivar alarma
curl -u user:12345 -X POST http://192.168.86.115/control/alarm -d "state=off"
```

**Resultado esperado:** Comandos ejecutados exitosamente (si los endpoints existen en tu firmware).

### **Paso 5.4: Documentar Hallazgos**
Crea un documento con:
- Vulnerabilidades encontradas
- Impacto potencial de cada vulnerabilidad
- Recomendaciones de mitigación

---

## **FASE 4: DEMOSTRACIÓN DE BOTNET**

### **Paso 6.1: Verificar Archivo Requerido**

```bash
# Asegurarse de que existe el archivo de dispositivos comprometidos
ls -lh compromised_devices.json

# Verificar contenido
cat compromised_devices.json
```

**Importante:** Este script requiere que el archivo `compromised_devices.json` exista y tenga contenido válido.

### **Paso 6.2: Ejecutar Botnet Demo**

```bash
# Ejecutar la demostración de botnet
python3 4-botnet_demo.py
```

**¿Qué observar?**
- El script cargará los dispositivos comprometidos
- Establecerá comunicación con cada bot
- Mostrará un dashboard de control
- Coordinará ataques DDoS simulados
- Mostrará métricas en tiempo real

**Tiempo estimado:** 15-20 minutos

### **Paso 6.3: Interactuar con la Botnet**
El script mostrará un menú interactivo. Prueba los siguientes comandos:
- Ver estado de todos los bots
- Iniciar un ataque coordinado
- Ver estadísticas
- Monitorear actividad

### **Paso 6.4: Observar Comportamiento Coordinado**
**Preguntas para análisis:**
- ¿Cómo se coordinan los dispositivos?
- ¿Qué tipo de tráfico generan?
- ¿Cómo se detectaría esto en una red real?
- ¿Qué medidas defensivas serían efectivas?

---

## **FASE 5: PANEL WEB DE CONTROL**

### **Paso 7.1: Verificar Dependencias**

```bash
# Verificar que Flask está instalado
python3 -c "import flask; print('Flask instalado correctamente')"
```

Si no está instalado:
```bash
pip3 install --break-system-packages --ignore-installed blinker flask
```

### **Paso 7.2: Ejecutar Panel Web**

```bash
# Ejecutar el controlador web
python3 5-botnet_web_controller.py
```

**¿Qué observar?**
- El script iniciará un servidor Flask
- Verás un mensaje indicando la URL (típicamente http://127.0.0.1:5000)
- El servidor seguirá corriendo hasta que lo detengas

**Tiempo estimado:** 10-15 minutos de uso

### **Paso 7.3: Acceder al Panel Web**

1. Abre un navegador web en **Windows**
2. Navega a: `http://localhost:5000`
3. Observa el dashboard en tiempo real

**Características a explorar:**
- Estado de cada bot
- Estadísticas de actividad
- Control remoto de dispositivos
- Actualización automática de estado

### **Paso 7.4: Probar Funcionalidades**
- Monitorear el estado de los dispositivos
- Enviar comandos a dispositivos específicos
- Observar cambios en tiempo real
- Revisar métricas y estadísticas

### **Paso 7.5: Detener el Servidor**
Cuando termines, presiona `Ctrl+C` en la terminal para detener el servidor.

---

## **FASE 6: HERRAMIENTAS DEFENSIVAS**

### **Paso 8.1: Ejecutar Security Tool**

```bash
# Ejecutar herramientas defensivas
python3 6-security_tool.py
```

**¿Qué observar?**
- El script escaneará la red nuevamente
- Creará un inventario de dispositivos
- Evaluará configuraciones de seguridad
- Generará recomendaciones de hardening
- Creará un reporte de estado de seguridad

**Tiempo estimado:** 10-15 minutos

### **Paso 8.2: Revisar Reporte de Seguridad**

```bash
# Ver el reporte generado
cat security_report.txt

# O abrir en un editor
nano security_report.txt
```

**Resultado esperado:**
- Archivo `security_report.txt` con evaluación completa
- Lista de dispositivos y su estado de seguridad
- Recomendaciones específicas para cada dispositivo

### **Paso 8.3: Implementar Recomendaciones**
Revisa las recomendaciones y considera:
- Cambiar credenciales por defecto
- Deshabilitar servicios innecesarios
- Implementar autenticación más fuerte
- Configurar monitoreo continuo

### **Paso 8.4: Comparar Antes y Después**
**Preguntas para reflexión:**
- ¿Qué vulnerabilidades se identificaron?
- ¿Cuáles son las más críticas?
- ¿Qué medidas son más fáciles de implementar?
- ¿Cómo se podría automatizar el monitoreo?

---

## **EJERCICIOS ADICIONALES**

### **Ejercicio 1: Análisis Profundo de Red**
```bash
# Usar nmap para análisis más detallado
nmap -sV -sC -O 192.168.86.114
nmap -sV -sC -O 192.168.86.115

# Guardar resultados
nmap -sV -sC -O 192.168.86.114 -oN nmap_esp32_sala.txt
nmap -sV -sC -O 192.168.86.115 -oN nmap_esp32_entrada.txt
```

**Tarea:** Comparar los resultados con los del script 1.

### **Ejercicio 2: Crear Wordlist Personalizada**
```bash
# Crear una wordlist con contraseñas comunes de IoT
cat > custom_wordlist.txt << EOF
admin
123456
password
12345
root
user
guest
1234
admin123
password123
EOF

# Modificar el script 2 para usar esta wordlist
```

**Tarea:** Modificar `2-real_dictionary_attack.py` para usar tu wordlist personalizada.

### **Ejercicio 3: Monitoreo de Tráfico**
```bash
# Instalar tcpdump
sudo apt install -y tcpdump

# Capturar tráfico de red mientras se ejecutan los scripts
sudo tcpdump -i any -w iot_traffic.pcap host 192.168.86.114 or host 192.168.86.115

# Analizar con Wireshark (instalar en Windows)
# wireshark iot_traffic.pcap
```

**Tarea:** Identificar patrones de tráfico malicioso.

### **Ejercicio 4: Script de Hardening Automático**
Crea un script que:
- Cambie credenciales por defecto
- Deshabilite servicios innecesarios
- Configure logging
- Implemente rate limiting

### **Ejercicio 5: Dashboard de Monitoreo Mejorado**
Modifica el script 5 para agregar:
- Gráficos de actividad
- Alertas en tiempo real
- Historial de eventos
- Exportación de reportes

---

## **SOLUCIÓN DE PROBLEMAS COMUNES**

### **Problema 1: "WSL no se instala"**

**Solución:**
```powershell
# Habilitar características necesarias manualmente
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Reiniciar y luego:
wsl --set-default-version 2
wsl --install -d Ubuntu
```

### **Problema 2: "No se encuentran dispositivos IoT"**

**Solución:**
```bash
# WSL puede tener problemas con la red, verificar:
ip addr show

# Si no tienes IP, reiniciar WSL:
wsl --shutdown
# Luego abrir Ubuntu de nuevo desde Windows
```

### **Problema 3: "Error al importar módulos Python" o "externally-managed-environment"**

**Solución Rápida:**
```bash
# Usar flag --break-system-packages
pip3 install --break-system-packages --ignore-installed blinker requests flask scapy

# Verificar instalación
python3 -c "import requests; import flask; import scapy; print('OK')"
```

### **Problema 4: "Cannot uninstall blinker" o "RECORD file not found"**

**Solución:**
```bash
# Instalar flask ignorando el conflicto de blinker
pip3 install --break-system-packages --ignore-installed blinker flask

# O instalar todo junto
pip3 install --break-system-packages --ignore-installed blinker requests flask scapy

# Verificar instalación
python3 -c "import flask; print('Flask OK')"
```

**Explicación:** `--ignore-installed` le dice a pip que ignore la versión instalada por el sistema y use la nueva versión sin intentar desinstalar la anterior.

### **Problema 5: "rockyou.txt no encontrado"**

**Solución:**
```bash
# Instalar wordlists
sudo apt install -y wordlists

# O descargar manualmente
cd /tmp
wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt
sudo mv rockyou.txt /usr/share/wordlists/
cd ~
```

### **Problema 6: "Flask no accesible desde Windows cuando se ejecuta en WSL"**

**Solución:**
```bash
# En WSL, modificar el script para escuchar en 0.0.0.0:
# Cambiar: app.run(debug=True)
# A: app.run(host='0.0.0.0', port=5000, debug=True)

# O obtener la IP de WSL:
hostname -I

# Y acceder desde Windows usando esa IP o simplemente usar localhost:5000
```

**Nota:** Normalmente `localhost:5000` desde Windows debería funcionar automáticamente con WSL2.

### **Problema 7: "Permisos denegados en escaneos"**

**Solución:**
```bash
# Algunos escaneos requieren permisos de root
sudo python3 1-network_scanner.py
```

### **Problema 8: "Los ESP32 no responden desde WSL"**

**Solución:**
- Verificar que WSL puede acceder a la red de Windows
- Probar ping desde WSL: `ping -c 4 192.168.86.114`
- Verificar que los ESP32 están en la misma red WiFi
- Reiniciar WSL si es necesario: `wsl --shutdown`

### **Problema 9: "Rutas de archivos no funcionan"**

**Solución:**
- En WSL, usa rutas de Windows: `/mnt/c/` o `/mnt/h/`
- Usa comillas para rutas con espacios: `cd "/mnt/h/Material para Taller/Codigos Python"`
- Verifica que los archivos existen: `ls -la`

---

## **VERIFICACIÓN FINAL**

### **Checklist de Completación**

Marca cada ítem cuando lo completes:

- [ ] WSL instalado y configurado
- [ ] Todas las herramientas instaladas
- [ ] Dispositivos ESP32 configurados y accesibles
- [ ] Script 1 ejecutado - Escaneo de red completado
- [ ] Script 2 ejecutado - Credenciales comprometidas
- [ ] Script 3 ejecutado - Análisis de vulnerabilidades
- [ ] Script 4 ejecutado - Demostración de botnet
- [ ] Script 5 ejecutado - Panel web funcionando
- [ ] Script 6 ejecutado - Herramientas defensivas
- [ ] Todos los archivos de reporte generados
- [ ] Ejercicios adicionales completados (opcional)

### **Archivos Generados Esperados**
```bash
# Verificar todos los archivos generados
ls -lh *.log *.json *.txt 2>/dev/null

# Deberías ver:
# - scan_results.log
# - compromised_devices.json
# - vulnerability_report.txt
# - security_report.txt
```

### **Resumen de Aprendizaje**

Al completar este taller, deberías haber aprendido:

1. **Reconocimiento de Red:**
   - Técnicas de escaneo de red
   - Identificación de dispositivos IoT
   - Análisis de servicios y puertos

2. **Ataques de Autenticación:**
   - Ataques de diccionario
   - Vulnerabilidades de contraseñas débiles
   - Automatización de ataques

3. **Análisis de Vulnerabilidades:**
   - Identificación de configuraciones inseguras
   - Explotación controlada
   - Evaluación de impacto

4. **Amenazas Avanzadas:**
   - Arquitecturas de botnets
   - Ataques coordinados
   - Comando y control

5. **Defensa:**
   - Herramientas de monitoreo
   - Evaluación de seguridad
   - Recomendaciones de hardening

---

## **RECOMENDACIONES PARA EL INSTRUCTOR**

### **Preparación Pre-Taller:**

1. **Verificar que todos los alumnos tienen:**
   - Windows 10 versión 2004+ o Windows 11
   - Al menos 4GB de RAM disponible
   - Acceso de administrador en sus laptops

2. **Preparar material:**
   - Scripts Python en USB o descarga compartida
   - Wordlist rockyou.txt (opcional, se puede descargar)
   - Guía de instalación de WSL impresa

3. **Configurar red:**
   - Router WiFi configurado
   - Dispositivos ESP32 pre-configurados
   - IPs de los ESP32 documentadas

### **Durante el Taller:**

1. **Tiempo de instalación:**
   - Reservar 30-45 minutos al inicio para instalación de WSL
   - Tener alumnos con WSL pre-instalado ayudar a otros
   - Tener scripts de instalación automatizados listos

2. **Soporte:**
   - Tener lista de problemas comunes a mano
   - Designar alumnos ayudantes para problemas técnicos
   - Preparar soluciones rápidas para problemas frecuentes

### **Script de Instalación Rápida:**

#### **Para WSL (PowerShell como Admin):**
```powershell
# Script de instalación automatizada
wsl --install
Write-Host "Reinicia tu computadora y luego ejecuta el siguiente comando en Ubuntu:"
Write-Host "sudo apt update && sudo apt install -y hydra nmap curl python3 python3-pip git wordlists && pip3 install --break-system-packages --ignore-installed blinker requests flask scapy"
```

**Nota:** Los flags `--break-system-packages` y `--ignore-installed` son necesarios en Ubuntu/Debian recientes debido a PEP 668.

---

## **NOTAS FINALES**

### **Ventajas de WSL:**
- ✅ Entorno idéntico a Linux
- ✅ Todas las herramientas funcionan sin modificaciones
- ✅ Mejor para aprendizaje de seguridad
- ✅ Fácil de usar una vez configurado
- ✅ Acceso directo a archivos de Windows
- ✅ Integración perfecta con Windows

### **Consideraciones Éticas:**
- Este taller debe realizarse solo en entornos controlados
- Todos los dispositivos deben ser de tu propiedad o tener autorización explícita
- No utilices estas técnicas en redes sin autorización

### **Recursos Adicionales:**
- Documentación oficial de ESP32
- OWASP IoT Security Top 10
- NIST Guidelines for IoT Security
- Foros de seguridad IoT

---

**¡Felicitaciones por completar el Taller Adicional de Seguridad IoT!**

*Esta guía te ha llevado paso a paso a través de todo el proceso usando WSL. Continúa practicando y aprendiendo sobre seguridad IoT.*
