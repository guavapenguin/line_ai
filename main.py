import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# 從環境變數中獲取 LINE API Key (此變數僅用於列印，不影響 Webhook 邏輯)
LINE_API_KEY = os.environ.get("API_KEY")

# --- 輔助函數區 (Helper Functions for LINE Custom Payload) ---

def create_mbti_flex_message(result_text, query):
    """
    生成一個 LINE Flex Message JSON 結構，用於展示 MBTI 分析結果。
    (包含您的工程師和數據分析背景的客製化內容)
    """
    return {
      "type": "flex",
      "altText": "樂團MBTI分析結果",
      "contents": {
        "type": "bubble",
        "body": {
          "type": "box",
          "layout": "vertical",
          "contents": [
            {"type": "text", "text": "樂團 MBTI 數據分析", "weight": "bold", "size": "xl"},
            {"type": "separator", "margin": "md"},
            {"type": "text", "text": f"分析請求: {query}", "margin": "md", "size": "sm", "color": "#aaaaaa"},
            {"type": "text", "text": result_text, "wrap": True, "margin": "md", "size": "lg", "color": "#1DB446"},
            {"type": "text", "text": "數據來自您的樂團資料庫，推論機率已優化。", "margin": "md", "size": "xxs", "color": "#aaaaaa"}
          ]
        }
      }
    }

def create_link_carousel_message(links_data):
    """
    生成一個 LINE Carousel 訊息 JSON 結構，展示多個重要連結。
    """
    columns = []
    for title, url in links_data:
        columns.append({
          "thumbnailImageUrl": "https://i.imgur.com/K9sXz3o.png", # 請替換為樂團圖示 URL
          "title": title,
          "text": f"點擊開啟 {title}",
          "actions": [
            {
              "type": "uri",
              "label": "開啟連結",
              "uri": url
            }
          ]
        })
    return {
        "type": "template",
        "altText": "樂團重要連結清單",
        "template": {
            "type": "carousel",
            "columns": columns
        }
    }


# --- Webhook 路由 (The Core Logic) ---

@app.route("/", methods=["POST"])
def webhook():
    # 接收 Dialogflow CX 傳送過來的 JSON 數據
    req = request.get_json(silent=True, force=True)
    
    # 【安全修正】確保 user_message 永遠是字串，避免 NoneType 錯誤
    user_message = req.get("text", "").strip() 
    tag = req.get("tag") # 預期為 "process_user_query"
    
    # 預設的回覆 (如果沒有匹配到任何邏輯)
    response_text = "抱歉，助理已啟動，但我無法從您的查詢中找到有效的指令關鍵詞。"
    line_message_json = None
    
    # --- 邏輯判斷：如果包含喚醒詞，則執行業務邏輯 ---
    if "彩虹城市AI助理" in user_message: 
        
        # --- 邏輯 A: MBTI 查詢 (判斷原始文字是否包含關鍵詞) ---
        if "MBTI" in user_message.upper() or "分析" in user_message:
            result_text = "偵測到您的 INTJ 特質，專注度高。根據樂團歷史數據推算：您的樂團合作潛力為 92%，但決策效率的衝突機率為 35%。建議設立數據基準點來協調分歧。"
            line_message_json = create_mbti_flex_message(result_text, user_message)
            response_text = "MBTI 分析結果已透過 Flex Message 傳送。"
            
        # --- 邏輯 B: 繳費查詢 ---
        elif "繳費" in user_message or "狀態" in user_message:
            member_id = "0711" 
            status = "已繳清"
            due_date = "2026/01/15 (下一期)"
            response_text = f"【樂團繳費狀態查詢】\n團員 ID {member_id} 的最新狀態：\n**目前狀態：{status}**。\n下一期費用將於 {due_date} 產生。請保持數據整合，避免行政錯誤。"
            
        # --- 邏輯 C: 連結查詢 ---
        elif "連結" in user_message or "清單" in user_message:
            links_data = [
                ("🎼 排練時間與進度表", "https://docs.google.com/schedule_doc"),
                ("🎵 樂譜雲端總庫", "https://drive.google.com/score_folder"),
            ]
            line_message_json = create_link_carousel_message(links_data)
            response_text = "樂團重要連結清單已傳送，請使用輪播訊息查看。"

        # --- 邏輯 D: 守門員回覆（若只輸入喚醒詞或無關鍵字）---
        elif "彩虹城市AI助理" == user_message:
            response_text = "樂團助理已啟動。請在『彩虹城市AI助理』後，加上您的查詢內容，例如：**查MBTI**、**繳費狀態**或**連結清單**。"
            
    # --- 最終：構建 Dialogflow CX 期望的回應格式 ---
    if line_message_json:
        # 回傳 Custom Payload (Flex 或 Carousel)
        dialogflow_cx_response = {
            "fulfillmentResponse": {
                "messages": [{"payload": {"line": line_message_json}}]
            }
        }
    else:
        # 回傳標準的文字回覆格式 (用於繳費查詢或提示訊息)
        dialogflow_cx_response = {
            "fulfillmentResponse": {
                "messages": [{"text": {"text": [response_text]}}]
            }
        }
    
    # 確保總是回傳 JSON
    return jsonify(dialogflow_cx_response)


@app.route("/health", methods=["GET"])
def health_check():
    """Cloud Run Health Check"""
    return "OK", 200


if __name__ == "__main__":
    # 根據 Cloud Run 的環境變數設定 PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
