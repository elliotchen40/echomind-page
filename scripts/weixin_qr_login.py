#!/usr/bin/env python3
"""Standalone WeChat QR login script using the same API as openclaw-weixin plugin."""

import urllib.request
import urllib.error
import json
import time
import sys

BASE_URL = "https://ilinkai.weixin.qq.com"
BOT_TYPE = "3"

def fetch_qrcode():
    url = f"{BASE_URL}/ilink/bot/get_bot_qrcode?bot_type={BOT_TYPE}"
    print(f"Fetching QR code from: {url}")
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    if data.get('ret') != 0:
        print(f"Failed to get QR code: {data}")
        sys.exit(1)
    return data['qrcode'], data.get('qrcode_img_content', '')

def poll_status(qrcode):
    url = f"{BASE_URL}/ilink/bot/get_qrcode_status?qrcode={urllib.parse.quote(qrcode)}"
    print(f"Polling QR status: {url}")
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    return data

def wait_for_scan(qrcode):
    print("Waiting for QR scan...")
    for i in range(90):  # 90 * 2 seconds = 3 minutes
        try:
            data = poll_status(qrcode)
            state = data.get('status')
            print(f"  [{i*2}s] status={state}")
            if state == 'confirmed':
                token = data.get('token', '')
                print(f"\n✅ Login successful! Token: {token}")
                return token
            elif state == 'expired':
                print("\n❌ QR code expired, need to regenerate")
                return None
        except Exception as e:
            print(f"  [{i*2}s] Error: {e}")
        time.sleep(2)
    print("\n❌ Timeout waiting for scan")
    return None

if __name__ == "__main__":
    import urllib.parse
    qrcode, qrcode_url = fetch_qrcode()
    print(f"QR code ID: {qrcode}")
    print(f"QR code URL: {qrcode_url}")
    print("\nPlease scan the QR code using WeChat!")
    print("Waiting up to 3 minutes for scan...\n")
    
    token = wait_for_scan(qrcode)
    if token:
        print(f"\nSave this token: {token}")
        print("Update your openclaw-weixin account file with this token.")
