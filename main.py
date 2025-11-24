import os
import logging
from flask import Flask, request, jsonify
from google import genai
# 最終修正：修正匯入路徑，確保與安裝的 google-genai 套件結構匹配
from google.genai.errors import APIError  

# 設置日誌記錄
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- 環境變數設置 (通過 Cloud Run Secrets 注入) ---
# LINE/Gemini API Key
LINE_API_KEY = os.environ.get("API_KEY")
LINE_ASSERTION_KEY = os.environ.get("ASSERTION_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 初始化 Gemini Client
ai_client = None
if GEMINI_API_KEY:
    try:
        # 這裡的 genai 已經是從 from google import genai 來的
        ai_client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Gemini Client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Client: {e}")
else:
    logger.warning("GEMINI_API_KEY not found. AI features will be disabled.")


@app.route("/", methods=["POST"])
def webhook():
    """
    接收來自 Dialogflow CX 的 Webhook 請求，執行 AI 邏輯，並回傳格式化回應。
    """
    # 接收 Dialogflow 傳送過來的 JSON 數據
    req = request.get_json(silent=True, force=True)
    logger.info(f"Received Dialogflow request from user: {req.get('session', 'N/A')}")
    
    # 提取用戶訊息 (Dialogflow CX 格式)
    user_message = req.get("queryResult", {}).get("queryText", "沒有收到訊息")

    response_text = ""
    
    # --- 執行 AI 邏輯 ---
    if ai_client and user_message != "沒有收到訊息":
        try:
            logger.info(f"Calling Gemini with query: '{user_message}'")
            
            # 使用 gemini-2.5-flash 進行快速對話
            ai_response = ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message
            )
            response_text = ai_response.text
            
        except APIError as e:
            # 處理 API 級別的錯誤
            logger.error(f"Gemini API Error: {e}")
            response_text = "AI 服務呼叫失敗。請檢查 API 金鑰或配額設定。"
            
        except Exception as e:
            # 處理其他運行時錯誤
            logger.error(f"An unexpected error occurred during AI call: {e}")
            response_text = "後端系統處理錯誤，請稍後再試。"
    else:
        # 如果 AI client 未初始化，返回默認的檢查訊息
        response_text = f"您說了：'{user_message}'。這是來自 Cloud Run 的測試回應。AI 功能目前處於離線狀態 (Key未配置)。"

    # --- 構建 Dialogflow 期望的回應格式 ---
    dialogflow_response = {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [response_text]
                }
            }
        ]
    }
    
    # 必須返回 JSON
    return jsonify(dialogflow_response)


@app.route("/health", methods=["GET"])
def health_check():
    """
    Cloud Run 健康檢查端點。
    """
    return "OK", 200


if __name__ == "__main__":
    # 確保監聽 PORT=8080 和 0.0.0.0
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
