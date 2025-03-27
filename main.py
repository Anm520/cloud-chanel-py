import requests
from bs4 import BeautifulSoup
from parser_utils import parse_message
from flask import Flask, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv
from flask_cors import CORS  # 导入CORS支持

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)
CHANNEL_NAME = os.getenv('CHANNEL_NAME', 'tianyirigeng')  # 默认值用于开发环境
PORT = os.getenv('PORT', 3001)  # 默认值用于开发环境
headers = {
        'authority': 't.me',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
def search_telegram_channel(base_url: str = None, params: dict = None):
    """动态获取频道名称"""
    channel = os.getenv('CHANNEL_NAME', CHANNEL_NAME)
    base_url = f"https://t.me/s/{channel}"
    try:
        response = requests.get(
            base_url,
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error {e.response.status_code}: {e.request.url}")
        return None
    except Exception as e:
        print(f"Request error: {str(e)}")
        return None

def fetch_telegram_channel(before: dict = None):
    """Telegram频道抓取核心函数
    Args:
        before_id (str|None): 可选的分页标识符
    """

    channel = os.getenv('CHANNEL_NAME', CHANNEL_NAME)
    url = f"https://t.me/s/{channel}"
    if before:
        url += f"?before={before}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None

@app.route('/messages', methods=['GET'])
def get_telegram_messages():
    try:
        # 允许空值且不强制校验
        before = request.args.get('before', default='', type=str)
        
        # 修改后的调用逻辑
        html_content = fetch_telegram_channel(before if before else None)
        
        if not html_content:
            return jsonify({"error": "Failed to fetch content"}), 500
            
        soup = BeautifulSoup(html_content, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message')
        
        results = []
        for message in messages:
            try:
                if data := parse_message(message):
                    results.append(data)
            except Exception as e:
                print(f"Error parsing message: {str(e)}")
                continue
                
        return jsonify({"data": results})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search_messages():
    try:
        # 必需参数校验
        search_query = request.args.get('q', type=str)
        if not search_query:
            return jsonify({"error": "Parameter 'q' is required"}), 400
        
        # 构造Telegram搜索URL（不带分页参数）
        channel = os.getenv('CHANNEL_NAME', CHANNEL_NAME)
        search_url = f"https://t.me/s/{channel}"
        params = {'q': search_query}
        
        # 获取并解析内容
        html_content = search_telegram_channel(search_url, params=params)
        if not html_content:
            return jsonify({"error": "Failed to fetch search results"}), 500
            
        soup = BeautifulSoup(html_content, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message')  # 保持相同选择器
        
        # 使用统一解析逻辑
        results = []
        for message in messages:
            try:
                if data := parse_message(message):
                    results.append(data)
            except Exception as e:
                print(f"Error parsing message: {str(e)}")
                continue
                
        return jsonify({
            "query": search_query,
            "data": results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"data": "test"})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)

handler = RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler) 