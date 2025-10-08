# app.py 內容：用於 Railway 部署的 Flask 預測服務
import os
import random
import json
from flask import Flask, request, jsonify

# 初始化 Flask 應用
app = Flask(__name__)

# 股價預測 API 端點
@app.route("/predict", methods=["POST"])
def predict():
    try:
        # 1. 嘗試從標準 JSON 體獲取數據 (Flask 預設行為)
        data = request.json
        
        # 2. 如果標準 JSON 體獲取失敗，則嘗試手動解析其他格式的數據
        if not data and request.data:
            
            # 嘗試解析 URL 編碼的表單數據 (如果 Make 採用 x-www-form-urlencoded 模式)
            # Make 會將整個 JSON 字串放在一個名為 'data' 的 field 裡
            if request.form and 'data' in request.form:
                data_string = request.form['data']
                # 再次手動解析這個 JSON 字串 (使用 json.loads)
                data = json.loads(data_string) 
            
            # 如果以上都失敗，再嘗試將原始請求體解析為 JSON
            elif request.data:
                data = json.loads(request.data.decode('utf-8'))


        # 3. 檢查數據是否為我們預期的列表格式
        if not data or not isinstance(data, list):
            return jsonify({"error": "Invalid data format. Expected a list."}), 400

        # 4. 提取關鍵欄位
        
        # 確保數據列表非空且包含關鍵欄位
        if not data or '股票代碼' not in data[0] or '昨日收盤價 (NTD)' not in data[0]:
            return jsonify({"error": "Missing '股票代碼' or '昨日收盤價 (NTD)' in data."}), 400
            
        stock_code = data[0]['股票代碼']
        
        # 獲取最新收盤價，並進行清理
        try:
            # 確保價格可以被轉換成浮點數
            latest_close = float(data[0]['昨日收盤價 (NTD)'])
        except ValueError:
            return jsonify({"error": f"Invalid price data for {stock_code}. Value received: {data[0]['昨日收盤價 (NTD)']}"}), 400

        
        # 5. 核心預測區塊 (使用簡單的隨機模型進行模擬)
        # 這裡將來會替換成您的實際機器學習預測模型
        prediction_change_pct = random.uniform(-0.005, 0.005) 
        predicted_price = latest_close * (1 + prediction_change_pct)
        
        # 6. 計算建議的買賣目標價
        target_sell = predicted_price * 1.005
        target_buy = predicted_price * 0.99
        
        # 7. 回傳結果給 Make
        return jsonify({
            "stock_code": stock_code,
            "predicted_price": round(predicted_price, 2),
            "target_buy": round(target_buy, 2),
            "target_sell": round(target_sell, 2),
            "base_price": round(latest_close, 2)
        })

    except Exception as e:
        # 捕捉所有未預期的錯誤，並回傳 500 錯誤訊息
        return jsonify({"error": str(e), "message": "An unexpected error occurred during processing"}), 500

# 啟動 Flask 服務 (這是 Railway 伺服器啟動的標準入口點)
if __name__ == "__main__":
    # Railway 會在環境變數中提供 PORT，使用 host='0.0.0.0' 確保服務可從外部訪問
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)