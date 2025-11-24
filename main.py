import os
from flask import Flask, request, jsonify

app = Flask(__name__)
LINE_API_KEY = os.environ.get("API_KEY")

# 輔助函數：生成 LINE Flex Message 範例 (用於 MBTI 結果)
def create_mbti_flex_message(result_text, query):
    # 這裡放 Flex Message 的 JSON 內容... (略，沿用上次的複雜 JSON 結構)
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

# 輔助函數：生成 LINE Carousel 訊息 (用於連結查詢)
def create_link_carousel_message(links_data):
    # 模擬生成一個 Carousel (輪播) 訊息，展示多個連結
    columns = []
    for title, url in links_data:
        columns.append({
          "thumbnailImageUrl": "https://example.com/link_icon.png", # 替換為實際圖片URL
          "title": title,
          "text": f"點擊查看 {title} 文件",
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
        "altText": "重要連結清單",
        "template": {
            "type": "carousel",
            "columns": columns
        }
    }


@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json(silent=True, force=True)
    tag = req.get("tag") 
    user_message = req.get("text", "未知的輸入")
    
    response_text = "抱歉，無法識別您的樂團助理請求，請確保您包含『彩虹城市AI助理』和明確的查詢內容。"
    line_message_json = None
    
    # --- 邏輯 A: MBTI 查詢 (Tag: direct_mbti_query) ---
    if tag == "direct_mbti_query":
        # 這裡應該是調用你的數據分析服務
        result_text = "根據樂團歷史數據推算，您的團員在時間管理上存在分歧，可能與你們的『處女座INTJ』團員對細節的極致要求有關。建議使用數據整合工具來平衡排練時間。"
        line_message_json = create_mbti_flex_message(result_text, user_message)
        response_text = "MBTI 分析結果已完成。"
        
    # --- 邏輯 B: 繳費查詢 (Tag: direct_payment_query) ---
    elif tag == "direct_payment_query":
        # 這裡應該是呼叫外部資料庫或 API 進行查詢
        member_id = "0711" # 假設你已經從 CX 參數中解析出團員ID
        status = "已繳清"
        due_date = "2026/01/15 (下一期)"
        
        response_text = f"團員 ID {member_id} 的最新繳費狀態：\n**目前狀態：{status}**。\n下一期費用將於 {due_date} 產生。如有疑問，請聯繫行政組。"

    # --- 邏輯 C: 連結查詢 (Tag: direct_links_query) ---
    elif tag == "direct_links_query":
        # 提供樂團重要連結數據
        links_data = [
            ("排練時間表", "https://docs.google.com/schedule_doc"),
            ("樂譜雲端", "https://drive.google.com/score_folder"),
            ("行政會議紀錄", "https://notion.so/meeting_notes")
        ]
        line_message_json = create_link_carousel_message(links_data)
        response_text = "樂團重要連結清單已傳送，請使用輪播訊息查看。"


    # --- 構建 Dialogflow CX 期望的回應格式 ---
    # (此部分保持不變，根據是否有 Custom Payload 來回傳)
    if line_message_json:
        dialogflow_cx_response = {
            "fulfillmentResponse": {
                "messages": [{"payload": {"line": line_message_json}}]
            }
        }
    else:
        # 如果是繳費查詢 (純文字回覆)，則使用 text 格式
        dialogflow_cx_response = {
            "fulfillmentResponse": {
                "messages": [{"text": {"text": [response_text]}}]
            }
        }

    return jsonify(dialogflow_cx_response)

# (其餘程式碼不變)
