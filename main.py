import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# 從環境變數中獲取 LINE API Key (保留，但不影響 Webhook 運作)
LINE_API_KEY = os.environ.get("API_KEY")

@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json(silent=True, force=True)
    print(f"Received Dialogflow CX request: {req}")

    # 嘗試從 CX 請求中獲取用戶輸入的文字和上下文
    user_message = req.get("text", "沒有找到用戶輸入文字")
    tag = req.get("tag", "No Tag")
    current_page = req.get("currentPage", {}).get("displayName", "Unknown Page")

    if LINE_API_KEY:
        print(f"LINE API Key loaded successfully (first few chars): {LINE_API_KEY[:5]}...")
    else:
        print("Warning: LINE API Key not found in environment variables.")

    # ----------------------------------------------------
    #  核心：構建 LINE Custom Payload 訊息
    # ----------------------------------------------------
    
    # 1. 構建要回傳給用戶的文字內容
    response_text = f"您在 '{current_page}' 頁面說：'{user_message}'。請問您對哪項服務感興趣？"
    
    # 2. 構建 LINE Quick Reply (快速回覆) 的按鈕清單
    # 這是 LINE Messaging API 規定的 JSON 格式
    quick_reply_items = [
        {
            "type": "action",
            "action": {
                "type": "message",
                "label": "樂團MBTI分析",
                "text": "我想看樂團MBTI分析結果"
            }
        },
        {
            "type": "action",
            "action": {
                "type": "message",
                "label": "繳費查詢",
                "text": "我想查詢繳費狀態"
            }
        },
        {
            "type": "action",
            "action": {
                "type": "message",
                "label": "連結查詢",
                "text": "我想查詢連結清單"
            }
        }
    ]

    # 3. 構建完整的 LINE 訊息 JSON 物件 (一個帶有 Quick Reply 的 Text Message)
    line_message_json = {
        "type": "text",
        "text": response_text,
        "quickReply": {
            "items": quick_reply_items
        }
    }

    # 4. 構建 Dialogflow CX 期望的回應格式 (使用 'payload' 欄位)
    dialogflow_cx_response = {
        "fulfillmentResponse": {
            "messages": [
                {
                    "payload": {
                        # 命名空間必須是 'line' 
                        "line": line_message_json
                    }
                }
            ]
        }
    }
    
    print(f"Sending CX Response: {dialogflow_cx_response}")
    return jsonify(dialogflow_cx_response)

# (健康檢查和啟動程式碼不變)
@app.route("/health", methods=["GET"])
def health_check():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
