import asyncio
import tkinter as tk
from telethon.sync import TelegramClient
from telethon import types, functions

api_id = '1234567'  # Ваш API ID
api_hash = 'your_api_hash'  # Ваш API Hash

# Примерные emoji_id для премиум-статусов, их нужно узнать через Telegram Premium
status_emojis = {
    "dnd": -12398745604826,   # 🚫 Не беспокоить
    "busy": -42385432987456,  # 💼 Занят
    "away": -92387534987456,  # ☕ Отошёл
    "online": None            # В сети (дефолтный статус, сброс)
}

async def set_status(mode):
    async with TelegramClient('status_session', api_id, api_hash) as client:
        emoji_id = status_emojis.get(mode)
        if emoji_id is None:
            # В сети (дефолт)
            await client(functions.account.UpdateEmojiStatusRequest(
                emoji_status=types.EmojiStatusDefault()
            ))
            result = "Статус 'В сети' установлен."
            # Включить уведомления обратно
            dialogs = await client.get_dialogs()
            for dialog in dialogs:
                await client.edit_peer_notify_settings(dialog.entity, mute=False)
        else:
            await client(functions.account.UpdateEmojiStatusRequest(
                emoji_status=types.EmojiStatus(document_id=emoji_id)
            ))
            result = f"Статус установлен: {mode}"
            # Если DND, отключаем уведомления
            if mode == "dnd":
                dialogs = await client.get_dialogs()
                for dialog in dialogs:
                    await client.edit_peer_notify_settings(dialog.entity, mute=True)
        return result

def on_select(mode):
    result = asyncio.run(set_status(mode))
    status_label.config(text=result)

root = tk.Tk()
root.title('Telegram Status Setter')
root.geometry("300x180")

status_label = tk.Label(root, text="Выберите статус Telegram Premium:")
status_label.pack(pady=10)

buttons = [
    ('В сети', 'online'),
    ('Не беспокоить', 'dnd'),
    ('Занят', 'busy'),
    ('Отошёл', 'away')
]

for btn_text, btn_mode in buttons:
    tk.Button(root, text=btn_text, width=20, command=lambda m=btn_mode: on_select(m)).pack(pady=3)

root.mainloop()
