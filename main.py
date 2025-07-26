import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Получаем переменные из окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("DEBUG: BOT_TOKEN =", BOT_TOKEN)
print("DEBUG: CHAT_ID =", CHAT_ID)

URL = "https://www.ebay.com/itm/356848025074"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        print("📨 Telegram отправлено:", response.status_code)
    except Exception as e:
        print("❌ Ошибка при отправке Telegram:", e)

def check_stock():
    try:
        text = requests.get(URL).text
        has_out = "Out of Stock" in text or "This item is out of stock" in text
        has_buy = "Add to cart" in text or "Buy It Now" in text or "Place bid" in text
        return (not has_out) and has_buy
    except Exception as e:
        print("❌ Ошибка при загрузке страницы:", e)
        return False

def main():
    print("🚀 Бот запущен на Railway.")
    send_telegram("🟢 Бот eBay Checker запущен и работает 24/7.")

    notified = False
    last_info_time = datetime.now() - timedelta(hours=1)

    while True:
        in_stock = check_stock()

        if in_stock:
            if not notified:
                send_telegram("🛒 Railway - Товар снова в наличии! 👉 https://www.ebay.com/itm/356848025074")
                notified = True
        else:
            print("⏳ Товара нет. Ждём...")
            notified = False

            # Раз в час отправляем "живой отчёт"
            now = datetime.now()
            if now - last_info_time >= timedelta(hours=1):
                send_telegram("⏳ Я работаю, но товара пока нет в наличии.")
                last_info_time = now

        time.sleep(60)

if __name__ == "__main__":
    main()
    # Обновление для перезапуска
