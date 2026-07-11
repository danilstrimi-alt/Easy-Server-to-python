# 💡 Примеры использования Easy Server

## 📖 Содержание

1. [Базовые примеры](#базовые-примеры)
2. [Примеры по типам серверов](#примеры-по-типам-серверов)
3. [Сценарии реального использования](#сценарии-реального-использования)
4. [Скрипты автоматизации](#скрипты-автоматизации)

---

## 🎯 Базовые примеры

### Пример 1: Первый запуск

```bash
$ python main.py

➤ help
# Выводит справку

➤ presets
# Показывает все доступные предустановки

➤ create my_first_server minecraft
✅ Сервер 'my_first_server' успешно создан

➤ list
📋 СПИСОК СЕРВЕРОВ
🔴 my_first_server
   Тип: minecraft
   Порт: 25565
   Статус: STOPPED
   Включен: ✅
   Макс. игроков: 20

➤ exit
```

### Пример 2: Запуск и остановка

```bash
$ python main.py

➤ start my_first_server
✅ Сервер 'my_first_server' запущен (PID: 12345)

➤ status my_first_server
{
  "name": "my_first_server",
  "type": "minecraft",
  "port": 25565,
  "max_players": 20,
  "status": "running",
  "enabled": true,
  "pid": 12345,
  "cpu_percent": 15.2,
  "memory_mb": 512.5
}

➤ stop my_first_server
✅ Сервер 'my_first_server' остановлен
```

### Пример 3: Редактирование конфигурации

```bash
$ python main.py

➤ create gaming_server minecraft 25565 50
✅ Сервер 'gaming_server' успешно создан

➤ edit gaming_server max_players 100
✅ Параметр 'max_players' изменен на '100'

➤ edit gaming_server port 25566
✅ Параметр 'port' изменен на '25566'

➤ edit gaming_server description "My awesome Minecraft server"
✅ Параметр 'description' изменен на 'My awesome Minecraft server'
```

### Пример 4: Использование из командной строки

```bash
# Создать
python main.py create server1 minecraft

# Запустить
python main.py start server1

# Показать статус
python main.py status server1

# Остановить
python main.py stop server1

# Перезагрузить
python main.py restart server1

# Удалить
python main.py delete server1
```

---

## 🎮 Примеры по типам серверов

### Minecraft

#### Создание простого сервера для друзей

```bash
$ python main.py

➤ create friends_mc minecraft 25565 10
✅ Сервер 'friends_mc' успешно создан

➤ start friends_mc
✅ Сервер 'friends_mc' запущен (PID: 1001)

# Друзья могут подключиться по адресу:
# localhost:25565 или 192.168.1.XXX:25565
```

#### Сервер для опубликования

```bash
➤ create public_mc minecraft 25565 50
✅ Сервер 'public_mc' успешно создан

➤ edit public_mc description "Public Minecraft Server - Join us!"
✅ Параметр 'description' изменен

➤ start public_mc
✅ Сервер 'public_mc' запущен
```

### CS:GO

#### Создание боевого сервера

```bash
➤ create csgo_competitive csgo 27015 32
✅ Сервер 'csgo_competitive' успешно создан

➤ start csgo_competitive
✅ Сервер 'csgo_competitive' запущен (PID: 2001)

➤ status csgo_competitive
{
  "name": "csgo_competitive",
  "type": "csgo",
  "port": 27015,
  "max_players": 32,
  "status": "running",
  "cpu_percent": 25.3,
  "memory_mb": 1024.8
}
```

### SCP: Secret Laboratory

#### Создание SCP сервера

```bash
➤ create scp_main scp-sl 7777 100
✅ Сервер 'scp_main' успешно создан

➤ edit scp_main description "SCP:SL Public Server - 100 slots"
✅ Параметр 'description' изменен

➤ start scp_main
✅ Сервер 'scp_main' запущен (PID: 3001)

➤ list
🟢 scp_main
   Тип: scp-sl
   Макс. игроков: 100
   Статус: RUNNING
   Память: 2048.5 MB
```

### Valheim

#### Создание локального сервера

```bash
➤ create valheim_survival valheim 2456 6
✅ Сервер 'valheim_survival' успешно создан

➤ start valheim_survival
✅ Сервер 'valheim_survival' запущен

# Максимум 6 игроков - идеально для приватной группы
```

### Rust

#### Высоконагруженный сервер

```bash
➤ create rust_main rust 28015 500
✅ Сервер 'rust_main' успешно создан

➤ edit rust_main max_players 500
✅ Параметр 'max_players' изменен

➤ start rust_main
✅ Сервер 'rust_main' запущен (PID: 4001)

# Отслеживайте ресурсы
➤ status rust_main
```

---

## 📊 Сценарии реального использования

### Сценарий 1: Организация ланпати

```bash
$ python main.py

# Создаём несколько серверов для разных игр
➤ create lanparty_mc minecraft 25565 20
✅ Сервер 'lanparty_mc' успешно создан

➤ create lanparty_cs csgo 27015 32
✅ Сервер 'lanparty_cs' успешно создан

➤ create lanparty_gmod gmod 27016 64
✅ Сервер 'lanparty_gmod' успешно создан

# Запускаем все одновременно
➤ start lanparty_mc
✅ Сервер 'lanparty_mc' запущен (PID: 5001)

➤ start lanparty_cs
✅ Сервер 'lanparty_cs' запущен (PID: 5002)

➤ start lanparty_gmod
✅ Сервер 'lanparty_gmod' запущен (PID: 5003)

# Проверяем все серверы
➤ list
📋 СПИСОК СЕРВЕРОВ

🟢 lanparty_mc
   Тип: minecraft
   Статус: RUNNING
   Макс. игроков: 20

🟢 lanparty_cs
   Тип: csgo
   Статус: RUNNING
   Макс. игроков: 32

🟢 lanparty_gmod
   Тип: gmod
   Статус: RUNNING
   Макс. игроков: 64

# После мероприятия - останавливаем все
➤ stop lanparty_mc
➤ stop lanparty_cs
➤ stop lanparty_gmod
```

### Сценарий 2: Развитие сервера

```bash
$ python main.py

# День 1: Создаём малый сервер
➤ create my_game minecraft 25565 10
✅ Сервер 'my_game' успешно создан

➤ start my_game
✅ Сервер 'my_game' запущен

# Сервер растёт, увеличиваем мощность
➤ stop my_game
✅ Сервер 'my_game' остановлен

➤ edit my_game max_players 50
✅ Параметр 'max_players' изменен на '50'

➤ edit my_game description "Popular Minecraft Server - 50 slots"
✅ Параметр 'description' изменен

➤ start my_game
✅ Сервер 'my_game' запущен

# Ещё больше игроков
➤ stop my_game

➤ edit my_game port 25566
➤ edit my_game max_players 100
➤ edit my_game description "Popular Minecraft Server - 100 slots"

➤ start my_game
```

### Сценарий 3: Тестирование и production

```bash
$ python main.py

# Создаём тестовый сервер
➤ create test_server minecraft 25565 5
✅ Сервер 'test_server' успешно создан

# Тестируем новые настройки
➤ start test_server
✅ Сервер 'test_server' запущен

# ... тестирование ...

➤ stop test_server

# Создаём production сервер с проверенными настройками
➤ create prod_server minecraft 25567 100
✅ Сервер 'prod_server' успешно создан

➤ edit prod_server description "Official Server"
✅ Параметр 'description' изменен

➤ start prod_server
✅ Сервер 'prod_server' запущен

# Удаляем тестовый
➤ delete test_server
```

### Сценарий 4: Мониторинг серверов

```bash
$ python main.py

# Создаём несколько серверов
➤ create server_1 minecraft 25565 20
➤ create server_2 csgo 27015 32
➤ create server_3 scp-sl 7777 100

# Запускаем все
➤ start server_1
➤ start server_2
➤ start server_3

# Периодически проверяем статус
➤ list
📋 СПИСОК СЕРВЕРОВ

🟢 server_1
   Статус: RUNNING
   CPU: 12.5%
   Память: 512.3 MB

🟢 server_2
   Статус: RUNNING
   CPU: 18.7%
   Память: 768.9 MB

🟢 server_3
   Статус: RUNNING
   CPU: 22.1%
   Память: 1024.5 MB

# Если сервер нужно перезагрузить
➤ restart server_2
```

---

## 🤖 Скрипты автоматизации

### Скрипт 1: Запуск всех серверов (Python)

Создайте файл `start_all.py`:

```python
#!/usr/bin/env python3
import subprocess
import time

servers = ['server_1', 'server_2', 'server_3']

print("🚀 Запуск всех серверов...")

for server in servers:
    print(f"⏱️ Запуск {server}...")
    subprocess.run(['python', 'main.py', 'start', server])
    time.sleep(2)

print("✅ Все серверы запущены!")
```

Использование:
```bash
python start_all.py
```

### Скрипт 2: Остановка всех серверов (Python)

Создайте файл `stop_all.py`:

```python
#!/usr/bin/env python3
import subprocess
import time

servers = ['server_1', 'server_2', 'server_3']

print("⛔ Остановка всех серверов...")

for server in servers:
    print(f"⏱️ Остановка {server}...")
    subprocess.run(['python', 'main.py', 'stop', server])
    time.sleep(1)

print("✅ Все серверы остановлены!")
```

### Скрипт 3: Мониторинг серверов (Python)

Создайте файл `monitor.py`:

```python
#!/usr/bin/env python3
import subprocess
import json
import time
from datetime import datetime

servers = ['server_1', 'server_2', 'server_3']

print("📊 Мониторинг серверов (Ctrl+C для выхода)")

while True:
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Статус серверов:")
    
    for server in servers:
        result = subprocess.run(
            ['python', 'main.py', 'status', server],
            capture_output=True,
            text=True
        )
        
        try:
            status = json.loads(result.stdout)
            state = "🟢 ONLINE" if status['status'] == 'running' else "🔴 OFFLINE"
            
            if status['status'] == 'running':
                print(f"{state} {server:15} | CPU: {status.get('cpu_percent', 'N/A'):.1f}% | "
                      f"RAM: {status.get('memory_mb', 'N/A'):.1f}MB")
            else:
                print(f"{state} {server:15}")
        except:
            print(f"❌ {server:15} | Error reading status")
    
    time.sleep(10)  # Обновлять каждые 10 секунд
```

### Скрипт 4: Batch запуск серверов (Windows)

Создайте файл `run_servers.bat`:

```batch
@echo off
echo 🚀 Запуск серверов...

python main.py start server_1
timeout /t 2
python main.py start server_2
timeout /t 2
python main.py start server_3

echo ✅ Все серверы запущены!
pause
```

### Скрипт 5: Batch остановка серверов (Windows)

Создайте файл `stop_servers.bat`:

```batch
@echo off
echo ⛔ Остановка серверов...

python main.py stop server_1
timeout /t 1
python main.py stop server_2
timeout /t 1
python main.py stop server_3

echo ✅ Все серверы остановлены!
pause
```

### Скрипт 6: Bash запуск (Linux/macOS)

Создайте файл `run_all_servers.sh`:

```bash
#!/bin/bash

servers=("server_1" "server_2" "server_3")

echo "🚀 Запуск всех серверов..."

for server in "${servers[@]}"; do
    echo "⏱️ Запуск $server..."
    python3 main.py start $server
    sleep 2
done

echo "✅ Все серверы запущены!"
```

Сделайте исполняемым:
```bash
chmod +x run_all_servers.sh
./run_all_servers.sh
```

---

## 📌 Советы и трюки

### Совет 1: Использование в разных портах

```bash
# Запустить один тип сервера на разных портах
python main.py create mc_1 minecraft 25565 20
python main.py create mc_2 minecraft 25566 20
python main.py create mc_3 minecraft 25567 20

python main.py start mc_1
python main.py start mc_2
python main.py start mc_3
```

### Совет 2: Быстрое редактирование

Отредактируйте JSON файл напрямую в папке `servers/`:

```json
{
    "name": "my_server",
    "type": "minecraft",
    "port": 25565,
    "max_players": 100,
    "description": "Custom Description",
    "enabled": true,
    "start_command": "java -Xmx2048M -Xms2048M -jar server.jar nogui"
}
```

### Совет 3: Получение адреса сервера

```bash
# Windows
ipconfig

# Linux/macOS
ifconfig
# или
hostname -I
```

Используйте внешний IP для доступа извне!

---

**Надеюсь эти примеры помогли вам! Удачи! 🎮**
