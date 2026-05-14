import asyncio
from telethon import TelegramClient, events, Button
import os, re, subprocess

# ================= НАСТРОЙКИ =================
MAIN_TOKEN = "8962532742:AAG1377yowFSqklfaPP_AzEXvIvV-Fm_jqw"
BASE_DIRS = ["/storage/emulated/0/Download/докс", "/storage/emulated/0/Download/апп"]
# =============================================

client = TelegramClient('dox_main', api_id=6, api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e")

# Список зеркал
mirrors = {}

def find_bases():
    bases = []
    for d in BASE_DIRS:
        if not os.path.exists(d):
            continue
        for f in os.listdir(d):
            if f.endswith(('.csv','.txt')):
                bases.append(os.path.join(d, f))
    return bases

BASES = find_bases()

def search_query(query):
    results = []
    for path in BASES:
        try:
            r = subprocess.run(['grep','-i','-m','3',query,path],
                capture_output=True, text=True, timeout=5)
            for line in r.stdout.strip().split('\n'):
                if line.strip():
                    results.append(line[:1000])
        except: pass
    return results[:15]

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Hello")

@client.on(events.NewMessage(pattern='/clone'))
async def clone_bot(event):
    """Создание зеркала бота"""
    args = event.text.split(' ', 1)
    if len(args) < 2:
        await event.reply("Использование: `/clone ТОКЕН_БОТА`")
        return
    
    new_token = args[1].strip()
    msg = await event.reply("Создаю зеркало...")
    
    try:
        # Запускаем клона
        clone = TelegramClient(f'clone_{len(mirrors)}', 6, "eb06d4abfb49dc3eeb1aeb98ae0f581e")
        await clone.start(bot_token=new_token)
        
        # Копируем обработчики
        @clone.on(events.NewMessage(pattern='/start'))
        async def clone_start(e):
            await e.reply("Hello")
        
        @clone.on(events.NewMessage(incoming=True))
        async def clone_search(e):
            if e.out or e.text.startswith('/'):
                return
            q = e.text.strip()
            if not q:
                return
            res = search_query(q)
            if res:
                text = '\n──\n'.join(res[:5])
                await e.reply(text[:4000])
            else:
                await e.reply("❌")
        
        mirrors[new_token] = clone
        await msg.edit(f"Зеркало создано!")
    
    except Exception as e:
        await msg.edit(f"Ошибка: {e}")

@client.on(events.NewMessage(incoming=True))
async def search_handler(event):
    if event.out or event.text.startswith('/'):
        return
    
    query = event.text.strip()
    if not query or len(query) < 3:
        return
    
    results = search_query(query)
    
    if not results:
        await event.reply("❌")
        return
    
    text = '\n──\n'.join(results[:5])
    await event.reply(text[:4000])

async def main():
    await client.start(bot_token=MAIN_TOKEN)
    print("✅ Бот запущен!")
    print("Команды:")
    print("  /start - Hello")
    print("  /clone ТОКЕН - создать зеркало")
    print("  Любой текст - поиск по базам")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
