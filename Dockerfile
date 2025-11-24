# 使用官方 Python 基礎映像檔
FROM python:3.9-slim-buster

# 設定工作目錄
WORKDIR /app

# 將 requirements.txt 複製到工作目錄並安裝依賴
COPY requirements.txt .
RUN pip install -r requirements.txt

# 將應用程式程式碼複製到工作目錄
COPY . .

# Cloud Run 服務將監聽 PORT 環境變數指定的埠
ENV PORT 8080

# 運行應用程式
CMD ["python", "main.py"]

