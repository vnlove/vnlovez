#!/usr/bin/env python3
"""Lấy giá vàng từ DOJI và gửi về Telegram."""

import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError

DOJI_API = "https://giavang.doji.vn/api/giavang/?api_key=258fbd2a19eab10e3bbd33a7&jsoncallback=jQuery"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "chat_id_group_vip")


def fetch_doji_prices():
    req = Request(DOJI_API, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=15) as resp:
        raw = resp.read().decode("utf-8-sig")

    root = ET.fromstring(raw)
    result = {"domestic": [], "international": [], "domestic_time": "", "intl_time": ""}

    dgp = root.find("DGPlist")
    if dgp is not None:
        dt = dgp.find("DateTime")
        if dt is not None and dt.text:
            result["domestic_time"] = dt.text.strip()
        for row in dgp.findall("Row"):
            result["domestic"].append({
                "name": row.get("Name", ""),
                "buy": row.get("Buy", "N/A"),
                "sell": row.get("Sell", "N/A"),
            })

    igp = root.find("IGPList")
    if igp is not None:
        dt = igp.find("DateTime")
        if dt is not None and dt.text:
            result["intl_time"] = dt.text.strip()
        for row in igp.findall("Row"):
            result["international"].append({
                "name": row.get("Name", ""),
                "buy": row.get("Buy", "N/A"),
                "sell": row.get("Sell", "N/A"),
            })

    return result


def format_message(data):
    vn_tz = timezone(timedelta(hours=7))
    now = datetime.now(vn_tz).strftime("%H:%M %d/%m/%Y")

    lines = [f"💰 GIÁ VÀNG DOJI - {now}", ""]

    if data["domestic"]:
        time_str = data["domestic_time"] or now
        lines.append(f"🇻🇳 VÀNG TRONG NƯỚC ({time_str})")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        for item in data["domestic"]:
            lines.append(f"▸ {item['name']}")
            lines.append(f"  Mua:  {item['buy']}")
            lines.append(f"  Bán:  {item['sell']}")
            lines.append("")

    if data["international"]:
        time_str = data["intl_time"] or now
        lines.append(f"🌍 THỊ TRƯỜNG QUỐC TẾ ({time_str})")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        for item in data["international"]:
            lines.append(f"▸ {item['name']}")
            lines.append(f"  Mua:  {item['buy']}")
            lines.append(f"  Bán:  {item['sell']}")
            lines.append("")

    lines.append("🔗 Nguồn: DOJI (giavang.doji.vn)")
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
        print("ERROR: Set TELEGRAM_BOT_TOKEN environment variable")
        sys.exit(1)
    if not chat_id or chat_id == "chat_id_group_vip":
        print("WARNING: TELEGRAM_CHAT_ID chưa được set, dùng mặc định 'chat_id_group_vip'")

    print("Đang lấy giá vàng từ DOJI...")
    try:
        data = fetch_doji_prices()
    except (URLError, ET.ParseError) as e:
        print(f"ERROR: Không lấy được giá vàng: {e}")
        sys.exit(1)

    msg = format_message(data)
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
