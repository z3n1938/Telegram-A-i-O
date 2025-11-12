#!/usr/bin/env python3
import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from colorama import init, Fore, Style
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
import requests

init(autoreset=True)

# ==================== BANNER ====================
BANNER = f"""
{Fore.MAGENTA}╔{"═"*50}╗
{Fore.MAGENTA}║  {Fore.CYAN}z3n1938 presents: Telegram-A-i-O v1.0{Fore.MAGENTA}  ║
{Fore.MAGENTA}╚{"═"*50}╝{Style.RESET_ALL}
"""

# ==================== CONFIG ====================
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    api_id = int(config['api_id'])
    api_hash = config['api_hash']
    phone = config['phone']
    webhook_url = config.get('webhook_url')
except Exception as e:
    print(f"{Fore.RED}config.json hatası: {e}")
    sys.exit(1)

client = TelegramClient('session', api_id, api_hash)

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def send_webhook(content: str):
    if webhook_url:
        try:
            requests.post(webhook_url, json={"content": f"Telegram-A-i-O: {content}"})
            print(f"{Fore.GREEN}Webhook gönderildi!")
        except Exception as e:
            print(f"{Fore.RED}Webhook hatası: {e}")

# ==================== MENÜ ====================
def menu():
    clear()
    print(BANNER)
    options = [
        "Mesaj Çek (Kanal/Grup)",
        "Medya İndir (Son Mesajlardan)",
        "Üye Listesi Çıkar",
        "Ban/Kick Kullanıcı",
        "Chat Profil Info"
    ]
    for i, opt in enumerate(options, 1):
        print(f"{Fore.GREEN}[{i}] {opt}")
    print(f"{Fore.YELLOW}[0] Çıkış")
    return input(f"\n{Fore.WHITE}Seçim > {Fore.CYAN}").strip()

# ==================== YARDIMCI ====================
async def get_chat(prompt: str = "Chat ID/Username: "):
    chat_input = input(prompt).strip()
    try:
        return await client.get_entity(chat_input)
    except Exception as e:
        print(f"{Fore.RED}Chat bulunamadı: {e}")
        return None

# ==================== İŞLEMLER ====================
async def option1():
    chat = await get_chat("Kanal/Grup ID gir: ")
    if not chat: return
    try:
        limit = int(input("Mesaj sayısı (örn: 50): "))
    except:
        print(f"{Fore.RED}Geçersiz sayı!")
        return
    messages = []
    async for msg in client.iter_messages(chat, limit=limit):
        messages.append({
            'id': msg.id,
            'date': msg.date.isoformat(),
            'text': (msg.text or '')[:100] + ('...' if msg.text and len(msg.text) > 100 else ''),
            'sender': msg.sender_id
        })
    with open('messages.json', 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    send_webhook(f"{len(messages)} mesaj çekildi: {getattr(chat, 'title', 'Bilinmiyor')}")
    print(f"{Fore.GREEN}{len(messages)} mesaj 'messages.json'a kaydedildi!")

async def option2():
    chat = await get_chat("Chat ID gir: ")
    if not chat: return
    try:
        limit = int(input("İndirilecek medya sayısı: "))
    except:
        return
    os.makedirs('downloads', exist_ok=True)
    count = 0
    async for msg in client.iter_messages(chat, limit=limit):
        if msg.media:
            await msg.download_media(file='downloads/')
            count += 1
    send_webhook(f"{count} medya indirildi: {getattr(chat, 'title', 'Bilinmiyor')}")
    print(f"{Fore.GREEN}{count} medya 'downloads/'a kaydedildi!")

async def option3():
    chat = await get_chat("Grup ID gir: ")
    if not chat: return
    members = []
    # DOĞRU: await YOK → TotalList döner, async for çalışır
    async for user in client.get_participants(chat):
        members.append({
            'id': user.id,
            'username': user.username or '',
            'first_name': user.first_name or ''
        })
    with open('members.csv', 'w', encoding='utf-8') as f:
        f.write('ID,Username,Name\n')
        for m in members:
            f.write(f"{m['id']},{m['username']},{m['first_name']}\n")
    send_webhook(f"{len(members)} üye listelendi: {getattr(chat, 'title', 'Bilinmiyor')}")
    print(f"{Fore.GREEN}{len(members)} üye 'members.csv'e kaydedildi!")

async def option4():
    chat = await get_chat("Chat ID gir: ")
    if not chat: return
    user_input = input("Banlanacak kullanıcı ID/Username: ").strip()
    try:
        user = await client.get_entity(user_input)
    except Exception as e:
        print(f"{Fore.RED}Kullanıcı bulunamadı: {e}")
        return
    duration = input("Süre (gün, 0=kalıcı): ").strip()
    days = int(duration) if duration.isdigit() else 0
    until_date = datetime.now() + timedelta(days=days) if days > 0 else None

    rights = ChatBannedRights(
        until_date=until_date,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
        send_polls=True,
        change_info=True,
        invite_users=True,
        pin_messages=True,
        manage_topics=True
    )
    try:
        await client(EditBannedRequest(chat, user, rights))
        send_webhook(f"{user.first_name} banlandı: {getattr(chat, 'title', 'Bilinmiyor')}")
        print(f"{Fore.GREEN}{user.first_name} banlandı!")
    except FloodWaitError as e:
        print(f"{Fore.YELLOW}Flood wait: {e.seconds} saniye bekle.")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        print(f"{Fore.RED}Ban hatası: {e} (Admin misin?)")

async def option5():
    chat = await get_chat("Chat ID gir: ")
    if not chat: return
    title = getattr(chat, 'title', 'Bilinmiyor')
    members = getattr(chat, 'participants_count', 'Bilinmiyor')
    print(f"{Fore.CYAN}Chat: {title}\nÜye Sayısı: {members}\nID: {chat.id}")
    send_webhook(f"Profil: {title} ({members} üye)")

# ==================== ANA PROGRAM ====================
async def main():
    print(f"{Fore.YELLOW}Telegram'a bağlanıyor...")
    try:
        await client.start(phone=phone)
        me = await client.get_me()
        print(f"{Fore.GREEN}Bağlandı! {me.first_name} (@{me.username or 'yok'})")
    except Exception as e:
        print(f"{Fore.RED}Bağlantı hatası: {e}")
        return

    while True:
        choice = menu()
        if choice == '1': await option1()
        elif choice == '2': await option2()
        elif choice == '3': await option3()
        elif choice == '4': await option4()
        elif choice == '5': await option5()
        elif choice == '0':
            print(f"{Fore.YELLOW}Çıkış yapılıyor...")
            break
        else:
            print(f"{Fore.RED}Geçersiz seçim!")
        input(f"\n{Fore.YELLOW}Devam için Enter...")

    await client.disconnect()
    print(f"{Fore.GREEN}Bağlantı kesildi. Görüşürüz!")

# ==================== ÇALIŞTIR ====================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Kullanıcı iptal etti.")
    except Exception as e:
        print(f"{Fore.RED}Kritik hata: {e}")