#!/usr/bin/env python3
"""
NETWORK SCANNER - Escáner de Red para Dispositivos IoT
Descubre y analiza dispositivos IoT en la red local
"""

import socket
import ipaddress
import requests
import concurrent.futures
from datetime import datetime
import json
import subprocess
import platform

def get_local_network():
    """Detecta automáticamente la red local"""
    try:
        # Conectar a un servidor externo para obtener la IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Obtener la máscara de red
        if platform.system() == "Windows":
            # Windows: usar ipconfig
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if local_ip in line:
                    # Buscar la máscara de subred
                    continue
            # Por defecto, asumir /24
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        else:
            # Linux/Mac: usar ip o ifconfig
            try:
                result = subprocess.run(['ip', 'route', 'get', '8.8.8.8'], 
                                      capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'src' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == 'src':
                                local_ip = parts[i+1]
                                break
            except:
                pass
            
            # Intentar obtener máscara de red
            try:
                result = subprocess.run(['ip', 'addr', 'show'], 
                                      capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if local_ip in line and '/' in line:
                        # Extraer CIDR
                        cidr = line.split('/')[1].split()[0]
                        network = ipaddress.IPv4Network(f"{local_ip}/{cidr}", strict=False)
                        return str(network)
            except:
                pass
            
            # Por defecto, asumir /24
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        
        return str(network.network_address) + "/24"
    except Exception as e:
        print(f"[!] Error detectando red local: {e}")
        print("[*] Usando red por defecto: 192.168.1.0/24")
        return "192.168.1.0/24"

class NetworkScanner:
    def __init__(self, network_range=None, ports=[80, 443, 8080]):
        if network_range is None:
            network_range = get_local_network()
        self.network_range = network_range
        self.ports = ports
        self.discovered_devices = []
        
    def scan_port(self, ip, port, timeout=1):
        """Escanea un puerto específico en una IP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((str(ip), port))
            sock.close()
            return result == 0
        except:
            return False
    
    def get_http_info(self, ip, port=80):
        """Obtiene información HTTP del dispositivo"""
        try:
            url = f"http://{ip}:{port}"
            response = requests.get(url, timeout=2, allow_redirects=True)
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'server': response.headers.get('Server', 'Unknown'),
                'title': self.extract_title(response.text)
            }
        except:
            return None
    
    def extract_title(self, html):
        """Extrae el título de una página HTML"""
        try:
            import re
            match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            return match.group(1) if match else "Sin título"
        except:
            return "Sin título"
    
    def identify_device_type(self, ip, http_info):
        """Identifica el tipo de dispositivo basado en la respuesta HTTP"""
        if not http_info:
            return "Desconocido"
        
        server = http_info.get('server', '').lower()
        title = http_info.get('title', '').lower()
        
        # Identificación de ESP32
        if 'esp32' in server or 'esp32' in title:
            return "ESP32 IoT Device"
        if 'arduino' in server or 'arduino' in title:
            return "Arduino Device"
        if 'raspberry' in server or 'raspberry' in title:
            return "Raspberry Pi"
        if http_info.get('status_code') == 200:
            return "Web Server"
        
        return "IoT Device"
    
    def scan_host(self, ip):
        """Escanea un host completo"""
        device_info = {
            'ip': str(ip),
            'ports': [],
            'services': {},
            'device_type': 'Unknown',
            'timestamp': datetime.now().isoformat()
        }
        
        # Escanear puertos
        for port in self.ports:
            if self.scan_port(ip, port):
                device_info['ports'].append(port)
                
                # Obtener información HTTP si es puerto web
                if port in [80, 443, 8080]:
                    http_info = self.get_http_info(ip, port)
                    if http_info:
                        device_info['services'][port] = http_info
                        device_info['device_type'] = self.identify_device_type(ip, http_info)
        
        # Solo retornar si tiene puertos abiertos
        if device_info['ports']:
            return device_info
        return None
    
    def scan_network(self, max_workers=50):
        """Escanea toda la red en paralelo"""
        print(f"[*] Iniciando escaneo de red: {self.network_range}")
        print(f"[*] Escaneando puertos: {self.ports}")
        print(f"[*] Usando {max_workers} hilos paralelos\n")
        
        network = ipaddress.ip_network(self.network_range, strict=False)
        hosts = list(network.hosts())
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ip = {executor.submit(self.scan_host, ip): ip for ip in hosts}
            
            for future in concurrent.futures.as_completed(future_to_ip):
                try:
                    result = future.result()
                    if result:
                        self.discovered_devices.append(result)
                        self.print_device_info(result)
                except Exception as e:
                    pass
        
        return self.discovered_devices
    
    def print_device_info(self, device):
        """Imprime información del dispositivo encontrado"""
        print(f"\n[+] Dispositivo encontrado: {device['ip']}")
        print(f"    Tipo: {device['device_type']}")
        print(f"    Puertos abiertos: {', '.join(map(str, device['ports']))}")
        
        for port, service in device['services'].items():
            print(f"    Puerto {port}:")
            print(f"      Status: {service.get('status_code', 'N/A')}")
            print(f"      Server: {service.get('server', 'N/A')}")
            print(f"      Título: {service.get('title', 'N/A')}")
    
    def find_iot_targets(self):
        """Identifica objetivos IoT específicos (todos los dispositivos IoT encontrados)"""
        targets = []
        for device in self.discovered_devices:
            # Considerar cualquier dispositivo IoT encontrado como objetivo
            if device['device_type'] != 'Unknown' and device['device_type'] != 'Web Server':
                targets.append(device)
        return targets
    
    def generate_report(self, filename="scan_results.log"):
        """Genera un reporte de los dispositivos encontrados"""
        report = {
            'scan_date': datetime.now().isoformat(),
            'network_range': self.network_range,
            'total_devices': len(self.discovered_devices),
            'devices': self.discovered_devices,
            'iot_targets': self.find_iot_targets()
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[*] Reporte guardado en: {filename}")
        return report

def main():
    print("=" * 60)
    print("    NETWORK SCANNER - Escáner de Dispositivos IoT")
    print("=" * 60)
    
    # Detectar red automáticamente
    network = get_local_network()
    print(f"[*] Red detectada automáticamente: {network}")
    
    scanner = NetworkScanner(network_range=network, ports=[80, 443, 8080])
    devices = scanner.scan_network()
    
    print(f"\n[*] Escaneo completado: {len(devices)} dispositivos encontrados")
    
    # Buscar objetivos IoT
    targets = scanner.find_iot_targets()
    if targets:
        print(f"\n[!] Dispositivos IoT identificados:")
        for target in targets:
            print(f"    - {target['ip']} ({target['device_type']})")
    else:
        print(f"\n[*] Todos los dispositivos encontrados son objetivos potenciales")
    
    # Generar reporte
    scanner.generate_report()
    
    return devices

if __name__ == "__main__":
    main()

