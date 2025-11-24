import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# 從環境變數中獲取 LINE API Key (此變數僅用於列印，不影響 Webhook 邏輯)
LINE_API_KEY = os.environ.get("API_KEY")

@app.route("/", methods=["POST"])
def webhook():
    # 接收 Dialogflow CX 傳送過來的 JSON 數據
    req = request.get_json(silent=True, force=True)
    
    # 修正：使用 .get() 並提供一個安全的預設值 "" (空字串)，然後再使用 .strip() 清理空格
    user_message = req.get("text", "").strip() # <-- 關鍵修正點：確保 user_message 永遠是字串
    
    # 預設的回覆 (如果沒有匹配到任何邏輯)
    response_text = "抱歉，助理已啟動，但我無法從您的查詢中找到有效的指令關鍵詞。"
    line_message_json = None
    
    # --- 邏輯判斷：確保 user_message 是字串後，才可以進行 'in' 判斷 ---
    # 因為前面我們使用了 .get("", "").strip()，所以這裡可以安全地執行 'in' 判斷
    if "彩虹城市AI助理" in user_message:        
        dialogflow_cx_response = {
            "fulfillmentResponse": {
                "messages": [{"text": {"text": [response_text]}}]
            }
        }
        return jsonify(dialogflow_cx_response)
    else:
        return ""


# --- Health Check 路由 ---

@app.route("/health", methods=["GET"])
def health_check():
    """Cloud Run Health Check"""
    return "OK", 200


if __name__ == "__main__":
    # 根據 Cloud Run 的環境變數設定 PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
