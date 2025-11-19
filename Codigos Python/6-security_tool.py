#!/usr/bin/env python3
"""
SECURITY TOOL - Herramienta Defensiva de Seguridad IoT
Monitorea y protege infraestructuras IoT mediante análisis continuo
"""

import socket
import ipaddress
import requests
import json
import time
from datetime import datetime
from requests.auth import HTTPBasicAuth
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

class SecurityTool:
    def __init__(self, network_range=None):
        if network_range is None:
            network_range = get_local_network()
        self.network_range = network_range
        self.device_inventory = []
        self.vulnerabilities_found = []
        self.recommendations = []
        self.baseline_established = False
        
    def scan_network(self):
        """Escanea la red para crear inventario de dispositivos"""
        print("[*] Escaneando red para crear inventario de dispositivos...")
        
        network = ipaddress.ip_network(self.network_range, strict=False)
        hosts = list(network.hosts())
        
        devices = []
        for ip in hosts:
            if self.check_device(ip):
                device_info = self.get_device_info(ip)
                if device_info:
                    devices.append(device_info)
                    print(f"  [+] Dispositivo encontrado: {ip} - {device_info.get('type', 'Unknown')}")
        
        self.device_inventory = devices
        print(f"[*] Inventario creado: {len(devices)} dispositivos encontrados")
        return devices
    
    def check_device(self, ip, timeout=1):
        """Verifica si un dispositivo está en línea"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((str(ip), 80))
            sock.close()
            return result == 0
        except:
            return False
    
    def get_device_info(self, ip):
        """Obtiene información básica de un dispositivo"""
        try:
            url = f"http://{ip}/"
            response = requests.get(url, timeout=2)
            
            return {
                'ip': str(ip),
                'status': 'online',
                'type': self.identify_device_type(response),
                'server': response.headers.get('Server', 'Unknown'),
                'last_seen': datetime.now().isoformat()
            }
        except:
            return None
    
    def identify_device_type(self, response):
        """Identifica el tipo de dispositivo"""
        server = response.headers.get('Server', '').lower()
        content = response.text.lower()
        
        if 'esp32' in server or 'esp32' in content:
            return 'ESP32 IoT Device'
        if 'arduino' in server or 'arduino' in content:
            return 'Arduino Device'
        if 'raspberry' in server:
            return 'Raspberry Pi'
        
        return 'Web Server'
    
    def check_default_credentials(self, ip):
        """Verifica si el dispositivo tiene credenciales por defecto"""
        default_creds = [
            ('admin', 'admin'),
            ('admin', '123456'),
            ('admin', 'password'),
            ('user', 'user'),
            ('user', '12345'),
            ('root', 'root'),
        ]
        
        for username, password in default_creds:
            try:
                url = f"http://{ip}/"
                response = requests.get(
                    url,
                    auth=HTTPBasicAuth(username, password),
                    timeout=2
                )
                if response.status_code == 200:
                    return True, username, password
            except:
                pass
        
        return False, None, None
    
    def analyze_vulnerabilities(self):
        """Analiza vulnerabilidades en los dispositivos encontrados"""
        print("\n[*] Analizando vulnerabilidades...")
        
        for device in self.device_inventory:
            ip = device['ip']
            vulns = []
            
            # Verificar credenciales por defecto
            has_default, user, pwd = self.check_default_credentials(ip)
            if has_default:
                vuln = {
                    'device': ip,
                    'type': 'Default Credentials',
                    'severity': 'High',
                    'description': f'Credenciales por defecto encontradas: {user}:{pwd}',
                    'recommendation': 'Cambiar inmediatamente las credenciales por defecto'
                }
                vulns.append(vuln)
                print(f"  [!] {ip}: Credenciales por defecto detectadas")
            
            # Verificar servicios expuestos
            try:
                url = f"http://{ip}/"
                response = requests.get(url, timeout=2)
                
                # Verificar si hay endpoints sin autenticación
                if response.status_code == 200 and not has_default:
                    vuln = {
                        'device': ip,
                        'type': 'Unauthenticated Access',
                        'severity': 'Medium',
                        'description': 'Servicio web accesible sin autenticación',
                        'recommendation': 'Implementar autenticación en todos los endpoints'
                    }
                    vulns.append(vuln)
                    print(f"  [!] {ip}: Acceso sin autenticación detectado")
            except:
                pass
            
            if vulns:
                self.vulnerabilities_found.extend(vulns)
        
        print(f"[*] Análisis completado: {len(self.vulnerabilities_found)} vulnerabilidades encontradas")
        return self.vulnerabilities_found
    
    def generate_recommendations(self):
        """Genera recomendaciones de seguridad basadas en los hallazgos"""
        print("\n[*] Generando recomendaciones de seguridad...")
        
        recommendations = []
        
        # Recomendaciones basadas en vulnerabilidades
        if any(v['type'] == 'Default Credentials' for v in self.vulnerabilities_found):
            recommendations.append({
                'priority': 'High',
                'category': 'Authentication',
                'recommendation': 'Cambiar todas las contraseñas por defecto',
                'action': 'Implementar política de contraseñas fuertes (mínimo 12 caracteres, mayúsculas, números, símbolos)'
            })
        
        if any(v['type'] == 'Unauthenticated Access' for v in self.vulnerabilities_found):
            recommendations.append({
                'priority': 'High',
                'category': 'Access Control',
                'recommendation': 'Implementar autenticación en todos los servicios',
                'action': 'Configurar autenticación HTTP básica o mejor aún, usar tokens JWT'
            })
        
        # Recomendaciones generales
        recommendations.extend([
            {
                'priority': 'Medium',
                'category': 'Network Security',
                'recommendation': 'Segmentar la red IoT',
                'action': 'Crear VLAN separada para dispositivos IoT con reglas de firewall estrictas'
            },
            {
                'priority': 'Medium',
                'category': 'Monitoring',
                'recommendation': 'Implementar monitoreo continuo',
                'action': 'Configurar sistema de monitoreo para detectar cambios y anomalías'
            },
            {
                'priority': 'Low',
                'category': 'Updates',
                'recommendation': 'Mantener firmware actualizado',
                'action': 'Establecer proceso de actualización regular de firmware'
            }
        ])
        
        self.recommendations = recommendations
        
        for rec in recommendations:
            print(f"  [{rec['priority']}] {rec['recommendation']}")
        
        return recommendations
    
    def monitor_network(self, duration=60, interval=10):
        """Monitorea la red continuamente buscando cambios"""
        print(f"\n[*] Iniciando monitoreo de red por {duration} segundos...")
        print(f"[*] Intervalo de escaneo: {interval} segundos\n")
        
        baseline = self.device_inventory.copy()
        start_time = time.time()
        scan_count = 0
        
        while time.time() - start_time < duration:
            scan_count += 1
            current_devices = []
            
            # Escanear red actual
            network = ipaddress.ip_network(self.network_range, strict=False)
            for ip in network.hosts():
                if self.check_device(ip):
                    device_info = self.get_device_info(ip)
                    if device_info:
                        current_devices.append(device_info)
            
            # Comparar con baseline
            baseline_ips = {d['ip'] for d in baseline}
            current_ips = {d['ip'] for d in current_devices}
            
            new_devices = current_ips - baseline_ips
            missing_devices = baseline_ips - current_ips
            
            if new_devices:
                print(f"[!] ALERTA: Nuevos dispositivos detectados: {', '.join(new_devices)}")
            
            if missing_devices:
                print(f"[!] ALERTA: Dispositivos desaparecidos: {', '.join(missing_devices)}")
            
            if not new_devices and not missing_devices:
                print(f"[*] Escaneo #{scan_count}: Sin cambios detectados")
            
            time.sleep(interval)
        
        print(f"\n[*] Monitoreo completado: {scan_count} escaneos realizados")
    
    def generate_security_report(self, filename="security_report.json"):
        """Genera un reporte completo de seguridad"""
        print(f"\n[*] Generando reporte de seguridad...")
        
        report = {
            'report_date': datetime.now().isoformat(),
            'network_range': self.network_range,
            'device_inventory': {
                'total_devices': len(self.device_inventory),
                'devices': self.device_inventory
            },
            'vulnerabilities': {
                'total': len(self.vulnerabilities_found),
                'by_severity': {
                    'High': len([v for v in self.vulnerabilities_found if v['severity'] == 'High']),
                    'Medium': len([v for v in self.vulnerabilities_found if v['severity'] == 'Medium']),
                    'Low': len([v for v in self.vulnerabilities_found if v['severity'] == 'Low'])
                },
                'details': self.vulnerabilities_found
            },
            'recommendations': self.recommendations,
            'security_score': self.calculate_security_score()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[*] Reporte guardado en: {filename}")
        return report
    
    def calculate_security_score(self):
        """Calcula un score de seguridad (0-100)"""
        if not self.device_inventory:
            return 0
        
        base_score = 100
        penalty_per_vuln = {
            'High': 20,
            'Medium': 10,
            'Low': 5
        }
        
        for vuln in self.vulnerabilities_found:
            base_score -= penalty_per_vuln.get(vuln['severity'], 0)
        
        return max(0, base_score)

def main():
    print("=" * 60)
    print("    SECURITY TOOL - Herramienta Defensiva IoT")
    print("=" * 60)
    
    # Detectar red automáticamente
    network = get_local_network()
    print(f"[*] Red detectada automáticamente: {network}")
    
    tool = SecurityTool(network_range=network)
    
    # Fase 1: Crear inventario
    print("\n[FASE 1] Creación de Inventario")
    tool.scan_network()
    
    # Fase 2: Análisis de vulnerabilidades
    print("\n[FASE 2] Análisis de Vulnerabilidades")
    tool.analyze_vulnerabilities()
    
    # Fase 3: Generar recomendaciones
    print("\n[FASE 3] Recomendaciones de Seguridad")
    tool.generate_recommendations()
    
    # Fase 4: Monitoreo (opcional, comentado por defecto)
    # print("\n[FASE 4] Monitoreo Continuo")
    # tool.monitor_network(duration=60)
    
    # Fase 5: Generar reporte
    print("\n[FASE 5] Generación de Reporte")
    report = tool.generate_security_report()
    
    # Resumen final
    print(f"\n{'='*60}")
    print("    RESUMEN DE SEGURIDAD")
    print(f"{'='*60}")
    print(f"Dispositivos en red: {len(tool.device_inventory)}")
    print(f"Vulnerabilidades encontradas: {len(tool.vulnerabilities_found)}")
    print(f"Recomendaciones generadas: {len(tool.recommendations)}")
    print(f"Score de seguridad: {report['security_score']}/100")
    
    if report['security_score'] < 50:
        print("\n[!] ADVERTENCIA: Score de seguridad bajo. Se recomienda acción inmediata.")
    elif report['security_score'] < 75:
        print("\n[!] Score de seguridad medio. Se recomiendan mejoras.")
    else:
        print("\n[+] Score de seguridad aceptable.")

if __name__ == "__main__":
    main()

