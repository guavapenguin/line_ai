import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# 從環境變數中獲取 LINE API Key
# 這個環境變數是我們在部署 Cloud Run 時，透過 --update-secrets 注入的
LINE_API_KEY = os.environ.get("API_KEY")


@app.route("/", methods=["POST"])
def webhook():
    # 接收 Dialogflow 傳送過來的 JSON 數據
    req = request.get_json(silent=True, force=True)
    print(f"Received Dialogflow request: {req}")

    # 這裡可以加入您的業務邏輯
    # 例如：解析用戶訊息，呼叫 Vertex AI，查詢資料庫等
    # 為了簡單起見，我們這裡只回傳一個簡單的訊息

    # 檢查 LINE API Key 是否已載入
    if LINE_API_KEY:
        print(
            f"LINE API Key loaded successfully (first few chars): {LINE_API_KEY[:5]}..."
        )
    else:
        print("Warning: LINE API Key not found in environment variables.")

    # 假設 Dialogflow 傳送的訊息在 req['queryResult']['queryText']
    user_message = req.get("queryResult", {}).get("queryText", "沒有收到訊息")

    response_text = f"您說了：'{user_message}'。這是來自 Cloud Run 的回應。您的 LINE API Key 似乎已設定。"

    # 構建 Dialogflow 期望的回應格式
    dialogflow_response = {"fulfillmentMessages": [{"text": {"text": [response_text]}}]}
    return jsonify(dialogflow_response)


@app.route("/health", methods=["GET"])
def health_check():
    return "OK", 200


if __name__ == "__main__":
    # Cloud Run 會將 PORT 環境變數注入到容器中
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
