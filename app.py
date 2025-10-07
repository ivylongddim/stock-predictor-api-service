# app.py 內容 (請複製以下所有代碼)
from flask import Flask, request, jsonify
import random
import os

app = Flask(__name__)

# 股價預測 API 端點
@app.route("/predict", methods=["POST"])
def predict():
    try:
        # 接收 n8n/Make 傳來的數據
        data = request.json
        if not data or not isinstance(data, list):
            return jsonify({"error": "Invalid data format. Expected a list."}), 400

        # 提取股票代碼和最新的收盤價
        # 這裡假設 n8n/Make 傳來的是單一股票的歷史數據列表，且最新數據在列表的 [0]
        
        # 確保數據列表非空且包含關鍵欄位
        if not data or '股票代碼' not in data[0] or '昨日收盤價 (NTD)' not in data[0]:
            return jsonify({"error": "Missing '股票代碼' or '昨日收盤價 (NTD)' in data."}), 400
            
        stock_code = data[0]['股票代碼']
        
        # 獲取最新收盤價，並進行清理
        try:
            latest_close = float(data[0]['昨日收盤價 (NTD)'])
        except ValueError:
            return jsonify({"error": f"Invalid price data for {stock_code}."}), 400

        # 核心預測區塊 (使用簡單的隨機模型)
        # 模擬一個簡單的預測模型：預測價格在最新收盤價的 +/- 0.5% 範圍內
        prediction_change_pct = random.uniform(-0.005, 0.005) 
        predicted_price = latest_close * (1 + prediction_change_pct)
        
        # 計算建議的買賣目標價
        # 交易策略範例：賣價比預測高 0.5%，買價比預測低 1.0%
        target_sell = predicted_price * 1.005
        target_buy = predicted_price * 0.99
        
        # 回傳結果給 n8n/Make
        return jsonify({
            "stock_code": stock_code,
            "predicted_price": round(predicted_price, 2),
            "target_buy": round(target_buy, 2),
            "target_sell": round(target_sell, 2),
            "base_price": round(latest_close, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e), "message": "An unexpected error occurred during processing"}), 500

# 啟動 Flask 服務 (Railway 會使用 OS 提供的 PORT 變數)
if __name__ == "__main__":
    # Railway 會在環境變數中提供 PORT，必須使用它
    port = int(os.environ.get("PORT", 5000))
    # 設置 host='0.0.0.0' 確保服務器可以監聽來自外部的請求
    app.run(host='0.0.0.0', port=port)