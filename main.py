from flask import Flask, request, jsonify
import asyncio
from pyrogram import Client

app = Flask(__name__)

# بيانات حسابك وجلستك المستخرجة بنجاح
API_ID = 33399206
API_HASH = "b5e51c407203e5dcfabee2c9c1ae4d70"
SESSION_STRING = "BAH9oaYAVyNXhQ2Bw5tUGywqVHGsSQTwcs3ahnRJFy5B7rEZOYLCXPhAVyyUf2Ocm2fTBrE-2ks3LOhuMdRjkoXJsirp1KJsUST_LXMCW0-Aw4cx6Uq-NbITbbn-Lwf9X1wH30MkxKLZ7_YPmvGQ2BYgniz5irvjIYdE4gmDSXDO9QM7bGxa8LeDBB-BYtRplLrrgh2nJIvktpyUXgF_Rg87_910lqgJjKpGpyonhhFD0ws6v4Lhh37bnJutCe0YPpAZ4QT3xAdSHrVPEs9c9Ni3aR3UoB5k4yzlXXXdRJdDWvt7Xuc2YWqj7dzvkUBKvzmBwvwRf-NP5voJJ4xT0GvcrrwhJAAAAAIRq6xQAA"

async def run_publish(groups, text):
    async with Client(":memory:", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING) as user_app:
        for group in groups.split(","):
            if group.strip():
                try:
                    await user_app.send_message(chat_id=group.strip(), text=text)
                    await asyncio.sleep(30) # فاصل أمان لحماية حسابك من الحظر
                except Exception:
                    pass

@app.route('/publish', methods=['POST'])
def publish():
    data = request.json
    groups = data.get("groups")
    text = data.get("text")
    
    # تشغيل النشر بالحساب الشخصي في الخلفية بدون حظر السيرفر
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_publish(groups, text))
    return jsonify({"status": "success"})

@app.route('/')
def home():
    return "Server is Running 24/7!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

