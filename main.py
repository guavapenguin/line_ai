import os
from flask import Flask, request, jsonify

app = Flask(__name__)
LINE_API_KEY = os.environ.get("API_KEY")

# 輔助函數：生成 LINE Quick Reply 訊息
def create_quick_reply(text, options):
    items = []
    for label, postback_text in options:
        items.append({
            "type": "action",
            "action": {"type": "message", "label": label, "text": postback_text}
        })
    return {
        "type": "text",
        "text": text,
        "quickReply": {"items": items}
    }

@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json(silent=True, force=True)
    # print(f"Received Dialogflow CX request: {req}")

    # --- Step 1: 解析關鍵上下文 ---
    tag = req.get("tag")
    user_message = req.get("text", "未知的輸入")
    
    response_text = f"抱歉，後端程式碼無法識別標籤 '{tag}'，請檢查路由設定。"
    line_message_json = None
    
    # --- Step 2: 根據 Tag 加入業務邏輯判斷 ---

    if tag == "initial_greeting":
        # 邏輯 A: 剛進入對話，提供樂團相關服務選項
        
        # 使用你提供的樂團相關選項清單
        options = [
            ("樂團MBTI分析", "我想看樂團MBTI分析結果"),
            ("繳費查詢", "我想查詢繳費狀態"),
            ("連結查詢", "我想查詢連結清單")
        ]
        
        response_text = "歡迎使用樂團助理服務！我可以協助您進行樂團成員數據分析與行政事務查詢。請問您需要哪項協助？"
        line_message_json = create_quick_reply(response_text, options)
        
    # --- 其他 tag 判斷 (例如 query_mbti, query_payment, query_links) ---
    # 你應該在 CX 中為這些 text (例如 "我想看樂團MBTI分析結果") 設定新的 Intent 和 Webhook Tag
    elif tag == "query_mbti":
        response_text = "要進行MBTI分析，我需要所有團員的MBTI類型數據。請您提供資料，我將推算出樂團的合作機率和潛在衝突點。"
        # 這裡可以加入更進階的邏輯，例如要求用戶輸入團員名單
        line_message_json = create_quick_reply(response_text, [("提供數據", "開始輸入MBTI資料")])

    elif tag == "query_payment":
        # 這裡可以呼叫外部 API 查詢資料庫
        response_text = "請輸入您的團員編號，我將為您查詢最近一次的繳費狀態和截止日期。"

    # --- Step 3: 構建 Dialogflow CX 期望的回應格式 ---
    if line_message_json:
        dialogflow_cx_response = {
            "fulfillmentResponse": {
                "messages": [{"payload": {"line": line_message_json}}]
            }
        }
    else:
        dialogflow_cx_response = {
            "fulfillmentResponse": {
                "messages": [{"text": {"text": [response_text]}}]
            }
        }

    return jsonify(dialogflow_cx_response)

# (其餘程式碼不變)
@app.route("/health", methods=["GET"])
def health_check():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
