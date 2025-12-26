import time
import requests
import logging
import json
import os
import re
import sys
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TimedOut
import asyncio
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='telegram.utils.request')

# === CONFIG ===
TG_Username = '@motion_earn_backup'
BOT_TOKEN = '8120061901:AAFWh6dyofD7mtepgo-G8vy0_M_H917iSUg'
CHAT_ID = '-1002744208270'
USERNAME = 'Omorfaruk00'
PASSWORD = 'Omorfarukff'
BASE_URL = "http://94.23.120.156"
LOGIN_PAGE_URL = BASE_URL + "/ints/login"
LOGIN_POST_URL = BASE_URL + "/ints/signin"
DATA_URL = BASE_URL + "/ints/client/res/data_smscdr.php"

# 🔹 ONLY NEW CONFIG
NUMBER_CHANNEL = "@motion_numbers"

# Initialize Telegram bot
bot = Bot(token=BOT_TOKEN)

# Global session
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

# Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def escape_markdown(text: str) -> str:
    return re.sub(r'([_*()~`>#+=|{}.!-])', r'\\\1', text)

def save_already_sent(already_sent):
    with open("already_sent.json", "w") as f:
        json.dump(list(already_sent), f)

def load_already_sent():
    if os.path.exists("already_sent.json"):
        with open("already_sent.json", "r") as f:
            return set(json.load(f))
    return set()

u = 'করুন'

def login():
    try:
        logging.info("Attempting to load login page...")
        resp = session.get(LOGIN_PAGE_URL)
        match = re.search(r'What is (\d+) \+ (\d+)', resp.text)
        if not match:
            logging.error("Captcha not found.")
            return False
        num1, num2 = int(match.group(1)), int(match.group(2))
        captcha_answer = num1 + num2
        logging.info(f"Solved captcha: {num1} + {num2} = {captcha_answer}")

        payload = {
            "username": USERNAME,
            "password": PASSWORD,
            "capt": captcha_answer
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": LOGIN_PAGE_URL
        }

        resp = session.post(LOGIN_POST_URL, data=payload, headers=headers)
        if "dashboard" in resp.text.lower() or "logout" in resp.text.lower():
            logging.info("Login successful ✓")
            return True
        else:
            logging.error("Login failed ✗")
            return False
    except Exception as e:
        logging.error(f"Login error: {e}")
        return False

def build_api_url():
    start_date = "2025-05-05"
    end_date = "2026-01-01"
    return (
        f"{DATA_URL}?fdate1={start_date}%2000:00:00&fdate2={end_date}%2023:59:59&"
        "frange=&fnum=&fcli=&fgdate=&fgmonth=&fgrange=&fgnumber=&fgcli=&fg=0&"
        "sEcho=1&iColumns=7&sColumns=%2C%2C%2C%2C%2C%2C&iDisplayStart=0&iDisplayLength=25&"
        "mDataProp_0=0&sSearch_0=&bRegex_0=false&bSearchable_0=true&bSortable_0=true&"
        "mDataProp_1=1&sSearch_1=&bRegex_1=false&bSearchable_1=true&bSortable_1=true&"
        "mDataProp_2=2&sSearch_2=&bRegex_2=false&bSearchable_2=true&bSortable_2=true&"
        "mDataProp_3=3&sSearch_3=&bRegex_3=false&bSearchable_3=true&bSortable_3=true&"
        "mDataProp_4=4&sSearch_4=&bRegex_4=false&bSearchable_4=true&bSortable_4=true&"
        "mDataProp_5=5&sSearch_5=&bRegex_5=false&bSearchable_5=true&bSortable_5=true&"
        "mDataProp_6=6&sSearch_6=&bRegex_6=false&bSearchable_6=true&bSortable_6=true&"
        "sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=desc&iSortingCols=1"
    )

t = u
already_sent = load_already_sent()

def fetch_data():
    url = build_api_url()
    headers = {"X-Requested-With": "XMLHttpRequest"}

    try:
        response = session.get(url, headers=headers, timeout=10)
        logging.info(f"Response Status: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403 or "login" in response.text.lower():
            logging.warning("Session expired. Re-logging...")
            if login():
                return fetch_data()
        return None
    except Exception as e:
        logging.error(f"Fetch error: {e}")
        return None

async def sent_messages():
    logging.info("Checking for messages...")
    data = fetch_data()

    if data and 'aaData' in data:
        for row in data['aaData']:
            date = str(row[0]).strip()
            number = str(row[2]).strip()
            service = str(row[3]).strip()
            message = str(row[4]).strip()

            match = re.search(r'\d{3}-\d{3}|\d{4,6}', message)
            otp = match.group() if match else None

            if otp:
                unique_key = f"{number}|{otp}"
                if unique_key not in already_sent:
                    already_sent.add(unique_key)

                    text = (
                        "💥 *NEW OTP RECEIVED* 💥\n\n"
                        f"⏰ Time: {escape_markdown(date)}\n"
                        f"🔏 SERVICE: `{escape_markdown(service)}`\n"
                        f"🌎 NUMBER: `{escape_markdown(number)}`\n\n"
                        f"💌MAIN OTP: `{escape_markdown(otp)}`\n\n"
                        f"*MASSAGE*\n"
                        f"```{escape_markdown(message)}```\n\n"
                        f"💢 *{escape_markdown('Be Active, New OTP Loading...')}*\n\n"
                        f"*আমাদের ব্যাকআপ চ্যানেল এ জয়েন {escape_markdown(u)}*  *{escape_markdown(TG_Username)}*"
                    )

                    # 🔹 ONLY ADDITION: NUMBER CHANNEL BUTTON
                    keyboard = [[
                        InlineKeyboardButton(
                            "📢 NUMBER CHANNEL",
                            url=f"https://t.me/{NUMBER_CHANNEL.lstrip('@')}"
                        )
                    ]]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    try:
                        await bot.send_message(
                            chat_id=CHAT_ID,
                            text=text,
                            parse_mode="MarkdownV2",
                            reply_markup=reply_markup
                        )
                        save_already_sent(already_sent)
                        logging.info(f"[+] Sent OTP: {otp}")
                    except TimedOut:
                        logging.error("Telegram TimedOut")
                    except Exception as e:
                        logging.error(f"Telegram error: {e}")
            else:
                logging.info(f"No OTP found in message: {message}")

async def main():
    logging.info("Bot started running...")
    if login():
        while True:
            await sent_messages()
            await asyncio.sleep(3)
    else:
        logging.error("Initial login failed. Exiting...")

if __name__ == "__main__":
    asyncio.run(main())
