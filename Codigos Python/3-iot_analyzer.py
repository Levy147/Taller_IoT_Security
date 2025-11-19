#!/usr/bin/env python3
"""
IOT ANALYZER - Analizador de Vulnerabilidades IoT
Identifica, evalúa y explota vulnerabilidades comunes en dispositivos IoT
"""

import requests
import json
from datetime import datetime
from requests.auth import HTTPBasicAuth
import socket
import ipaddress
import concurrent.futures

def get_local_network():
    """Detecta automáticamente la red local"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        return str(network.network_address) + "/24"
    except:
        return "192.168.1.0/24"

def discover_iot_devices(network_range=None, ports=[80, 443, 8080]):
    """Descubre dispositivos IoT en la red automáticamente"""
    if network_range is None:
        network_range = get_local_network()
    
    print(f"[*] Descubriendo dispositivos IoT en {network_range}...")
    devices = []
    
    def check_device(ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((str(ip), port))
            sock.close()
            if result == 0:
                try:
                    url = f"http://{ip}:{port}/"
                    response = requests.get(url, timeout=2)
                    if response.status_code in [200, 401, 403]:
                        return True, port
                except:
                    pass
            return False, None
        except:
            return False, None
    
    network = ipaddress.ip_network(network_range, strict=False)
    hosts = list(network.hosts())
    
    # Escanear dispositivos
    for ip in hosts[:100]:  # Limitar a primeros 100 para velocidad
        for port in ports:
            found, found_port = check_device(ip, port)
            if found:
                devices.append({'ip': str(ip), 'port': found_port})
                print(f"  [+] Dispositivo encontrado: {ip}:{found_port}")
                break  # Solo un puerto por IP
    
    return devices

class IoTAnalyzer:
    def __init__(self):
        self.vulnerabilities = []
        self.devices_analyzed = []
        
    def check_connectivity(self, ip, port=80):
        """Verifica conectividad básica con el dispositivo"""
        try:
            url = f"http://{ip}:{port}/"
            response = requests.get(url, timeout=3)
            return True, response.status_code
        except:
            return False, None
    
    def test_default_credentials(self, ip, port=80):
        """Prueba credenciales por defecto comunes"""
        default_creds = [
            ('admin', 'admin'),
            ('admin', '123456'),
            ('admin', 'password'),
            ('admin', '12345'),
            ('user', 'user'),
            ('user', '12345'),
            ('user', '123456'),
            ('root', 'root'),
            ('root', '123456'),
            ('guest', 'guest'),
        ]
        
        print(f"[*] Probando credenciales por defecto en {ip}...")
        found_creds = []
        
        for username, password in default_creds:
            try:
                url = f"http://{ip}:{port}/"
                response = requests.get(
                    url,
                    auth=HTTPBasicAuth(username, password),
                    timeout=2
                )
                
                if response.status_code == 200:
                    print(f"[+] Credenciales válidas encontradas: {username}:{password}")
                    found_creds.append({
                        'username': username,
                        'password': password,
                        'status_code': response.status_code
                    })
            except:
                pass
        
        return found_creds
    
    def scan_endpoints(self, ip, port=80, credentials=None):
        """Escanea endpoints comunes en dispositivos IoT"""
        common_endpoints = [
            '/', '/index.html', '/admin', '/config', '/settings',
            '/api', '/control', '/status', '/info', '/system',
            '/firmware', '/update', '/reboot', '/reset',
            '/lights', '/tv', '/ac', '/door', '/alarm'
        ]
        
        print(f"[*] Escaneando endpoints en {ip}...")
        accessible_endpoints = []
        
        auth = None
        if credentials:
            auth = HTTPBasicAuth(credentials['username'], credentials['password'])
        
        for endpoint in common_endpoints:
            try:
                url = f"http://{ip}:{port}{endpoint}"
                response = requests.get(url, auth=auth, timeout=2)
                
                if response.status_code == 200:
                    accessible_endpoints.append({
                        'endpoint': endpoint,
                        'status_code': response.status_code,
                        'requires_auth': credentials is not None
                    })
                    print(f"  [+] {endpoint} - Accesible (Status: {response.status_code})")
            except:
                pass
        
        return accessible_endpoints
    
    def test_remote_control(self, ip, port=80, credentials=None):
        """Prueba controles remotos del dispositivo"""
        control_commands = {
            'lights': ['/lights/on', '/lights/off', '/lights/toggle'],
            'tv': ['/tv/on', '/tv/off', '/tv/channel/1'],
            'ac': ['/ac/on', '/ac/off', '/ac/temp/22'],
            'door': ['/door/open', '/door/close', '/door/lock'],
            'alarm': ['/alarm/on', '/alarm/off', '/alarm/disarm']
        }
        
        print(f"[*] Probando controles remotos en {ip}...")
        working_controls = []
        
        auth = None
        if credentials:
            auth = HTTPBasicAuth(credentials['username'], credentials['password'])
        
        for device_type, commands in control_commands.items():
            for command in commands:
                try:
                    url = f"http://{ip}:{port}{command}"
                    # Intentar POST primero, luego GET
                    for method in [requests.post, requests.get]:
                        try:
                            response = method(url, auth=auth, timeout=2)
                            if response.status_code in [200, 201, 202]:
                                working_controls.append({
                                    'device': device_type,
                                    'command': command,
                                    'method': method.__name__,
                                    'status_code': response.status_code
                                })
                                print(f"  [+] Control funcional: {device_type} - {command}")
                                break
                        except:
                            pass
                except:
                    pass
        
        return working_controls
    
    def check_info_leakage(self, ip, port=80, credentials=None):
        """Busca fugas de información en configuraciones"""
        info_endpoints = [
            '/config', '/settings', '/system', '/info',
            '/status', '/about', '/version', '/firmware'
        ]
        
        print(f"[*] Buscando fugas de información en {ip}...")
        leaked_info = []
        
        auth = None
        if credentials:
            auth = HTTPBasicAuth(credentials['username'], credentials['password'])
        
        for endpoint in info_endpoints:
            try:
                url = f"http://{ip}:{port}{endpoint}"
                response = requests.get(url, auth=auth, timeout=2)
                
                if response.status_code == 200:
                    content = response.text.lower()
                    # Buscar información sensible
                    sensitive_keywords = [
                        'password', 'passwd', 'secret', 'key',
                        'token', 'api', 'firmware', 'version',
                        'ssid', 'wifi', 'network', 'ip'
                    ]
                    
                    found_keywords = [kw for kw in sensitive_keywords if kw in content]
                    
                    if found_keywords:
                        leaked_info.append({
                            'endpoint': endpoint,
                            'keywords_found': found_keywords,
                            'content_length': len(response.text)
                        })
                        print(f"  [!] Posible fuga en {endpoint}: {', '.join(found_keywords)}")
            except:
                pass
        
        return leaked_info
    
    def analyze_device(self, ip, port=80):
        """Analiza un dispositivo IoT completo"""
        print(f"\n{'='*60}")
        print(f"    ANALIZANDO DISPOSITIVO: {ip}:{port}")
        print(f"{'='*60}")
        
        device_analysis = {
            'ip': ip,
            'port': port,
            'timestamp': datetime.now().isoformat(),
            'connectivity': False,
            'default_credentials': [],
            'accessible_endpoints': [],
            'remote_controls': [],
            'info_leakage': [],
            'vulnerabilities': []
        }
        
        # Verificar conectividad
        is_online, status = self.check_connectivity(ip, port)
        if not is_online:
            print(f"[-] Dispositivo {ip} no está accesible")
            return device_analysis
        
        device_analysis['connectivity'] = True
        print(f"[+] Dispositivo accesible (Status: {status})")
        
        # Probar credenciales por defecto
        default_creds = self.test_default_credentials(ip, port)
        device_analysis['default_credentials'] = default_creds
        
        credentials = None
        if default_creds:
            credentials = default_creds[0]
            device_analysis['vulnerabilities'].append({
                'type': 'Default Credentials',
                'severity': 'High',
                'description': f'Credenciales por defecto encontradas: {credentials["username"]}:{credentials["password"]}'
            })
        
        # Escanear endpoints
        endpoints = self.scan_endpoints(ip, port, credentials)
        device_analysis['accessible_endpoints'] = endpoints
        
        # Probar controles remotos
        controls = self.test_remote_control(ip, port, credentials)
        device_analysis['remote_controls'] = controls
        
        if controls:
            device_analysis['vulnerabilities'].append({
                'type': 'Remote Control Access',
                'severity': 'Critical',
                'description': f'Controles remotos accesibles: {len(controls)} funciones'
            })
        
        # Buscar fugas de información
        info_leaks = self.check_info_leakage(ip, port, credentials)
        device_analysis['info_leakage'] = info_leaks
        
        if info_leaks:
            device_analysis['vulnerabilities'].append({
                'type': 'Information Disclosure',
                'severity': 'Medium',
                'description': f'Fugas de información detectadas en {len(info_leaks)} endpoints'
            })
        
        # Verificar endpoints sin autenticación
        if not credentials:
            unauthenticated = [e for e in endpoints if not e.get('requires_auth', True)]
            if unauthenticated:
                device_analysis['vulnerabilities'].append({
                    'type': 'Unauthenticated Access',
                    'severity': 'High',
                    'description': f'Endpoints accesibles sin autenticación: {len(unauthenticated)}'
                })
        
        self.devices_analyzed.append(device_analysis)
        return device_analysis
    
    def generate_report(self, filename="vulnerability_report.txt"):
        """Genera un reporte de vulnerabilidades"""
        print(f"\n{'='*60}")
        print("    GENERANDO REPORTE DE VULNERABILIDADES")
        print(f"{'='*60}")
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("    REPORTE DE VULNERABILIDADES IoT")
        report_lines.append("=" * 60)
        report_lines.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Dispositivos analizados: {len(self.devices_analyzed)}\n")
        
        for device in self.devices_analyzed:
            report_lines.append(f"\n{'='*60}")
            report_lines.append(f"DISPOSITIVO: {device['ip']}:{device['port']}")
            report_lines.append(f"{'='*60}")
            
            if not device['connectivity']:
                report_lines.append("Estado: NO ACCESIBLE\n")
                continue
            
            report_lines.append("Estado: ACCESIBLE")
            
            # Credenciales por defecto
            if device['default_credentials']:
                report_lines.append("\n[!] CREDENCIALES POR DEFECTO ENCONTRADAS:")
                for cred in device['default_credentials']:
                    report_lines.append(f"  - {cred['username']}:{cred['password']}")
            
            # Endpoints accesibles
            if device['accessible_endpoints']:
                report_lines.append(f"\n[+] ENDPOINTS ACCESIBLES ({len(device['accessible_endpoints'])}):")
                for endpoint in device['accessible_endpoints']:
                    report_lines.append(f"  - {endpoint['endpoint']} (Status: {endpoint['status_code']})")
            
            # Controles remotos
            if device['remote_controls']:
                report_lines.append(f"\n[!] CONTROLES REMOTOS FUNCIONALES ({len(device['remote_controls'])}):")
                for control in device['remote_controls']:
                    report_lines.append(f"  - {control['device']}: {control['command']}")
            
            # Fugas de información
            if device['info_leakage']:
                report_lines.append(f"\n[!] FUGAS DE INFORMACIÓN DETECTADAS ({len(device['info_leakage'])}):")
                for leak in device['info_leakage']:
                    report_lines.append(f"  - {leak['endpoint']}: {', '.join(leak['keywords_found'])}")
            
            # Vulnerabilidades
            if device['vulnerabilities']:
                report_lines.append(f"\n[!] VULNERABILIDADES ENCONTRADAS ({len(device['vulnerabilities'])}):")
                for vuln in device['vulnerabilities']:
                    report_lines.append(f"  [{vuln['severity']}] {vuln['type']}: {vuln['description']}")
            else:
                report_lines.append("\n[+] No se encontraron vulnerabilidades críticas")
        
        # Guardar reporte
        report_content = "\n".join(report_lines)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(report_content)
        print(f"\n[*] Reporte guardado en: {filename}")
        
        return report_content

def main():
    print("=" * 60)
    print("    IOT ANALYZER - Analizador de Vulnerabilidades")
    print("=" * 60)
    
    analyzer = IoTAnalyzer()
    
    # Descubrir dispositivos automáticamente
    devices = discover_iot_devices()
    
    if not devices:
        print("[!] No se encontraron dispositivos IoT en la red.")
        print("[*] El análisis se completará sin dispositivos.")
    else:
        print(f"\n[*] {len(devices)} dispositivo(s) encontrado(s) para analizar")
        
        # Analizar cada dispositivo encontrado
        for device in devices:
            analyzer.analyze_device(device['ip'], device['port'])
    
    # Generar reporte
    analyzer.generate_report()
    
    # Resumen
    total_vulns = sum(len(d['vulnerabilities']) for d in analyzer.devices_analyzed)
    print(f"\n[*] Análisis completado:")
    print(f"    Dispositivos analizados: {len(analyzer.devices_analyzed)}")
    print(f"    Vulnerabilidades encontradas: {total_vulns}")

if __name__ == "__main__":
    main()

