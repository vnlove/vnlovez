#!/usr/bin/env python3
"""Lấy giá BTC từ CoinGecko và gửi về Telegram."""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError

COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,vnd&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true"

TELEGRAM_BOT_TOKEN = os.environ.get("ap_key_telegram_dvtbot", "")
TELEGRAM_CHAT_ID = os.environ.get("chat_id_group_vip", "")


def fetch_btc_price():
    req = Request(COINGECKO_API, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["bitcoin"]


def format_number(n):
    if isinstance(n, float):
        if n >= 1_000_000_000:
            return f"{n / 1_000_000_000:,.2f} tỷ"
        if n >= 1_000_000:
            return f"{n / 1_000_000:,.2f} triệu"
    return f"{n:,.0f}"


def format_message(btc):
    vn_tz = timezone(timedelta(hours=7))
    now = datetime.now(vn_tz).strftime("%H:%M %d/%m/%Y")

    change_24h = btc.get("usd_24h_change", 0)
    arrow = "🟢 +" if change_24h >= 0 else "🔴 "

    lines = [
        f"₿ GIÁ BITCOIN - {now}",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━",
        f"💵 USD:  ${format_number(btc['usd'])}",
        f"🇻🇳 VND:  {format_number(btc['vnd'])} đ",
        "",
        f"📈 24h:  {arrow}{change_24h:.2f}%",
        f"📊 Khối lượng 24h: ${format_number(btc['usd_24h_vol'])}",
        f"💰 Vốn hóa: ${format_number(btc['usd_market_cap'])}",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "🔗 Nguồn: CoinGecko",
    ]
    return "\n".join(lines)


def send_telegram(text, bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
    }).encode("utf-8")
    req = Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    })
    with urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result


def main():
    bot_token = TELEGRAM_BOT_TOKEN
    chat_id = TELEGRAM_CHAT_ID

    if not bot_token:
        print("ERROR: Chưa set biến môi trường ap_key_telegram_dvtbot")
        sys.exit(1)
    if not chat_id:
        print("ERROR: Chưa set biến môi trường chat_id_group_vip")
        sys.exit(1)

    print("Đang lấy giá BTC từ CoinGecko...")
    try:
        btc = fetch_btc_price()
    except (URLError, KeyError, json.JSONDecodeError) as e:
        print(f"ERROR: Không lấy được giá BTC: {e}")
        sys.exit(1)

    msg = format_message(btc)
    print(msg)
    print()

    print(f"Đang gửi về Telegram (chat_id: {chat_id})...")
    try:
        result = send_telegram(msg, bot_token, chat_id)
        if result.get("ok"):
            print("Gửi thành công!")
        else:
            print(f"Gửi thất bại: {result}")
    except URLError as e:
        print(f"ERROR: Không gửi được Telegram: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
