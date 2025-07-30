import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

BOT_TOKEN = "7828405994:AAFCzF4_f-WgB4BW0NtWIEma7YhZgqBzbbM"
CHAT_ID = "634345487"
URL = "https://www.ebay.com/itm/356848025074"

# Статус включения скрипта
active = False
last_info_time = datetime.now() - timedelta(hours=1)
last_update_id = None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("❌ Telegram send error:", e)

def check_stock():
    try:
        html = requests.get(URL).text
        has_out = "Out of Stock" in html or "This item is out of stock" in html
        has_buy = "Add to cart" in html or "Buy It Now" in html or "Place bid" in html
        return (not has_out) and has_buy
    except Exception as e:
        print("❌ Ошибка при загрузке страницы:", e)
        return False

def check_commands():
    global active, last_update_id
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(url).json()
        for update in response["result"]:
            update_id = update["update_id"]
            message = update.get("message", {})
            text = message.get("text", "").lower()
            chat_id = str(message.get("chat", {}).get("id", ""))

            if chat_id != CHAT_ID:
                continue  # Игнорируем чужие сообщения

            if last_update_id is None or update_id > last_update_id:
                last_update_id = update_id

                if text == "/пуск":
                    active = True
                    send_telegram("▶️ Мониторинг запущен.")
                elif text == "/стоп":
                    active = False
                    send_telegram("⏹ Мониторинг остановлен.")
                elif text == "/статус":
                    status = "🟢 ВКЛЮЧЕН" if active else "🔴 ВЫКЛЮЧЕН"
                    send_telegram(f"⚙️ Статус бота: {status}")
    except Exception as e:
        print("❌ Ошибка в check_commands:", e)

def main():
    global last_info_time
    print("🚀 Бот запущен с Telegram-управлением.")
    send_telegram("🤖 Бот запущен. Используй /пуск, /стоп, /статус для управления.")

    while True:
        check_commands()

        if active:
            if check_stock():
                send_telegram("🛒 Товар в наличии! 👉 https://www.ebay.com/itm/356848025074")
            else:
                now = datetime.now()
                if now - last_info_time >= timedelta(hours=1):
                    send_telegram("⏳ Я работаю, но товара пока нет.")
                    last_info_time = now
        else:
            print("⏸ Мониторинг выключен.")

        time.sleep(180)

if __name__ == "__main__":
    main()
