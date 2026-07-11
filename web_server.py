#!/usr/bin/env python3
"""
Easy Server - Web Interface
Веб-интерфейс для управления локальными серверами
"""

import os
import sys
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from main import ServerManager

# Инициализация Flask приложения
app = Flask(__name__)
CORS(app)

# Глобальный экземпляр менеджера
manager = None

def init_manager():
    """Инициализировать менеджер серверов"""
    global manager
    try:
        manager = ServerManager()
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False

# API ENDPOINTS

@app.route('/api/health', methods=['GET'])
def health():
    """Проверка статуса приложения"""
    return jsonify({'status': 'ok', 'version': '1.0.0'})

@app.route('/api/servers', methods=['GET'])
def get_servers():
    """Получить список всех серверов"""
    try:
        servers_list = []
        for server_name in manager.servers:
            status = manager.get_server_status(server_name)
            servers_list.append(status)
        return jsonify({'success': True, 'servers': servers_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/servers/<server_name>/status', methods=['GET'])
def get_server_status(server_name):
    """Получить статус конкретного сервера"""
    try:
        status = manager.get_server_status(server_name)
        if status.get('status') == 'not_found':
            return jsonify({'success': False, 'error': 'Сервер не найден'}), 404
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/servers/create', methods=['POST'])
def create_server():
    """Создать новый сервер"""
    try:
        data = request.json
        name = data.get('name')
        preset = data.get('preset')
        port = data.get('port')
        max_players = data.get('max_players')
        
        if not name or not preset:
            return jsonify({'success': False, 'error': 'Не указано имя или тип'}), 400
        
        success = manager.create_server(name, preset, port, max_players)
        
        if success:
            return jsonify({'success': True, 'message': f'Сервер "{name}" создан'})
        else:
            return jsonify({'success': False, 'error': 'Ошибка при создании сервера'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/servers/<server_name>/start', methods=['POST'])
def start_server(server_name):
    """Запустить сервер"""
    try:
        success = manager.start_server(server_name)
        if success:
            return jsonify({'success': True, 'message': f'Сервер "{server_name}" запущен'})
        else:
            return jsonify({'success': False, 'error': 'Ошибка при запуске'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/servers/<server_name>/stop', methods=['POST'])
def stop_server(server_name):
    """Остановить сервер"""
    try:
        success = manager.stop_server(server_name)
        if success:
            return jsonify({'success': True, 'message': f'Сервер "{server_name}" остановлен'})
        else:
            return jsonify({'success': False, 'error': 'Ошибка при остановке'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/servers/<server_name>/delete', methods=['POST'])
def delete_server(server_name):
    """Удалить сервер"""
    try:
        success = manager.delete_server(server_name)
        if success:
            return jsonify({'success': True, 'message': f'Сервер "{server_name}" удален'})
        else:
            return jsonify({'success': False, 'error': 'Ошибка при удалении'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/presets', methods=['GET'])
def get_presets():
    """Получить список предустановок серверов"""
    try:
        presets_by_category = {}
        
        for key, preset in manager.SERVER_PRESETS.items():
            category = preset.get('category', 'Прочее')
            if category not in presets_by_category:
                presets_by_category[category] = []
            
            presets_by_category[category].append({
                'id': key,
                'name': key.upper(),
                'description': preset.get('description', ''),
                'port': preset.get('port', 0),
                'max_players': preset.get('max_players', 0)
            })
        
        return jsonify({'success': True, 'presets': presets_by_category})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# СТРАНИЦЫ

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/create')
def create():
    """Страница создания сервера"""
    return render_template('create.html')

@app.route('/servers')
def servers():
    """Страница со списком серверов"""
    return render_template('servers.html')

# ОБРАБОТКА ОШИБОК

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Страница не найдена'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Ошибка сервера'}), 500

if __name__ == '__main__':
    print("="*80)
    print("EASY SERVER - WEB INTERFACE".center(80))
    print("="*80)
    
    if not init_manager():
        print("\n❌ Не удалось инициализировать менеджер")
        sys.exit(1)
    
    print("\n✅ Менеджер инициализирован")
    print("\n🌐 Запуск веб-сервера...")
    print("📍 Откройте браузер: http://localhost:5000")
    print("\nНажмите Ctrl+C для выхода\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
