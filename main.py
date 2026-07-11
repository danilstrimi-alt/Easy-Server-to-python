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

# Проверка зависимостей
try:
    import psutil
except ImportError:
    print("⚠️ psutil не установлен. Установите: pip install psutil")
    input("Нажмите Enter для выхода...")
    sys.exit(1)


class ServerManager:
    """Менеджер для управления локальными серверами"""
    
    SERVER_PRESETS = {
        # 🎮 ИГРОВЫЕ СЕРВЕРЫ
        'minecraft': {
            'type': 'minecraft',
            'category': '🎮 ИГРОВЫЕ СЕРВЕРЫ',
            'port': 25565,
            'max_players': 20,
            'start_command': 'java -Xmx1024M -Xms1024M -jar server.jar nogui',
            'description': 'Minecraft Java Edition'
        },
        'minecraft-bedrock': {
            'type': 'minecraft-bedrock',
            'category': '🎮 ИГРОВЫЕ СЕРВЕРЫ',
            'port': 19132,
            'max_players': 20,
            'start_command': './bedrock_server',
            'description': 'Minecraft Bedrock Edition'
        },
        'csgo': {
            'type': 'csgo',
            'category': '🎮 ИГРОВЫЕ СЕРВЕРЫ',
            'port': 27015,
            'max_players': 32,
            'start_command': 'srcds -game csgo -console -usercon +map de_dust2',
            'description': 'Counter-Strike: Global Offensive'
        },
        'cs2': {
            'type': 'cs2',
            'category': '🎮 ИГРОВЫЕ СЕРВЕРЫ',
            'port': 27015,
            'max_players': 32,
            'start_command': 'srcds -game csgo -console +map de_dust2',
            'description': 'Counter-Strike 2'
        },
        'scp-sl': {
            'type': 'scp-sl',
            'category': '🎮 ИГРОВЫЕ СЕРВЕРЫ',
            'port': 7777,
            'max_players': 100,
            'start_command': 'python -m scp_server',
            'description': 'SCP: Secret Laboratory'
        },
        'rust': {
            'type': 'rust',
            'category': '🎮 ИГРОВЫЕ СЕРВЕРЫ',
            'port': 28015,
            'max_players': 500,
            'start_command': './RustDedicated',
            'description': 'Rust'
        },
        'valheim': {
            'type': 'valheim',
            'category': '🎮 ИГРОВЫЕ СЕРВЕРЫ',
            'port': 2456,
            'max_players': 10,
            'start_command': './valheim_server.x86_64',
            'description': 'Valheim'
        },
        'ark': {
            'type': 'ark',
            'category': '🎮 ИГРОВЫЕ СЕРВЕРЫ',
            'port': 27015,
            'max_players': 100,
            'start_command': 'ShooterGameServer TheIsland?listen',
            'description': 'ARK: Survival Evolved'
        },
        'palworld': {
            'type': 'palworld',
            'category': '🎮 ИГРОВЫЕ СЕРВЕРЫ',
            'port': 8211,
            'max_players': 32,
            'start_command': './PalServer.exe',
            'description': 'Palworld'
        },

        # 🌐 ВЕБ-СЕРВИСЫ
        'apache': {
            'type': 'apache',
            'category': '🌐 ВЕБ-СЕРВИСЫ',
            'port': 80,
            'max_players': 100,
            'start_command': 'sudo systemctl start apache2',
            'description': 'Apache Web Server'
        },
        'nginx': {
            'type': 'nginx',
            'category': '🌐 ВЕБ-СЕРВИСЫ',
            'port': 80,
            'max_players': 100,
            'start_command': 'sudo systemctl start nginx',
            'description': 'Nginx Web Server'
        },
        'nodejs': {
            'type': 'nodejs',
            'category': '🌐 ВЕБ-СЕРВИСЫ',
            'port': 3000,
            'max_players': 100,
            'start_command': 'node server.js',
            'description': 'Node.js Server'
        },
        'python-http': {
            'type': 'python-http',
            'category': '🌐 ВЕБ-СЕРВИСЫ',
            'port': 8000,
            'max_players': 100,
            'start_command': 'python -m http.server 8000',
            'description': 'Python HTTP Server'
        },

        # 🗄️ БАЗЫ ДАННЫХ
        'mysql': {
            'type': 'mysql',
            'category': '🗄️ БАЗЫ ДАННЫХ',
            'port': 3306,
            'max_players': 100,
            'start_command': 'sudo systemctl start mysql',
            'description': 'MySQL Database'
        },
        'postgresql': {
            'type': 'postgresql',
            'category': '🗄️ БАЗЫ ДАННЫХ',
            'port': 5432,
            'max_players': 100,
            'start_command': 'sudo systemctl start postgresql',
            'description': 'PostgreSQL Database'
        },
        'mongodb': {
            'type': 'mongodb',
            'category': '🗄️ БАЗЫ ДАННЫХ',
            'port': 27017,
            'max_players': 100,
            'start_command': 'mongod --dbpath /data/db',
            'description': 'MongoDB Database'
        },

        # 🎙️ ГОЛОС И МЕДИА
        'mumble': {
            'type': 'mumble',
            'category': '🎙️ ГОЛОС И МЕДИА',
            'port': 64738,
            'max_players': 100,
            'start_command': 'murmurd -fg',
            'description': 'Mumble Voice Server'
        },
        'teamspeak': {
            'type': 'teamspeak',
            'category': '🎙️ ГОЛОС И МЕДИА',
            'port': 9987,
            'max_players': 100,
            'start_command': './ts3server_linux_amd64 inifile=ts3server.ini',
            'description': 'TeamSpeak 3 Server'
        },
    }
    
    def __init__(self, config_dir: str = './servers'):
        try:
            self.config_dir = Path(config_dir)
            self.config_dir.mkdir(exist_ok=True)
            self.servers: Dict[str, Dict] = {}
            self.processes: Dict[str, subprocess.Popen] = {}
            self.load_configs()
            print("✅ Менеджер инициализирован успешно!")
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            input("Нажмите Enter для выхода...")
            sys.exit(1)
    
    def load_configs(self) -> None:
        """Загрузить конфигурации серверов из файлов"""
        try:
            for config_file in self.config_dir.glob('*.json'):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        server_name = config.get('name', config_file.stem)
                        self.servers[server_name] = config
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки {config_file}: {e}")
        except Exception as e:
            print(f"⚠️ Ошибка чтения папки конфигов: {e}")
    
    def save_config(self, server_name: str, config: Dict) -> bool:
        """Сохранить конфигурацию сервера"""
        try:
            config_path = self.config_dir / f"{server_name}.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.servers[server_name] = config
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            return False
    
    def create_server(self, name: str, preset: str, port: Optional[int] = None, 
                     max_players: Optional[int] = None) -> bool:
        """Создать новый сервер"""
        try:
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
                'category': preset_config.get('category', 'Прочее'),
                'port': preset_config['port'],
                'max_players': preset_config.get('max_players', 20),
                'description': preset_config.get('description', f'{preset} Server'),
                'start_command': preset_config.get('start_command'),
                'enabled': True
            }
            
            if self.save_config(name, config):
                print(f"✅ Сервер '{name}' успешно создан")
                return True
            return False
        except Exception as e:
            print(f"❌ Ошибка создания сервера: {e}")
            return False
    
    def start_server(self, server_name: str) -> bool:
        """Запустить сервер"""
        try:
            if server_name not in self.servers:
                print(f"❌ Сервер '{server_name}' не найден")
                return False
            
            if server_name in self.processes and self.processes[server_name].poll() is None:
                print(f"⚠️ Сервер '{server_name}' уже запущен")
                return False
            
            server_config = self.servers[server_name]
            start_cmd = server_config.get('start_command')
            
            if not start_cmd:
                print(f"❌ Команда запуска не задана")
                return False
            
            def run_server():
                try:
                    process = subprocess.Popen(
                        start_cmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        cwd=self.config_dir
                    )
                    self.processes[server_name] = process
                    print(f"✅ Сервер '{server_name}' запущен (PID: {process.pid})")
                except Exception as e:
                    print(f"❌ Ошибка запуска: {e}")
            
            thread = threading.Thread(target=run_server, daemon=True)
            thread.start()
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def stop_server(self, server_name: str) -> bool:
        """Остановить сервер"""
        try:
            if server_name not in self.processes:
                print(f"⚠️ Сервер не запущен")
                return False
            
            process = self.processes[server_name]
            
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
        except Exception as e:
            print(f"❌ Ошибка остановки: {e}")
            return False
    
    def get_server_status(self, server_name: str) -> Dict:
        """Получить статус сервера"""
        try:
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
        except Exception as e:
            print(f"❌ Ошибка получения статуса: {e}")
            return {'status': 'error'}
    
    def list_servers(self) -> None:
        """Показать список всех серверов"""
        try:
            print("\n" + "="*80)
            print("СПИСОК СЕРВЕРОВ".center(80))
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
                
                if 'pid' in status:
                    print(f"   CPU: {status.get('cpu_percent', 0):.1f}%")
                    print(f"   RAM: {status.get('memory_mb', 0):.1f}MB")
            
            print("\n" + "="*80)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def delete_server(self, server_name: str) -> bool:
        """Удалить сервер"""
        try:
            if server_name not in self.servers:
                print(f"❌ Сервер не найден")
                return False
            
            if server_name in self.processes:
                self.stop_server(server_name)
            
            config_path = self.config_dir / f"{server_name}.json"
            config_path.unlink()
            del self.servers[server_name]
            print(f"✅ Сервер удален")
            return True
        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
            return False
    
    def show_main_menu(self) -> None:
        """Главное меню"""
        while True:
            try:
                print("\n" + "="*80)
                print("EASY SERVER - МЕНЕДЖЕР ЛОКАЛЬНЫХ СЕРВЕРОВ".center(80))
                print("="*80 + "\n")
                
                # Активные серверы
                active = [name for name in self.servers 
                         if self.get_server_status(name)['status'] == 'running']
                if active:
                    print("АКТИВНЫЕ СЕРВЕРЫ:")
                    for s in active:
                        print(f"  🟢 {s}")
                    print()
                
                print("1. Создать новый сервер")
                print("2. Запустить сервер")
                print("3. Остановить сервер")
                print("4. Показать все серверы")
                print("5. Статус сервера")
                print("6. Удалить сервер")
                print("7. Доступные игры/сервисы")
                print("0. Выход")
                
                choice = input("\nВыберите опцию (0-7): ").strip()
                
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
                    self.show_services_menu()
                elif choice == '0':
                    print("\nСпасибо за использование!\n")
                    break
                else:
                    print("❌ Неверный выбор")
                
                input("Нажмите Enter для продолжения...")
            except Exception as e:
                print(f"❌ Ошибка в меню: {e}")
                input("Нажмите Enter для продолжения...")
    
    def show_services_menu(self) -> None:
        """Меню сервисов по категориям"""
        try:
            categories = {}
            for key, preset in self.SERVER_PRESETS.items():
                cat = preset.get('category', 'Прочее')
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append((key, preset))
            
            while True:
                print("\n" + "="*80)
                print("ДОСТУПНЫЕ СЕРВИСЫ".center(80))
                print("="*80 + "\n")
                
                sorted_cats = sorted(categories.keys())
                for i, cat in enumerate(sorted_cats, 1):
                    count = len(categories[cat])
                    print(f"{i}. {cat} ({count} сервисов)")
                
                print("0. Назад\n")
                
                choice = input("Выберите категорию: ").strip()
                
                if choice == '0':
                    break
                
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(sorted_cats):
                        cat = sorted_cats[idx]
                        self.show_services_in_category(cat, categories[cat])
                except:
                    print("❌ Ошибка выбора")
                
                input("Нажмите Enter...")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def show_services_in_category(self, category: str, services: list) -> None:
        """Показать сервисы в категории"""
        try:
            while True:
                print("\n" + "="*80)
                print(category.center(80))
                print("="*80 + "\n")
                
                for i, (key, preset) in enumerate(services, 1):
                    print(f"{i}. {key.upper()}")
                    print(f"   {preset['description']}")
                    print(f"   Порт: {preset['port']}\n")
                
                print("0. Назад\n")
                
                choice = input("Выберите сервис (или 0 для выхода): ").strip()
                
                if choice == '0':
                    break
                
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(services):
                        key, _ = services[idx]
                        self.quick_create_server(key)
                except:
                    print("❌ Ошибка выбора")
                
                input("Нажмите Enter...")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def quick_create_server(self, game_type: str) -> None:
        """Быстрое создание сервера"""
        try:
            preset = self.SERVER_PRESETS[game_type]
            
            print(f"\nСоздание {game_type.upper()}\n")
            
            # Генерируем имя
            counter = 1
            name = f"{game_type}_server"
            while name in self.servers:
                counter += 1
                name = f"{game_type}_server_{counter}"
            
            name_input = input(f"Имя сервера [{name}]: ").strip() or name
            
            if name_input in self.servers:
                print("❌ Такой сервер уже существует")
                return
            
            port_input = input(f"Порт [{preset['port']}]: ").strip()
            port = int(port_input) if port_input else None
            
            if self.create_server(name_input, game_type, port):
                launch = input("Запустить сейчас? (да/нет): ").lower()
                if launch in ['да', 'yes', 'y']:
                    self.start_server(name_input)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def menu_create_server(self) -> None:
        """Меню создания"""
        try:
            print("\n" + "="*80)
            print("СОЗДАНИЕ СЕРВЕРА".center(80))
            print("="*80 + "\n")
            
            games = sorted(self.SERVER_PRESETS.keys())
            for i, game in enumerate(games, 1):
                preset = self.SERVER_PRESETS[game]
                print(f"{i}. {game.upper()} - {preset['description']}")
            
            choice = input(f"\nВыберите (1-{len(games)}): ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(games):
                    self.quick_create_server(games[idx])
            except:
                print("❌ Ошибка")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def menu_start_server(self) -> None:
        """Меню запуска"""
        try:
            if not self.servers:
                print("❌ Нет серверов")
                return
            
            print("\n" + "="*80)
            print("ЗАПУСК СЕРВЕРА".center(80))
            print("="*80 + "\n")
            
            servers = sorted(self.servers.keys())
            for i, s in enumerate(servers, 1):
                status = self.get_server_status(s)
                st = "🟢" if status['status'] == 'running' else "🔴"
                print(f"{i}. {st} {s}")
            
            choice = input(f"\nВыберите (1-{len(servers)}): ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(servers):
                    self.start_server(servers[idx])
            except:
                print("❌ Ошибка")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def menu_stop_server(self) -> None:
        """Меню остановки"""
        try:
            running = [s for s in self.servers 
                      if self.get_server_status(s)['status'] == 'running']
            
            if not running:
                print("❌ Нет запущенных серверов")
                return
            
            print("\n" + "="*80)
            print("ОСТАНОВКА СЕРВЕРА".center(80))
            print("="*80 + "\n")
            
            for i, s in enumerate(running, 1):
                print(f"{i}. 🟢 {s}")
            
            choice = input(f"\nВыберите (1-{len(running)}): ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(running):
                    self.stop_server(running[idx])
            except:
                print("❌ Ошибка")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def menu_show_status(self) -> None:
        """Статус сервера"""
        try:
            if not self.servers:
                print("❌ Нет серверов")
                return
            
            print("\n" + "="*80)
            print("СТАТУС СЕРВЕРА".center(80))
            print("="*80 + "\n")
            
            servers = sorted(self.servers.keys())
            for i, s in enumerate(servers, 1):
                status = self.get_server_status(s)
                st = "🟢" if status['status'] == 'running' else "🔴"
                print(f"{i}. {st} {s}")
            
            choice = input(f"\nВыберите (1-{len(servers)}): ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(servers):
                    status = self.get_server_status(servers[idx])
                    print("\n" + "-"*80)
                    for k, v in status.items():
                        if isinstance(v, float):
                            print(f"{k}: {v:.1f}")
                        else:
                            print(f"{k}: {v}")
                    print("-"*80)
            except:
                print("❌ Ошибка")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def menu_delete_server(self) -> None:
        """Удаление сервера"""
        try:
            if not self.servers:
                print("❌ Нет серверов")
                return
            
            print("\n" + "="*80)
            print("УДАЛЕНИЕ СЕРВЕРА".center(80))
            print("="*80 + "\n")
            
            servers = sorted(self.servers.keys())
            for i, s in enumerate(servers, 1):
                print(f"{i}. {s}")
            
            choice = input(f"\nВыберите (1-{len(servers)}): ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(servers):
                    confirm = input("Вы уверены? (да/нет): ").lower()
                    if confirm in ['да', 'yes', 'y']:
                        self.delete_server(servers[idx])
                    else:
                        print("Отменено")
            except:
                print("❌ Ошибка")
        except Exception as e:
            print(f"❌ Ошибка: {e}")


def main():
    """Главная функция"""
    try:
        manager = ServerManager()
        manager.show_main_menu()
    except KeyboardInterrupt:
        print("\n\nПрограмма завершена пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")


if __name__ == '__main__':
    main()
