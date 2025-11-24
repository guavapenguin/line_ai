import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# 從環境變數中獲取 LINE API Key (此變數僅用於列印，不影響 Webhook 邏輯)
LINE_API_KEY = os.environ.get("API_KEY")

# --- Webhook 路由 (The Core Logic) ---
@app.route("/", methods=["POST"])
def webhook():
    # 接收 Dialogflow CX 傳送過來的 JSON 數據
    req = request.get_json(silent=True, force=True)
    
    # 注意：這裡的 user_message 是 Webhook 進行邏輯判斷的唯一依據
    user_message = req.get("text")

    line_message_json = None
    
    # --- 邏輯 D: 守門員回覆（若只輸入喚醒詞）---
    if "彩虹城市AI助理" in user_message:                  
        dialogflow_cx_response = {
            "fulfillmentResponse": {
                "messages": [{"payload": {"line": line_message_json}}]
            }
        }
        return jsonify(dialogflow_cx_response)
    return "OK", 200


# --- Health Check 路由 ---

@app.route("/health", methods=["GET"])
def health_check():
    """Cloud Run Health Check"""
    return "OK", 200


if __name__ == "__main__":
    # 根據 Cloud Run 的環境變數設定 PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
