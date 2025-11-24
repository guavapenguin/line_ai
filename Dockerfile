# 使用官方 Python 基礎映像檔
FROM python:3.9-slim-buster

# 設定工作目錄
WORKDIR /app

# 將 requirements.txt 複製到工作目錄並安裝依賴
COPY requirements.txt .
# 最終修正：強制 pip 重新安裝，避免快取問題
RUN pip install --upgrade -r requirements.txt --no-cache-dir

# 將應用程式碼複製到工作目錄 (確保 main.py 在這裡)
COPY . .

# 運行應用程式 (這將執行您正確的 main.py 邏輯)
CMD ["python", "main.py"]
