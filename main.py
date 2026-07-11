#!/usr/bin/env python3
"""
Easy Server - Universal Local Server Manager
Локальный менеджер серверов для игр и приложений
"""

import os
import sys
import subprocess
import json
import threading
import time
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

try:
    import psutil
except ImportError:
    print("⚠️ psutil не установлен. Установите: pip install psutil")
    sys.exit(1)


class ServerManager:
    """Менеджер для управления локальными серверами"""
    
    # Предустановки для популярных серверов
    SERVER_PRESETS = {
        'minecraft': {
            'type': 'minecraft',
            'port': 25565,
            'max_players': 20,
            'start_command': 'java -Xmx1024M -Xms1024M -jar server.jar nogui',
            'description': 'Minecraft Java Edition Server'
        },
        'csgo': {
            'type': 'csgo',
            'port': 27015,
            'max_players': 32,
            'start_command': 'srcds -game csgo -console -usercon +game_type 0 +game_mode 1 +mapgroup mg_allclassic +map de_dust2',
            'description': 'CS:GO Game Server'
        },
        'scp-sl': {
            'type': 'scp-sl',
            'port': 7777,
            'max_players': 100,
            'start_command': 'python -m scp_server',
            'description': 'SCP: Secret Laboratory Server'
        },
        'gmod': {
            'type': 'gmod',
            'port': 27015,
            'max_players': 64,
            'start_command': 'srcds -game garrysmod',
            'description': 'Garry\'s Mod Server'
        },
        'valheim': {
            'type': 'valheim',
            'port': 2456,
            'max_players': 10,
            'start_command': './valheim_server.x86_64',
            'description': 'Valheim Server'
        },
        'rust': {
            'type': 'rust',
            'port': 28015,
            'max_players': 500,
            'start_command': './RustDedicated',
            'description': 'Rust Game Server'
        },
        'ark': {
            'type': 'ark',
            'port': 27015,
            'max_players': 100,
            'start_command': 'ShooterGameServer TheIsland?listen',
            'description': 'ARK: Survival Evolved Server'
        },
        'terraria': {
            'type': 'terraria',
            'port': 7777,
            'max_players': 8,
            'start_command': './TerrariaServer.exe -config /path/to/config.txt',
            'description': 'Terraria Server'
        }
    }
    
    def __init__(self, config_dir: str = './servers'):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.servers: Dict[str, Dict] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.load_configs()
    
    def load_configs(self) -> None:
        """Загрузить конфигурации серверов из файлов"""
        for config_file in self.config_dir.glob('*.json'):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    server_name = config.get('name', config_file.stem)
                    self.servers[server_name] = config
            except Exception as e:
                print(f"❌ Ошибка при загрузке {config_file}: {e}")
    
    def save_config(self, server_name: str, config: Dict) -> bool:
        """Сохранить конфигурацию сервера"""
        try:
            config_path = self.config_dir / f"{server_name}.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.servers[server_name] = config
            return True
        except Exception as e:
            print(f"❌ Ошибка при сохранении конфигурации: {e}")
            return False
    
    def create_server(self, name: str, preset: str, port: Optional[int] = None, 
                     max_players: Optional[int] = None) -> bool:
        """Создать новый сервер из предустановки"""
        if name in self.servers:
            print(f"⚠️ Сервер '{name}' уже существует")
            return False
        
        if preset not in self.SERVER_PRESETS:
            print(f"❌ Неизвестная предустановка: {preset}")
            return False
        
        preset_config = self.SERVER_PRESETS[preset].copy()
        
        if port:
            preset_config['port'] = port
        if max_players:
            preset_config['max_players'] = max_players
        
        config = {
            'name': name,
            'type': preset,
            'port': preset_config['port'],
            'max_players': preset_config.get('max_players', 20),
            'description': preset_config.get('description', f'{preset} Server'),
            'start_command': preset_config.get('start_command'),
            'stop_command': preset_config.get('stop_command'),
            'enabled': True
        }
        
        if self.save_config(name, config):
            print(f"✅ Сервер '{name}' успешно создан")
            return True
        return False
    
    def start_server(self, server_name: str) -> bool:
        """Запустить сервер"""
        if server_name not in self.servers:
            print(f"❌ Сервер '{server_name}' не найден")
            return False
        
        if server_name in self.processes and self.processes[server_name].poll() is None:
            print(f"⚠️ Сервер '{server_name}' уже запущен")
            return False
        
        server_config = self.servers[server_name]
        start_cmd = server_config.get('start_command')
        
        if not start_cmd:
            print(f"❌ Команда запуска не задана для сервера '{server_name}'")
            return False
        
        try:
            def run_server():
                try:
                    process = subprocess.Popen(
                        start_cmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=self.config_dir
                    )
                    self.processes[server_name] = process
                    print(f"✅ Сервер '{server_name}' запущен (PID: {process.pid})")
                    
                    while True:
                        output = process.stdout.readline()
                        if not output and process.poll() is not None:
                            break
                        if output:
                            print(f"[{server_name}] {output.rstrip()}")
                    
                except Exception as e:
                    print(f"❌ Ошибка при запуске сервера '{server_name}': {e}")
            
            thread = threading.Thread(target=run_server, daemon=True)
            thread.start()
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при запуске сервера: {e}")
            return False
    
    def stop_server(self, server_name: str) -> bool:
        """Остановить сервер"""
        if server_name not in self.processes:
            print(f"⚠️ Сервер '{server_name}' не запущен")
            return False
        
        process = self.processes[server_name]
        
        try:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                
                del self.processes[server_name]
                print(f"✅ Сервер '{server_name}' остановлен")
                return True
            else:
                del self.processes[server_name]
                return True
                
        except Exception as e:
            print(f"❌ Ошибка при остановке сервера: {e}")
            return False
    
    def get_server_status(self, server_name: str) -> Dict:
        """Получить статус сервера"""
        if server_name not in self.servers:
            return {'status': 'not_found'}
        
        server_config = self.servers[server_name]
        is_running = (server_name in self.processes and 
                     self.processes[server_name].poll() is None)
        
        status = {
            'name': server_name,
            'type': server_config.get('type'),
            'port': server_config.get('port'),
            'max_players': server_config.get('max_players'),
            'status': 'running' if is_running else 'stopped',
            'enabled': server_config.get('enabled', True)
        }
        
        if is_running:
            try:
                process = self.processes[server_name]
                pid = process.pid
                p = psutil.Process(pid)
                status['pid'] = pid
                status['cpu_percent'] = p.cpu_percent(interval=0.1)
                status['memory_mb'] = p.memory_info().rss / 1024 / 1024
            except:
                pass
        
        return status
    
    def list_servers(self) -> None:
        """Показать список всех серверов"""
        print("\n" + "="*80)
        print("📋 СПИСОК СЕРВЕРОВ".center(80))
        print("="*80)
        
        if not self.servers:
            print("❌ Нет созданных серверов\n")
            return
        
        for i, server_name in enumerate(self.servers, 1):
            status = self.get_server_status(server_name)
            
            status_emoji = "🟢" if status['status'] == 'running' else "🔴"
            
            print(f"\n{i}. {status_emoji} {server_name}")
            print(f"   Тип: {status['type']}")
            print(f"   Порт: {status['port']}")
            print(f"   Статус: {status['status'].upper()}")
            print(f"   Макс. игроков: {status['max_players']}")
            
            if 'pid' in status:
                print(f"   PID: {status['pid']}")
                print(f"   CPU: {status['cpu_percent']:.1f}%")
                print(f"   Память: {status['memory_mb']:.1f} MB")
        
        print("\n" + "="*80 + "\n")
    
    def delete_server(self, server_name: str) -> bool:
        """Удалить сервер"""
        if server_name not in self.servers:
            print(f"❌ Сервер '{server_name}' не найден")
            return False
        
        if server_name in self.processes:
            self.stop_server(server_name)
        
        config_path = self.config_dir / f"{server_name}.json"
        try:
            config_path.unlink()
            del self.servers[server_name]
            print(f"✅ Сервер '{server_name}' удален")
            return True
        except Exception as e:
            print(f"❌ Ошибка при удалении сервера: {e}")
            return False
    
    def show_main_menu(self) -> None:
        """Показать главное меню"""
        while True:
            print("\n" + "╔" + "═"*78 + "╗")
            print("║" + "🎮 EASY SERVER - Менеджер локальных серверов 🎮".center(78) + "║")
            print("╚" + "═"*78 + "╝\n")
            
            # Показываем статус активных серверов
            active_servers = []
            for name, config in self.servers.items():
                status = self.get_server_status(name)
                if status['status'] == 'running':
                    active_servers.append(f"🟢 {name}")
            
            if active_servers:
                print("📌 АКТИВНЫЕ СЕРВЕРЫ:")
                for server in active_servers:
                    print(f"   {server}")
                print()
            
            print("┌─ ВЫБЕРИТЕ ДЕЙСТВИЕ ─────────────────────────────────────────────────────┐")
            print("│                                                                         │")
            print("│  1️⃣  Создать новый сервер                                               │")
            print("│  2️⃣  Запустить существующий сервер                                      │")
            print("│  3️⃣  Остановить сервер                                                  │")
            print("│  4️⃣  Показать все серверы                                               │")
            print("│  5️⃣  Показать статус сервера                                            │")
            print("│  6️⃣  Удалить сервер                                                     │")
            print("│  7️⃣  Показать доступные игры                                            │")
            print("│  0️⃣  Выход                                                              │")
            print("│                                                                         │")
            print("└─────────────────────────────────────────────────────────────────────────┘")
            
            choice = input("\n➤ Выберите опцию (0-7): ").strip()
            
            if choice == '1':
                self.menu_create_server()
            elif choice == '2':
                self.menu_start_server()
            elif choice == '3':
                self.menu_stop_server()
            elif choice == '4':
                self.list_servers()
            elif choice == '5':
                self.menu_show_status()
            elif choice == '6':
                self.menu_delete_server()
            elif choice == '7':
                self.show_games_menu()
            elif choice == '0':
                print("\n👋 Спасибо за использование Easy Server!\n")
                sys.exit(0)
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
                input("Нажмите Enter для продолжения...")
    
    def show_games_menu(self) -> None:
        """Показать меню выбора игр"""
        games = list(self.SERVER_PRESETS.keys())
        
        while True:
            print("\n" + "="*80)
            print("🎮 ДОСТУПНЫЕ ИГРЫ".center(80))
            print("="*80 + "\n")
            
            for i, game in enumerate(games, 1):
                preset = self.SERVER_PRESETS[game]
                print(f"{i}. 📌 {game.upper()}")
                print(f"   Описание: {preset['description']}")
                print(f"   Порт: {preset['port']} | Макс. игроков: {preset['max_players']}\n")
            
            print("0. ◀️ Назад в главное меню\n")
            
            choice = input("➤ Выберите игру (0 для выхода): ").strip()
            
            if choice == '0':
                break
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(games):
                    game = games[idx]
                    self.quick_start_server(game)
                else:
                    print("❌ Неверный выбор")
            except ValueError:
                print("❌ Введите число")
            
            input("Нажмите Enter для продолжения...")
    
    def quick_start_server(self, game_type: str) -> None:
        """Быстрый запуск сервера выбранной игры"""
        preset = self.SERVER_PRESETS[game_type]
        
        print(f"\n🎮 Быстрый запуск {game_type.upper()}\n")
        
        # Проверяем существующие серверы этого типа
        existing = [name for name, cfg in self.servers.items() if cfg.get('type') == game_type]
        
        if existing:
            print(f"Найдены существующие серверы типа {game_type}:")
            for i, server in enumerate(existing, 1):
                status = self.get_server_status(server)
                state = "🟢 ЗАПУЩЕН" if status['status'] == 'running' else "🔴 ОСТАНОВЛЕН"
                print(f"{i}. {server} [{state}]")
            
            print(f"{len(existing)+1}. Создать новый сервер")
            print("0. Вернуться назад\n")
            
            choice = input("➤ Выберите действие: ").strip()
            
            if choice == '0':
                return
            elif choice == str(len(existing)+1):
                self.create_new_quick_server(game_type)
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(existing):
                        server = existing[idx]
                        status = self.get_server_status(server)
                        if status['status'] == 'running':
                            print(f"✅ Сервер '{server}' уже запущен!")
                        else:
                            confirm = input(f"Запустить сервер '{server}'? (да/нет): ").lower()
                            if confirm in ['да', 'yes', 'y']:
                                self.start_server(server)
                except ValueError:
                    print("❌ Неверный ввод")
        else:
            print(f"Серверов типа {game_type} не найдено\n")
            confirm = input(f"Создать новый сервер {game_type}? (да/нет): ").lower()
            if confirm in ['да', 'yes', 'y']:
                self.create_new_quick_server(game_type)
    
    def create_new_quick_server(self, game_type: str) -> None:
        """Создать новый сервер быстро"""
        preset = self.SERVER_PRESETS[game_type]
        
        print(f"\n📝 Создание сервера {game_type.upper()}\n")
        
        # Генерируем имя по умолчанию
        counter = 1
        default_name = f"{game_type}_server"
        while default_name in self.servers:
            counter += 1
            default_name = f"{game_type}_server_{counter}"
        
        name = input(f"Введите имя сервера [{default_name}]: ").strip() or default_name
        
        if name in self.servers:
            print(f"❌ Сервер с именем '{name}' уже существует")
            return
        
        port = input(f"Введите порт [{preset['port']}]: ").strip()
        if port:
            try:
                port = int(port)
            except ValueError:
                print(f"❌ Неверный порт, используется {preset['port']}")
                port = None
        else:
            port = None
        
        max_players = input(f"Введите макс. игроков [{preset['max_players']}]: ").strip()
        if max_players:
            try:
                max_players = int(max_players)
            except ValueError:
                print(f"❌ Неверное число, используется {preset['max_players']}")
                max_players = None
        else:
            max_players = None
        
        if self.create_server(name, game_type, port, max_players):
            launch = input(f"\n✅ Сервер создан! Запустить его сейчас? (да/нет): ").lower()
            if launch in ['да', 'yes', 'y']:
                self.start_server(name)
    
    def menu_create_server(self) -> None:
        """Меню создания сервера"""
        print("\n" + "="*80)
        print("➕ СОЗДАНИЕ НОВОГО СЕРВЕРА".center(80))
        print("="*80 + "\n")
        
        print("Доступные игры:")
        games = list(self.SERVER_PRESETS.keys())
        for i, game in enumerate(games, 1):
            print(f"{i}. {game.upper()}")
        
        choice = input("\n➤ Выберите игру (1-{}): ".format(len(games))).strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(games):
                game = games[idx]
                self.create_new_quick_server(game)
            else:
                print("❌ Неверный выбор")
        except ValueError:
            print("❌ Введите число")
        
        input("Нажмите Enter для продолжения...")
    
    def menu_start_server(self) -> None:
        """Меню запуска сервера"""
        if not self.servers:
            print("\n❌ Нет созданных серверов\n")
            input("Нажмите Enter для продолжения...")
            return
        
        print("\n" + "="*80)
        print("▶️ ЗАПУСК СЕРВЕРА".center(80))
        print("="*80 + "\n")
        
        servers = list(self.servers.keys())
        for i, server in enumerate(servers, 1):
            status = self.get_server_status(server)
            state = "🟢" if status['status'] == 'running' else "🔴"
            print(f"{i}. {state} {server}")
        
        choice = input("\n➤ Выберите сервер (1-{}): ".format(len(servers))).strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(servers):
                server = servers[idx]
                self.start_server(server)
            else:
                print("❌ Неверный выбор")
        except ValueError:
            print("❌ Введите число")
        
        input("Нажмите Enter для продолжения...")
    
    def menu_stop_server(self) -> None:
        """Меню остановки сервера"""
        running = []
        for name, config in self.servers.items():
            status = self.get_server_status(name)
            if status['status'] == 'running':
                running.append(name)
        
        if not running:
            print("\n❌ Нет запущенных серверов\n")
            input("Нажмите Enter для продолжения...")
            return
        
        print("\n" + "="*80)
        print("⏹️ ОСТАНОВКА СЕРВЕРА".center(80))
        print("="*80 + "\n")
        
        for i, server in enumerate(running, 1):
            print(f"{i}. 🟢 {server}")
        
        choice = input("\n➤ Выберите сервер (1-{}): ".format(len(running))).strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(running):
                server = running[idx]
                self.stop_server(server)
            else:
                print("❌ Неверный выбор")
        except ValueError:
            print("❌ Введите число")
        
        input("Нажмите Enter для продолжения...")
    
    def menu_show_status(self) -> None:
        """Меню показа статуса"""
        if not self.servers:
            print("\n❌ Нет созданных серверов\n")
            input("Нажмите Enter для продолжения...")
            return
        
        print("\n" + "="*80)
        print("📊 СТАТУС СЕРВЕРА".center(80))
        print("="*80 + "\n")
        
        servers = list(self.servers.keys())
        for i, server in enumerate(servers, 1):
            status = self.get_server_status(server)
            state = "🟢" if status['status'] == 'running' else "🔴"
            print(f"{i}. {state} {server}")
        
        choice = input("\n➤ Выберите сервер (1-{}): ".format(len(servers))).strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(servers):
                server = servers[idx]
                status = self.get_server_status(server)
                
                print("\n" + "-"*80)
                print(f"Сервер: {status['name']}")
                print(f"Тип: {status['type']}")
                print(f"Порт: {status['port']}")
                print(f"Статус: {status['status'].upper()}")
                print(f"Макс. игроков: {status['max_players']}")
                
                if 'pid' in status:
                    print(f"PID: {status['pid']}")
                    print(f"CPU: {status['cpu_percent']:.1f}%")
                    print(f"Память: {status['memory_mb']:.1f} MB")
                
                print("-"*80)
            else:
                print("❌ Неверный выбор")
        except ValueError:
            print("❌ Введите число")
        
        input("Нажмите Enter для продолжения...")
    
    def menu_delete_server(self) -> None:
        """Меню удаления сервера"""
        if not self.servers:
            print("\n❌ Нет созданных серверов\n")
            input("Нажмите Enter для продолжения...")
            return
        
        print("\n" + "="*80)
        print("🗑️ УДАЛЕНИЕ СЕРВЕРА".center(80))
        print("="*80 + "\n")
        
        servers = list(self.servers.keys())
        for i, server in enumerate(servers, 1):
            print(f"{i}. {server}")
        
        choice = input("\n➤ Выберите сервер (1-{}): ".format(len(servers))).strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(servers):
                server = servers[idx]
                confirm = input(f"\n⚠️ Вы уверены? Это действие необратимо (да/нет): ").lower()
                if confirm in ['да', 'yes', 'y']:
                    self.delete_server(server)
                else:
                    print("❌ Отменено")
            else:
                print("❌ Неверный выбор")
        except ValueError:
            print("❌ Введите число")
        
        input("Нажмите Enter для продолжения...")


def main():
    """Главная функция"""
    manager = ServerManager()
    manager.show_main_menu()


if __name__ == '__main__':
    main()
