from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# Konfigurasi
TELEGRAM_TOKEN = '7805960444:AAEb3UUNT3DZUfds6G2trRLv8UrJtLZfyyc'
CHAT_ID = '-1002500559635'
LOGIN_URL = 'https://www.didihub.com/api/main/user/email/login'
PAY_CHANNEL_URL = 'https://www.didihub.com/api/main/pay/channel'
PAY_POST_URL = 'https://www.didihub.com/api/main/pay/67'

# Kredensial
email = "Bukanmasterbiasa@gmail.com"
password = "Gunawan12345"
browserVisitorId = "05467f96e147f52215497fe02e9d24e0"
programVisitorId = "8650KmEtzpHDEjWb"

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    resp = requests.post(url, json=payload)
    return resp.ok

def process_payment(amount):
    # Login ke didihub
    login_payload = {
        "email": email,
        "password": password,
        "browserVisitorId": browserVisitorId,
        "programVisitorId": programVisitorId
    }
    login_headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.didihub.com",
        "Referer": "https://www.didihub.com/"
    }

    try:
        login_resp = requests.post(LOGIN_URL, json=login_payload, headers=login_headers)
        if login_resp.status_code != 200:
            return {"success": False, "message": "Login gagal"}

        token = login_resp.json().get("token")
        if not token:
            return {"success": False, "message": "Token tidak ditemukan"}

        # Request pembayaran
        pay_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User_token": token,
            "Origin": "https://www.didihub.com",
            "Referer": "https://www.didihub.com/"
        }

        pay_payload = {
            "amount": amount,
            "phone": "822328947322",  # menggunakan nilai default
            "name": "ASEp"  # menggunakan nilai default
        }

        pay_resp = requests.post(PAY_POST_URL, json=pay_payload, headers=pay_headers)
        if pay_resp.status_code != 200:
            return {"success": False, "message": "Gagal request pembayaran"}

        pay_result = pay_resp.json()
        
        # Cek QR code URL dari response
        qr_code_url = pay_result.get('qrCodeUrl') or pay_result.get('qr_code') or pay_result.get('qr') or None

        if qr_code_url:
            message = f"Pembayaran berhasil!\nNominal: {amount}\nQR Code / Link: {qr_code_url}"
        else:
            message = f"Pembayaran berhasil! Data:\n{json.dumps(pay_result, indent=2)}"

        # Kirim ke Telegram
        send_telegram_message(TELEGRAM_TOKEN, CHAT_ID, message)
        
        return {"success": True, "message": "Pembayaran berhasil diproses", "data": pay_result}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    amount = request.form.get('amount')
    if not amount:
        return jsonify({"success": False, "message": "Nominal pembayaran harus diisi"})
    
    result = process_payment(amount)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)