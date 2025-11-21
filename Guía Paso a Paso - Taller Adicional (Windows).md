# **GUÍA PASO A PASO - TALLER ADICIONAL DE SEGURIDAD IoT (WINDOWS)**

## **ÍNDICE**
1. [Opciones de Instalación](#opciones-de-instalación)
2. [OPCIÓN 1: Usando WSL (Recomendado)](#opción-1-usando-wsl-recomendado)
3. [OPCIÓN 2: Windows Nativo](#opción-2-windows-nativo)
4. [Configuración Inicial](#configuración-inicial)
5. [Fase 1: Reconocimiento](#fase-1-reconocimiento)
6. [Fase 2: Ataque y Compromiso](#fase-2-ataque-y-compromiso)
7. [Fase 3: Análisis y Explotación](#fase-3-análisis-y-explotación)
8. [Fase 4: Demostración de Botnet](#fase-4-demostración-de-botnet)
9. [Fase 5: Panel Web de Control](#fase-5-panel-web-de-control)
10. [Fase 6: Herramientas Defensivas](#fase-6-herramientas-defensivas)
11. [Ejercicios Adicionales](#ejercicios-adicionales)
12. [Solución de Problemas Comunes](#solución-de-problemas-comunes)
13. [Verificación Final](#verificación-final)

---

## **OPCIONES DE INSTALACIÓN**

Tienes dos opciones para ejecutar el taller en Windows:

### **OPCIÓN 1: WSL (Windows Subsystem for Linux)** ⭐ RECOMENDADO
- ✅ Compatibilidad total con todas las herramientas
- ✅ Mismo entorno que Linux
- ✅ Fácil instalación
- ✅ Mejor rendimiento para herramientas de seguridad

### **OPCIÓN 2: Windows Nativo**
- ✅ No requiere instalación adicional
- ⚠️ Algunas herramientas requieren alternativas
- ⚠️ Configuración más compleja

**Recomendación:** Usa WSL para una experiencia más fluida y sin problemas.

---

## **OPCIÓN 1: USANDO WSL (RECOMENDADO)**

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

### **Paso 1.2: Instalar WSL**

En PowerShell como **Administrador**:

```powershell
# Instalar WSL con Ubuntu (versión más reciente)
wsl --install

# Si tienes una versión anterior de Windows, usa:
# dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
# dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
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

### **Paso 1.4: Instalar Herramientas en WSL**

```bash
# Instalar herramientas necesarias
sudo apt install -y hydra nmap curl python3 python3-pip git

# Verificar instalación
python3 --version
nmap --version
hydra -h | head -5
```

**Resultado esperado:** Todas las herramientas deberían mostrar sus versiones.

### **Paso 1.5: Instalar Wordlist rockyou.txt**

```bash
# Instalar wordlists de Kali (incluye rockyou.txt)
sudo apt install -y wordlists

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

**⚠️ IMPORTANTE:** En Ubuntu/Debian recientes, puede aparecer el error "externally-managed-environment". Tienes dos opciones:

#### **OPCIÓN A: Usar --break-system-packages (Rápido para talleres)** ⭐ RECOMENDADO PARA TALLERES

```bash
# Instalar dependencias Python con flag especial
# Si hay conflicto con blinker (instalado por el sistema), usar --ignore-installed
pip3 install --break-system-packages --ignore-installed blinker requests flask scapy

# Si el comando anterior falla, instalar por separado:
pip3 install --break-system-packages requests
pip3 install --break-system-packages --ignore-installed blinker flask
pip3 install --break-system-packages scapy

# Verificar instalación
python3 -c "import requests; import flask; import scapy; print('Todas las bibliotecas instaladas correctamente')"
```

**Nota:** Esta opción es segura para entornos de taller/educativos donde no afectará otros proyectos.

**Si aparece error con blinker:** El flag `--ignore-installed` evita el conflicto con paquetes instalados por el sistema.

#### **OPCIÓN B: Usar Entorno Virtual (Mejor práctica)**

```bash
# Instalar python3-venv si no está instalado
sudo apt install -y python3-venv

# Crear entorno virtual
python3 -m venv ~/iot_taller_env

# Activar entorno virtual
source ~/iot_taller_env/bin/activate

# Instalar dependencias en el entorno virtual
pip install requests flask scapy

# Verificar instalación
python -c "import requests; import flask; import scapy; print('Todas las bibliotecas instaladas correctamente')"
```

**⚠️ IMPORTANTE:** Si usas entorno virtual, debes activarlo cada vez que abras una nueva terminal:
```bash
source ~/iot_taller_env/bin/activate
```

Y usar `python` en lugar de `python3` cuando el entorno esté activado.

#### **OPCIÓN C: Instalar desde repositorios del sistema (si están disponibles)**

```bash
# Intentar instalar desde repositorios
sudo apt install -y python3-requests python3-flask python3-scapy

# Verificar qué se instaló
python3 -c "import requests; print('requests OK')" 2>/dev/null || echo "requests no disponible"
python3 -c "import flask; print('flask OK')" 2>/dev/null || echo "flask no disponible"
python3 -c "import scapy; print('scapy OK')" 2>/dev/null || echo "scapy no disponible"
```

**Recomendación para el taller:** Usa la **OPCIÓN A** (`--break-system-packages`) ya que es más rápida y no requiere activar entornos virtuales en cada terminal.

### **Paso 1.7: Acceder a Archivos de Windows desde WSL**

Los archivos de Windows están disponibles en WSL en `/mnt/c/`:

```bash
# Ver tus archivos de Windows
ls /mnt/c/Users/TuUsuario/

# Navegar al directorio del taller
cd /mnt/c/Users/TuUsuario/"Material para Taller"/Codigos\ Python

# O si está en otra ubicación (ejemplo: H:)
cd /mnt/h/"Material para Taller"/Codigos\ Python

# Verificar que todos los scripts están presentes
ls -la *.py
```

**Nota:** Reemplaza `TuUsuario` con tu nombre de usuario de Windows.

---

## **OPCIÓN 2: WINDOWS NATIVO**

### **Paso 2.1: Instalar Python**

1. Descarga Python desde: https://www.python.org/downloads/
2. Durante la instalación, **marca la casilla "Add Python to PATH"**
3. Verifica la instalación:

```cmd
python --version
pip --version
```

### **Paso 2.2: Instalar Nmap para Windows**

1. Descarga Nmap desde: https://nmap.org/download.html
2. Ejecuta el instalador
3. Durante la instalación, selecciona instalar **Npcap** (necesario para escaneos)
4. Verifica la instalación:

```cmd
nmap --version
```

### **Paso 2.3: Instalar Hydra para Windows**

1. Descarga Hydra desde: https://github.com/vanhauser-thc/thc-hydra/releases
2. Extrae el archivo ZIP en `C:\tools\hydra\` (o la ubicación que prefieras)
3. Agrega Hydra al PATH:
   - Abre "Variables de entorno" en Windows
   - Edita la variable PATH
   - Agrega: `C:\tools\hydra\` (o tu ruta)
4. Verifica la instalación:

```cmd
hydra -h
```

**Alternativa más fácil:** Usa WSL para hydra, ya que es más complejo en Windows.

### **Paso 2.4: Descargar Wordlist rockyou.txt**

```powershell
# Crear directorio para wordlists
New-Item -ItemType Directory -Force -Path "C:\tools\wordlists"

# Descargar rockyou.txt
Invoke-WebRequest -Uri "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt" -OutFile "C:\tools\wordlists\rockyou.txt"

# Verificar descarga
Get-Item "C:\tools\wordlists\rockyou.txt" | Select-Object Length
```

**Nota:** El archivo es grande (~133MB), la descarga puede tardar.

### **Paso 2.5: Instalar Bibliotecas Python**

Abre **CMD** o **PowerShell**:

```cmd
# Instalar dependencias Python
pip install requests flask

# Scapy puede ser problemático en Windows, instalar con cuidado
pip install scapy

# Si scapy falla, puedes omitirlo (no es crítico para estos scripts)
```

**Verificar instalación:**

```cmd
python -c "import requests; import flask; print('Bibliotecas instaladas correctamente')"
```

### **Paso 2.6: Modificar Scripts para Windows (si es necesario)**

Los scripts deberían funcionar en Windows, pero si tienes problemas con `scapy`, puedes comentar las importaciones relacionadas. La mayoría de los scripts funcionan sin scapy.

---

## **CONFIGURACIÓN INICIAL**

### **Paso 3.1: Navegar al Directorio del Proyecto**

#### **Si usas WSL:**
```bash
# Navegar al directorio (ajusta la ruta según tu ubicación)
cd /mnt/h/"Material para Taller"/Codigos\ Python

# O si está en C:
cd /mnt/c/Users/TuUsuario/"Material para Taller"/Codigos\ Python

# Verificar scripts
ls -la *.py
```

#### **Si usas Windows nativo:**
```cmd
# Navegar al directorio
cd "H:\Material para Taller\Codigos Python"

# Verificar scripts
dir *.py
```

### **Paso 3.2: Verificar Conectividad de Red**

#### **En WSL:**
```bash
# Obtener tu dirección IP
ip addr show | grep "inet " | grep -v 127.0.0.1

# O usar comando más simple
hostname -I

# Obtener la puerta de enlace
ip route | grep default
```

#### **En Windows:**
```cmd
# Obtener información de red
ipconfig

# O más detallado
ipconfig /all
```

**Anota los siguientes datos:**
- Tu IP: `_________________`
- Rango de red: `_________________` (ejemplo: 192.168.86.0)
- Gateway: `_________________`

### **Paso 3.3: Configurar Dispositivos ESP32**

1. **Abrir Arduino IDE en Windows** (funciona normalmente)
2. **Para ESP32 Simulador de Sala:**
   - Cargar: `Codigos IoT/ESP32_Simulador_de_Sala/ESP32_Simulador_de_Sala.ino`
   - Configurar credenciales WiFi:
     ```cpp
     const char* ssid = "TU_WIFI_SSID";
     const char* password = "TU_WIFI_PASSWORD";
     ```
   - Subir firmware al ESP32
   - Anotar IP asignada: `_________________`

3. **Para ESP32 Simulador de Entrada:**
   - Cargar: `Codigos IoT/ESP32_Simulador_de_Entrada/ESP32_Simulador_de_Entrada.ino`
   - Configurar las mismas credenciales WiFi
   - Subir firmware al ESP32
   - Anotar IP asignada: `_________________`

### **Paso 3.4: Verificar Conectividad con los ESP32**

#### **En WSL:**
```bash
# Probar conectividad
ping -c 4 192.168.86.114  # Reemplazar con IP real
ping -c 4 192.168.86.115

# Probar acceso HTTP
curl -I http://192.168.86.114/
curl -I http://192.168.86.115/
```

#### **En Windows:**
```cmd
# Probar conectividad
ping -n 4 192.168.86.114
ping -n 4 192.168.86.115

# Probar acceso HTTP (requiere curl, o usar navegador)
curl -I http://192.168.86.114/
curl -I http://192.168.86.115/
```

**Resultado esperado:** 
- Ping exitoso
- Respuesta HTTP 401 (Unauthorized) - esto es correcto

### **Paso 3.5: Verificar Credenciales por Defecto**

#### **En WSL o Windows:**
```bash
# Probar credenciales del ESP32 Sala (admin:123456)
curl -u admin:123456 http://192.168.86.114/

# Probar credenciales del ESP32 Entrada (user:12345)
curl -u user:12345 http://192.168.86.115/
```

**Resultado esperado:** Respuesta HTTP 200 (OK)

---

## **FASE 1: RECONOCIMIENTO**

### **Paso 4.1: Ejecutar Network Scanner**

#### **En WSL:**
```bash
# Asegúrate de estar en el directorio correcto
cd /mnt/h/"Material para Taller"/Codigos\ Python

# Ejecutar el scanner
python3 1-network_scanner.py
```

#### **En Windows:**
```cmd
cd "H:\Material para Taller\Codigos Python"
python 1-network_scanner.py
```

**¿Qué observar?**
- El script escaneará el rango de red automáticamente
- Verás progreso en tiempo real
- Identificará dispositivos activos y puertos abiertos

**Tiempo estimado:** 10-15 minutos

### **Paso 4.2: Verificar Resultados del Escaneo**

#### **En WSL:**
```bash
# Verificar archivo generado
ls -lh scan_results.log

# Ver contenido
head -20 scan_results.log
```

#### **En Windows:**
```cmd
dir scan_results.log
type scan_results.log | more
```

**Resultado esperado:** Archivo `scan_results.log` con información JSON

### **Paso 4.3: Analizar Resultados**

#### **En WSL:**
```bash
# Ver resultados formateados
cat scan_results.log | python3 -m json.tool | less
```

#### **En Windows:**
```cmd
# Ver resultados (puedes abrir en Notepad++)
python -m json.tool scan_results.log
```

---

## **FASE 2: ATAQUE Y COMPROMISO**

### **Paso 5.1: Ejecutar Dictionary Attack**

#### **En WSL:**
```bash
# Ejecutar el ataque de diccionario
python3 2-real_dictionary_attack.py
```

#### **En Windows:**
```cmd
python 2-real_dictionary_attack.py
```

**Nota importante para Windows:** Si el script busca `rockyou.txt` en `/usr/share/wordlists/`, necesitarás modificar el script para que apunte a `C:\tools\wordlists\rockyou.txt`.

**Modificación necesaria en Windows:**
Abre `2-real_dictionary_attack.py` y busca la línea que carga la wordlist, cámbiala a:
```python
wordlist_path = r"C:\tools\wordlists\rockyou.txt"
```

**Tiempo estimado:** 20-30 minutos

### **Paso 5.2: Verificar Credenciales Comprometidas**

#### **En WSL:**
```bash
# Verificar archivo generado
ls -lh compromised_devices.json

# Ver contenido
cat compromised_devices.json | python3 -m json.tool
```

#### **En Windows:**
```cmd
dir compromised_devices.json
python -m json.tool compromised_devices.json
```

**Resultado esperado:** Archivo JSON con credenciales comprometidas

### **Paso 5.3: Validar Credenciales Manualmente**

```bash
# Probar las credenciales encontradas
curl -u admin:123456 http://192.168.86.114/
curl -u user:12345 http://192.168.86.115/
```

---

## **FASE 3: ANÁLISIS Y EXPLOTACIÓN**

### **Paso 6.1: Ejecutar IoT Analyzer**

#### **En WSL:**
```bash
python3 3-iot_analyzer.py
```

#### **En Windows:**
```cmd
python 3-iot_analyzer.py
```

**Tiempo estimado:** 20-25 minutos

### **Paso 6.2: Revisar Reporte de Vulnerabilidades**

#### **En WSL:**
```bash
cat vulnerability_report.txt
```

#### **En Windows:**
```cmd
type vulnerability_report.txt
notepad vulnerability_report.txt
```

### **Paso 6.3: Probar Explotación Manual**

```bash
# Controlar dispositivos usando credenciales comprometidas
curl -u admin:123456 -X POST http://192.168.86.114/control/tv -d "state=on"
curl -u admin:123456 -X POST http://192.168.86.114/control/lights -d "state=on"
curl -u user:12345 -X POST http://192.168.86.115/control/door -d "state=open"
```

---

## **FASE 4: DEMOSTRACIÓN DE BOTNET**

### **Paso 7.1: Verificar Archivo Requerido**

#### **En WSL:**
```bash
ls -lh compromised_devices.json
cat compromised_devices.json
```

#### **En Windows:**
```cmd
dir compromised_devices.json
type compromised_devices.json
```

### **Paso 7.2: Ejecutar Botnet Demo**

#### **En WSL:**
```bash
python3 4-botnet_demo.py
```

#### **En Windows:**
```cmd
python 4-botnet_demo.py
```

**Tiempo estimado:** 15-20 minutos

### **Paso 7.3: Interactuar con la Botnet**

El script mostrará un menú interactivo. Prueba los comandos disponibles.

---

## **FASE 5: PANEL WEB DE CONTROL**

### **Paso 8.1: Verificar Dependencias**

#### **En WSL:**
```bash
python3 -c "import flask; print('Flask instalado')"
```

#### **En Windows:**
```cmd
python -c "import flask; print('Flask instalado')"
```

### **Paso 8.2: Ejecutar Panel Web**

#### **En WSL:**
```bash
python3 5-botnet_web_controller.py
```

#### **En Windows:**
```cmd
python 5-botnet_web_controller.py
```

**Nota importante:** En WSL, necesitarás acceder desde Windows usando `localhost` o la IP de WSL.

### **Paso 8.3: Acceder al Panel Web**

1. **Si usas WSL:**
   - El script mostrará una URL (ej: http://127.0.0.1:5000)
   - Abre tu navegador en Windows y ve a: `http://localhost:5000`

2. **Si usas Windows nativo:**
   - Abre: `http://localhost:5000`

### **Paso 8.4: Detener el Servidor**

Presiona `Ctrl+C` en la terminal para detener el servidor.

---

## **FASE 6: HERRAMIENTAS DEFENSIVAS**

### **Paso 9.1: Ejecutar Security Tool**

#### **En WSL:**
```bash
python3 6-security_tool.py
```

#### **En Windows:**
```cmd
python 6-security_tool.py
```

**Tiempo estimado:** 10-15 minutos

### **Paso 9.2: Revisar Reporte de Seguridad**

#### **En WSL:**
```bash
cat security_report.txt
```

#### **En Windows:**
```cmd
type security_report.txt
notepad security_report.txt
```

---

## **EJERCICIOS ADICIONALES**

### **Ejercicio 1: Análisis con Nmap**

#### **En WSL:**
```bash
nmap -sV -sC -O 192.168.86.114
nmap -sV -sC -O 192.168.86.115
```

#### **En Windows:**
```cmd
nmap -sV -sC -O 192.168.86.114
nmap -sV -sC -O 192.168.86.115
```

### **Ejercicio 2: Monitoreo de Tráfico**

#### **En WSL:**
```bash
# Instalar tcpdump
sudo apt install -y tcpdump

# Capturar tráfico
sudo tcpdump -i any -w iot_traffic.pcap host 192.168.86.114 or host 192.168.86.115
```

#### **En Windows:**
- Usa **Wireshark** (descarga desde wireshark.org)
- Captura tráfico desde la interfaz de red
- Filtra por las IPs de los ESP32

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

**Solución WSL:**
```bash
# WSL puede tener problemas con la red, verificar:
ip addr show

# Si no tienes IP, reiniciar WSL:
wsl --shutdown
# Luego abrir Ubuntu de nuevo
```

**Solución Windows:**
```cmd
# Verificar firewall de Windows
netsh advfirewall show allprofiles

# Permitir Python si es necesario
netsh advfirewall firewall add rule name="Python" dir=in action=allow program="C:\Python\python.exe"
```

### **Problema 3: "Error al importar módulos Python" o "externally-managed-environment"**

**Este es un error común en Ubuntu/Debian recientes (PEP 668).**

**Solución Rápida (Recomendada para talleres):**
```bash
# En WSL - usar flag --break-system-packages
pip3 install --break-system-packages --upgrade requests flask scapy

# Verificar instalación
python3 -c "import requests; import flask; import scapy; print('OK')"
```

### **Problema 3.1: "Cannot uninstall blinker" o "RECORD file not found"**

**Este error ocurre cuando hay conflicto entre paquetes del sistema y pip.**

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

**Solución con Entorno Virtual (Mejor práctica):**
```bash
# Crear y activar entorno virtual
python3 -m venv ~/iot_taller_env
source ~/iot_taller_env/bin/activate

# Instalar dependencias
pip install requests flask scapy

# Recordar activar el entorno cada vez: source ~/iot_taller_env/bin/activate
```

**Solución Windows:**
```cmd
pip install --upgrade requests flask
```

### **Problema 4: "rockyou.txt no encontrado"**

**Solución WSL:**
```bash
sudo apt install -y wordlists
```

**Solución Windows:**
```powershell
# Descargar manualmente
Invoke-WebRequest -Uri "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt" -OutFile "C:\tools\wordlists\rockyou.txt"
```

### **Problema 5: "Flask no accesible desde Windows cuando se ejecuta en WSL"**

**Solución:**
```bash
# En WSL, modificar el script para escuchar en 0.0.0.0:
# Cambiar: app.run(debug=True)
# A: app.run(host='0.0.0.0', port=5000, debug=True)

# O obtener la IP de WSL:
hostname -I

# Y acceder desde Windows usando esa IP
```

### **Problema 6: "Permisos denegados en escaneos"**

**Solución WSL:**
```bash
# Algunos escaneos requieren permisos de root
sudo python3 1-network_scanner.py
```

**Solución Windows:**
- Ejecutar CMD o PowerShell como Administrador

### **Problema 7: "Los ESP32 no responden desde WSL"**

**Solución:**
- Verificar que WSL puede acceder a la red de Windows
- Probar ping desde WSL
- Si no funciona, usar Windows nativo para esa parte

### **Problema 8: "Rutas de archivos no funcionan"**

**Solución:**
- En WSL, usa rutas de Windows: `/mnt/c/` o `/mnt/h/`
- En Windows, usa rutas normales: `C:\` o `H:\`
- Usa comillas para rutas con espacios

---

## **VERIFICACIÓN FINAL**

### **Checklist de Completación**

- [ ] WSL instalado y configurado (o Windows nativo configurado)
- [ ] Todas las herramientas instaladas
- [ ] Dispositivos ESP32 configurados y accesibles
- [ ] Script 1 ejecutado - Escaneo de red completado
- [ ] Script 2 ejecutado - Credenciales comprometidas
- [ ] Script 3 ejecutado - Análisis de vulnerabilidades
- [ ] Script 4 ejecutado - Demostración de botnet
- [ ] Script 5 ejecutado - Panel web funcionando
- [ ] Script 6 ejecutado - Herramientas defensivas
- [ ] Todos los archivos de reporte generados

### **Archivos Generados Esperados**

#### **En WSL:**
```bash
ls -lh *.log *.json *.txt
```

#### **En Windows:**
```cmd
dir *.log *.json *.txt
```

**Deberías ver:**
- `scan_results.log`
- `compromised_devices.json`
- `vulnerability_report.txt`
- `security_report.txt`

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
   - Reservar 30-45 minutos al inicio para instalación
   - Tener alumnos con WSL pre-instalado ayudar a otros
   - Tener scripts de instalación automatizados listos

2. **Alternativas:**
   - Si WSL no funciona para algún alumno, usar Windows nativo
   - Tener versiones modificadas de scripts para Windows listas

3. **Soporte:**
   - Tener lista de problemas comunes a mano
   - Designar alumnos ayudantes para problemas técnicos

### **Scripts de Instalación Rápida:**

#### **Para WSL (PowerShell como Admin):**
```powershell
# Script de instalación automatizada
wsl --install
Write-Host "Reinicia tu computadora y luego ejecuta el siguiente comando en Ubuntu:"
Write-Host "sudo apt update && sudo apt install -y hydra nmap curl python3 python3-pip git wordlists && pip3 install --break-system-packages requests flask scapy"
```

**Nota:** El flag `--break-system-packages` es necesario en Ubuntu/Debian recientes debido a PEP 668.

#### **Para Windows Nativo:**
Crear un script batch que:
- Verifique Python instalado
- Descargue e instale Nmap
- Descargue rockyou.txt
- Instale dependencias Python

---

## **NOTAS FINALES**

### **Ventajas de WSL:**
- ✅ Entorno idéntico a Linux
- ✅ Todas las herramientas funcionan sin modificaciones
- ✅ Mejor para aprendizaje de seguridad
- ✅ Fácil de usar una vez configurado

### **Ventajas de Windows Nativo:**
- ✅ No requiere instalación adicional
- ✅ Familiar para usuarios de Windows
- ⚠️ Requiere más configuración
- ⚠️ Algunas herramientas pueden no funcionar perfectamente

### **Recomendación Final:**
**Usa WSL siempre que sea posible.** Es la opción más confiable y compatible con todas las herramientas del taller.

---

**¡Felicitaciones por completar el Taller Adicional de Seguridad IoT en Windows!**

*Esta guía te ha llevado paso a paso a través de todo el proceso adaptado para Windows. Continúa practicando y aprendiendo sobre seguridad IoT.*

