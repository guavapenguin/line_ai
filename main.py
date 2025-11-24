import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# 從環境變數中獲取 LINE API Key (保留此行，但不影響 Webhook 運作)
LINE_API_KEY = os.environ.get("API_KEY")

# --- 輔助函數區 (Helper Functions for LINE Custom Payload) ---

# 輔助函數 A: 生成 LINE Flex Message 範例 (用於 MBTI 結果)
def create_mbti_flex_message(result_text, query):
    """
    生成一個 LINE Flex Message JSON 結構，用於展示 MBTI 分析結果。
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
            {"type": "text", "text": "數據來自您的樂團資料。", "margin": "md", "size": "xxs", "color": "#aaaaaa"}
          ]
        }
      }
    }

# 輔助函數 B: 生成 LINE Carousel 訊息 (用於連結查詢)
def create_link_carousel_message(links_data):
    """
    生成一個 LINE Carousel 訊息 JSON 結構，展示多個重要連結。
    """
    columns = []
    for title, url in links_data:
        columns.append({
          "thumbnailImageUrl": "https://i.imgur.com/K9sXz3o.png", # 替換為樂團或文件的圖示 URL
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
    # print(f"Received Dialogflow CX request: {req}") # 建議在除錯時開啟

    # 解析關鍵上下文：Webhook Tag 和用戶輸入
    tag = req.get("tag") 
    user_message = req.get("text", "未知的輸入")
    
    # 預設的回覆 (如果沒有匹配到任何 tag 或發生錯誤)
    response_text = "抱歉，無法識別您的樂團助理請求，請確保您輸入『彩虹城市AI助理』並加上明確的查詢內容。"
    line_message_json = None
    
    
    # --- 邏輯 A: MBTI 查詢 (Tag: direct_mbti_query) ---
    if tag == "direct_mbti_query":
        # 根據你的專科數學和數據分析背景，提供一個數據化回應
        result_text = "偵測到您的 INTJ 特質，專注度高。根據樂團歷史數據推算：您的樂團合作潛力為 92%，但由於團員間的『感知型(P)』與『判斷型(J)』比例失衡，決策效率的衝突機率為 35%。建議設立數據基準點來協調分歧。"
        line_message_json = create_mbti_flex_message(result_text, user_message)
        response_text = "MBTI 分析結果已透過 Flex Message 完成傳送。"
        
    # --- 邏輯 B: 繳費查詢 (Tag: direct_payment_query) ---
    elif tag == "direct_payment_query":
        # 模擬查詢結果 (假設團員 ID 0711)
        member_id = "0711" 
        status = "已繳清"
        due_date = "2026/01/15 (下一期)"
        
        # 構建純文字回覆
        response_text = f"【樂團繳費狀態查詢】\n團員 ID {member_id} 的最新狀態：\n**目前狀態：{status}**。\n下一期費用將於 {due_date} 產生。請保持數據整合，避免行政錯誤。"
        
    # --- 邏輯 C: 連結查詢 (Tag: direct_links_query) ---
    elif tag == "direct_links_query":
        # 提供樂團重要連結數據
        links_data = [
            ("🎼 排練時間與進度表", "https://docs.google.com/schedule_doc"),
            ("🎵 樂譜雲端總庫", "https://drive.google.com/score_folder"),
            ("🗳️ 行政會議紀錄與投票", "https://notion.so/meeting_notes")
        ]
        line_message_json = create_link_carousel_message(links_data)
        response_text = "樂團重要連結清單已傳送，請使用輪播訊息查看。"


    # --- 最終：構建 Dialogflow CX 期望的回應格式 ---
    if line_message_json:
        # 如果生成了 Custom Payload (Flex 或 Carousel)，則使用 payload 格式
        dialogflow_cx_response = {
            "fulfillmentResponse": {
                "messages": [{"payload": {"line": line_message_json}}]
            }
        }
    else:
        # 否則使用標準的文字回覆格式
        dialogflow_cx_response = {
            "fulfillmentResponse": {
                "messages": [{"text": {"text": [response_text]}}]
            }
        }

    return jsonify(dialogflow_cx_response)


@app.route("/health", methods=["GET"])
def health_check():
    """Cloud Run Health Check"""
    return "OK", 200


if __name__ == "__main__":
    # 根據 Cloud Run 的環境變數設定 PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
