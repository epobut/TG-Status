import asyncio
import threading
from PIL import Image, ImageDraw
import pystray
from telethon import TelegramClient
from telethon.tl.types import User, InputNotifyPeer, PeerUser
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.types import InputPeerNotifySettings
from telethon.errors.rpcerrorlist import FloodWaitError

api_id = '' # Ваш api_id
api_hash = '' # Ваш api_hash

status = {'current': 'Онлайн', 'progress': 0, 'total': 1}

def create_image(color):
    '''Draws circle with progress bar overlay'''
    size = 64
    img = Image.new('RGB', (size, size), color)
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, 56, 56), fill='white')
    # Draw progress bar (bottom)
    if status['total'] > 1 and status['progress'] < status['total']:
        fill = int(40 * status['progress'] / status['total'])
        d.rectangle([12, 56 - fill, 52, 56], fill='green')
    return img

async def mute_unmute_all(mute=True, delay=2):
    async with TelegramClient('status_session', api_id, api_hash) as client:
        dialogs = [d for d in await client.get_dialogs() if isinstance(d.entity, User) and not d.entity.bot and not d.entity.is_self]
        status['total'] = len(dialogs)
        status['progress'] = 0
        for d in dialogs:
            entity = d.entity
            peer = InputNotifyPeer(PeerUser(entity.id))
            settings = InputPeerNotifySettings(mute_until=2**31 - 1 if mute else 0)
            try:
                await client(UpdateNotifySettingsRequest(peer=peer, settings=settings))
            except FloodWaitError as e:
                icon.title = f"Floodwait {e.seconds // 60}m..."
                await asyncio.sleep(e.seconds + 5)
            except Exception as ex:
                print(ex)
            status['progress'] += 1
            icon.icon = create_image("grey" if mute else "green")
            icon.title = f"{'Mute' if mute else 'Online'} {status['progress']}/{status['total']}"
            await asyncio.sleep(delay)
        status['current'] = "Mute" if mute else "Online"
        icon.icon = create_image("grey" if mute else "green")
        icon.title = f"Telegram {status['current']}"

def tray_mute(icon, item):
    threading.Thread(target=lambda: asyncio.run(mute_unmute_all(True))).start()

def tray_unmute(icon, item):
    threading.Thread(target=lambda: asyncio.run(mute_unmute_all(False))).start()

def quit_prog(icon, item):
    icon.stop()

icon = pystray.Icon(
    "TelegramMute",
    create_image("green"),
    title="Telegram Online",
    menu=pystray.Menu(
        pystray.MenuItem("Mute всех людей", tray_mute),
        pystray.MenuItem("Unmute всех людей", tray_unmute),
        pystray.MenuItem("Выход", quit_prog)
    )
)

# Запуск трей-иконки в основном потоке
icon.run()
