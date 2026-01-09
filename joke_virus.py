import tkinter as tk
from tkinter import ttk
import time
import threading

# Создаем главное окно
root = tk.Tk()
root.title("Системное обновление Windows")
root.geometry("500x200")
# Делаем окно поверх всех остальных
root.attributes('-topmost', True)

# Переменные для блокировки закрытия
start_time = time.time()
block_duration = 120  # 2 минуты в секундах
is_blocked = True

# Блокируем закрытие окна
def disable_event():
    if is_blocked:
        # Показываем сообщение, что закрытие невозможно
        show_block_message()
        return "break"  # Блокируем событие закрытия

# Функция для показа сообщения о блокировке
def show_block_message():
    message = tk.Toplevel(root)
    message.title("Ошибка")
    message.geometry("300x100")
    message.attributes('-topmost', True)
    
    label = tk.Label(message, text="Закрытие невозможно во время установки обновлений!", 
                     font=("Arial", 10), wraplength=250)
    label.pack(pady=20)
    
    # Автоматически закрываем сообщение через 2 секунды
    message.after(2000, message.destroy)

# Функция для разблокировки закрытия через 2 минуты
def unblock_close():
    global is_blocked
    time.sleep(block_duration)  # Ждем 2 минуты
    is_blocked = False
    # Меняем сообщение на разрешающее закрытие
    status_label.config(text="Обновление завершено! Можно закрыть окно.")

# Запускаем поток для разблокировки
block_thread = threading.Thread(target=unblock_close)
block_thread.daemon = True
block_thread.start()

# Блокируем стандартные способы закрытия
root.protocol("WM_DELETE_WINDOW", disable_event)
# Убираем кнопку закрытия из заголовка
root.overrideredirect(True)  # Это уберет всю рамку окна

# Добавляем свою рамку с заголовком
title_bar = tk.Frame(root, bg='#2B2B2B', relief='raised', bd=0)
title_bar.pack(fill=tk.X)

# Заголовок окна
title_label = tk.Label(title_bar, text="Системное обновление Windows", 
                       bg='#2B2B2B', fg='white', font=("Arial", 10))
title_label.pack(side=tk.LEFT, padx=5)

# Создаем элементы основного содержимого
content_frame = tk.Frame(root)
content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

label = tk.Label(content_frame, text="Идет установка обновлений... Не выключайте компьютер.", 
                 font=("Arial", 12))
label.pack(pady=20)

# Создаем прогресс-бар
progress = ttk.Progressbar(content_frame, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=20)

# Текст под прогресс-баром
status_label = tk.Label(content_frame, text="Подготовка... 0%")
status_label.pack()

# Создаем полноэкранное окно для мерцания
blink_window = tk.Toplevel(root)
blink_window.attributes('-fullscreen', True)  # Полноэкранный режим
blink_window.attributes('-topmost', True)     # Поверх всех окон
blink_window.overrideredirect(True)           # Убираем рамку окна
blink_window.configure(bg='black')            # Черный фон
blink_window.attributes('-alpha', 0.0)        # Сначала невидимо
blink_window.withdraw()                       # Скрываем до использования
blink_window.protocol("WM_DELETE_WINDOW", disable_event)  # Блокируем закрытие

# Переменные для управления мерцанием
is_blinking = False
blink_start_time = 0

# Функция для мерцания всего экрана
def blink_fullscreen():
    global is_blinking, blink_start_time
    
    current_time = root.tk.call('clock', 'milliseconds')
    elapsed_time = current_time - blink_start_time
    
    if elapsed_time < 8000:  # 8 секунд мерцания
        # Получаем текущую прозрачность
        current_alpha = blink_window.attributes('-alpha')
        
        # Меняем прозрачность (мерцание между черным и прозрачным)
        new_alpha = 0.8 if current_alpha < 0.5 else 0.0
        blink_window.attributes('-alpha', new_alpha)
        
        # Планируем следующее мерцание
        root.after(150, blink_fullscreen)  # Быстрое мерцание
    else:
        # Завершаем мерцание
        blink_window.attributes('-alpha', 0.0)
        blink_window.withdraw()
        is_blinking = False
        status_label.config(text="Конфликты устранены! Продолжение установки...")

# Функция для запуска мерцания
def start_fullscreen_blink():
    global is_blinking, blink_start_time
    
    if not is_blinking:
        is_blinking = True
        blink_start_time = root.tk.call('clock', 'milliseconds')
        blink_window.deiconify()  # Показываем окно мерцания
        blink_window.attributes('-alpha', 0.0)
        blink_fullscreen()
        status_label.config(text="КРИТИЧЕСКАЯ ОШИБКА! Восстановление системы...")

# Функция для обновления прогресса
def update_progress(step):
    progress['value'] = step
    
    # Запускаем мерцание экрана на 45% прогрессе
    if step == 45:
        start_fullscreen_blink()
    
    # Временно приостанавливаем прогресс во время мерцания
    if step >= 45 and step < 55 and is_blinking:
        # Ждем завершения мерцания перед продолжением
        if not is_blinking:
            update_progress(step + 1)
        else:
            root.after(100, lambda: update_progress(step))
        return
    
    status_label.config(text=f"Выполняется обновление... {step}%")
    
    if step < 100:
        # Через 0.1 секунду увеличиваем прогресс на 1%
        root.after(100, update_progress, step + 1)
    else:
        # После завершения прогресса ждем еще немного, чтобы достичь 2 минут
        remaining_time = block_duration - (time.time() - start_time)
        if remaining_time > 0:
            status_label.config(text=f"Завершено! Окно закроется через {int(remaining_time)} секунд...")
            root.after(int(remaining_time * 1000), root.destroy)
        else:
            status_label.config(text="Обновление завершено! Можно закрыть окно.")

# Обеспечиваем корректное закрытие обоих окон
def on_closing():
    if not is_blocked:
        blink_window.destroy()
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
blink_window.protocol("WM_DELETE_WINDOW", on_closing)

# Запускаем процесс "обновления"
root.after(1000, update_progress, 0)  # Запуск через 1 секунду

root.mainloop()
