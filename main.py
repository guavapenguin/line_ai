import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# 從環境變數中獲取 LINE API Key (此變數僅用於列印，不影響 Webhook 邏輯)
LINE_API_KEY = os.environ.get("API_KEY")

@app.route("/", methods=["POST"])
def webhook():
    # 接收 Dialogflow CX 傳送過來的 JSON 數據
    req = request.get_json(silent=True, force=True)
    
    # 修正：確保 user_message 永遠是字串
    user_message = req.get("text", "").strip()
    
    # 預設的回覆 (如果沒有匹配到任何邏輯)
    # 此訊息只會在 Webhook 內產生，如果 CX 判定不符合喚醒詞，這個訊息也不會傳給用戶
    response_text = "抱歉，助理已啟動，但我無法從您的查詢中找到有效的指令關鍵詞。"
    
    
    # --- 邏輯判斷：如果包含喚醒詞，則執行業務邏輯 ---
    if "彩虹城市AI助理" in user_message:
        # 這裡應該加入我們之前討論的複雜邏輯判斷：MBTI、繳費、連結
        
        # 為了測試，我們回傳一個簡單的確認回應
        response_text = f"助理已啟動並收到您的訊息：『{user_message}』，準備進行邏輯處理。"
    
    # --- 構建 Dialogflow CX 期望的回應格式 (不論邏輯是否匹配，都回傳此結構) ---
    dialogflow_cx_response = {
        "fulfillmentResponse": {
            "messages": [{"text": {"text": [response_text]}}]
        }
    }
    
    # 這裡確保總是回傳一個帶有 JSON 的 200 OK，而非僅僅 "OK"
    return jsonify(dialogflow_cx_response)


# --- Health Check 路由 ---

@app.route("/health", methods=["GET"])
def health_check():
    """Cloud Run Health Check"""
    return "OK", 200


if __name__ == "__main__":
    # 根據 Cloud Run 的環境變數設定 PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
