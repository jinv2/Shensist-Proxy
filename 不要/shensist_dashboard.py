import json
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# 后端：真实的分布式消息总线 (充当暗网/微信服务器)
# ==========================================
# 存储所有聊天记录，格式: {"sender": "神思庭", "text": "你好", "timestamp": 123456}
CHAT_HISTORY = []

# ==========================================
# 前端：商业级 Agent 客户端界面 (HTML/JS/CSS)
# ==========================================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>神思庭·形意 - Web4 客户端</title>
    <style>
        body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #1e1e1e; color: #d4d4d4; display: flex; height: 100vh; overflow: hidden; }
        /* 左侧配置栏 (注入灵魂) */
        .sidebar { width: 320px; background-color: #252526; border-right: 1px solid #3c3c3c; display: flex; flex-direction: column; padding: 20px; box-sizing: border-box; overflow-y: auto; }
        .sidebar h2 { font-size: 18px; margin-top: 0; color: #fff; border-bottom: 1px solid #3c3c3c; padding-bottom: 10px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; font-size: 12px; margin-bottom: 5px; color: #aaa; }
        .form-group input, .form-group textarea { width: 100%; box-sizing: border-box; background: #3c3c3c; border: 1px solid #555; color: #fff; padding: 8px; border-radius: 4px; font-family: inherit; }
        .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #007acc; }
        
        /* 托管开关 */
        .toggle-container { display: flex; align-items: center; justify-content: space-between; background: #2d2d30; padding: 10px; border-radius: 6px; border: 1px solid #007acc; margin-top: 10px; }
        .toggle-container span { font-weight: bold; color: #00ffcc; }
        .switch { position: relative; display: inline-block; width: 40px; height: 20px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 20px; }
        .slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 2px; bottom: 2px; background-color: white; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: #007acc; }
        input:checked + .slider:before { transform: translateX(20px); }

        /* 右侧聊天区 */
        .chat-area { flex-grow: 1; display: flex; flex-direction: column; background-color: #1e1e1e; }
        .chat-header { padding: 15px 20px; background-color: #2d2d30; border-bottom: 1px solid #3c3c3c; font-weight: bold; color: #fff; display: flex; justify-content: space-between;}
        .messages { flex-grow: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; }
        
        .msg-row { display: flex; margin-bottom: 15px; flex-direction: column; }
        .msg-row.me { align-items: flex-end; }
        .msg-row.other { align-items: flex-start; }
        .msg-sender { font-size: 12px; color: #888; margin-bottom: 4px; }
        .msg-bubble { max-width: 70%; padding: 10px 14px; border-radius: 8px; font-size: 14px; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word;}
        .msg-row.me .msg-bubble { background-color: #007acc; color: #fff; border-top-right-radius: 0; }
        .msg-row.other .msg-bubble { background-color: #3c3c3c; color: #d4d4d4; border-top-left-radius: 0; }
        
        .input-area { padding: 15px; background-color: #252526; border-top: 1px solid #3c3c3c; display: flex; gap: 10px; }
        .input-area input { flex-grow: 1; padding: 10px; background: #3c3c3c; border: 1px solid #555; color: #fff; border-radius: 4px; font-size: 14px; }
        .input-area button { padding: 10px 20px; background-color: #007acc; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .input-area button:hover { background-color: #005f9e; }
        
        .thinking { font-size: 12px; color: #00ffcc; text-align: center; margin-bottom: 10px; display: none; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>🛠️ 形意 Agent 客户端配置</h2>
        <div class="form-group">
            <label>我的身份名称 (微信号)</label>
            <input type="text" id="conf-name" value="神思庭本尊">
        </div>
        <div class="form-group">
            <label>大模型 API Base URL</label>
            <input type="text" id="conf-url" value="https://api.deepseek.com/v1/chat/completions" placeholder="如: https://api.openai.com/v1/chat/completions">
        </div>
        <div class="form-group">
            <label>大模型 API Key</label>
            <input type="password" id="conf-key" placeholder="sk-...">
        </div>
        <div class="form-group">
            <label>模型名称 (Model)</label>
            <input type="text" id="conf-model" value="deepseek-chat">
        </div>
        <div class="form-group" style="flex-grow: 1; display: flex; flex-direction: column;">
            <label>系统提示词 (注入灵魂与底线)</label>
            <textarea id="conf-prompt" style="flex-grow: 1; resize: none;">你是神思庭的全权商业代表。你的任务是和群里的其他人谈判，促成合作。你的绝对底线是价格不能低于XXXX。沟通要干练，不卑不亢，必要时使用隐喻。</textarea>
        </div>
        <div class="toggle-container">
            <span>🤖 Agent 全权托管</span>
            <label class="switch">
                <input type="checkbox" id="conf-autopilot">
                <span class="slider"></span>
            </label>
        </div>
    </div>

    <div class="chat-area">
        <div class="chat-header">
            <span>🌐 Web4 全局谈判室 (所有人可见)</span>
            <span id="conn-status" style="color:#00ffcc; font-size:12px;">● 已连接</span>
        </div>
        <div class="messages" id="chat-messages">
            </div>
        <div class="thinking" id="thinking-indicator">正在调用大模型思考对策中...</div>
        <div class="input-area">
            <input type="text" id="chat-input" placeholder="输入你想说的话（人类手动介入）..." onkeypress="if(event.key === 'Enter') sendManualMsg()">
            <button onclick="sendManualMsg()">发送 (接管)</button>
        </div>
    </div>

    <script>
        const msgContainer = document.getElementById('chat-messages');
        let localMessageCount = 0;
        let isThinking = false;

        // 核心循环：每秒向服务器拉取最新消息
        setInterval(fetchMessages, 1000);

        function fetchMessages() {
            fetch('/get_messages')
            .then(res => res.json())
            .then(data => {
                if (data.length > localMessageCount) {
                    const newMessages = data.slice(localMessageCount);
                    localMessageCount = data.length;
                    
                    const myName = document.getElementById('conf-name').value;
                    let lastMsg = null;

                    newMessages.forEach(msg => {
                        renderMessage(msg, myName);
                        lastMsg = msg;
                    });
                    
                    msgContainer.scrollTop = msgContainer.scrollHeight;

                    // 商业核心逻辑：如果最后一条消息不是我发的，且开启了【全权托管】，则触发大模型自动回复
                    const autoPilot = document.getElementById('conf-autopilot').checked;
                    if (autoPilot && lastMsg && lastMsg.sender !== myName && !isThinking) {
                        triggerAgentReply(data); // 传入所有历史记录给大模型
                    }
                }
            });
        }

        function renderMessage(msg, myName) {
            const isMe = msg.sender === myName;
            const row = document.createElement('div');
            row.className = 'msg-row ' + (isMe ? 'me' : 'other');
            
            const sender = document.createElement('div');
            sender.className = 'msg-sender';
            sender.innerText = msg.sender;
            
            const bubble = document.createElement('div');
            bubble.className = 'msg-bubble';
            bubble.innerText = msg.text;
            
            row.appendChild(sender);
            row.appendChild(bubble);
            msgContainer.appendChild(row);
        }

        // 人类手动发送消息
        function sendManualMsg() {
            const input = document.getElementById('chat-input');
            const text = input.value.trim();
            if (!text) return;
            const myName = document.getElementById('conf-name').value;
            
            fetch('/send_message', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({sender: myName, text: text})
            });
            input.value = '';
        }

        // 智能体调用大模型 API 自动回复
        function triggerAgentReply(historyData) {
            isThinking = true;
            document.getElementById('thinking-indicator').style.display = 'block';
            
            // 收集当前客户端的配置
            const payload = {
                api_url: document.getElementById('conf-url').value,
                api_key: document.getElementById('conf-key').value,
                model: document.getElementById('conf-model').value,
                system_prompt: document.getElementById('conf-prompt').value,
                my_name: document.getElementById('conf-name').value,
                history: historyData
            };

            // 发送给后端代理请求真实的大模型 API
            fetch('/ask_llm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                isThinking = false;
                document.getElementById('thinking-indicator').style.display = 'none';
                
                if (data.reply) {
                    // 把大模型生成的话发送到全局聊天室
                    fetch('/send_message', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({sender: payload.my_name, text: data.reply})
                    });
                } else if (data.error) {
                    alert("API 调用失败: " + data.error);
                }
            });
        }
    </script>
</body>
</html>
"""

# ==========================================
# 真实的 API 路由与 LLM 请求处理
# ==========================================
class WechatServerHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass # 保持终端安静

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif self.path == '/get_messages':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(CHAT_HISTORY).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(post_data)

        if self.path == '/send_message':
            # 接收人类或智能体发出的消息，存入全局总线
            CHAT_HISTORY.append({
                "sender": data['sender'],
                "text": data['text'],
                "timestamp": time.time()
            })
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            print(f"[{data['sender']}]: {data['text']}") # 在终端显示以供监控

        elif self.path == '/ask_llm':
            # 核心：真实的 API 请求代理
            api_url = data['api_url']
            api_key = data['api_key']
            model = data['model']
            my_name = data['my_name']
            
            if not api_key:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "请在左侧输入大模型 API Key"}).encode('utf-8'))
                return

            # 构建真实的 OpenAI 格式的上下文
            messages = [{"role": "system", "content": data['system_prompt']}]
            for msg in data['history']:
                role = "assistant" if msg['sender'] == my_name else "user"
                # 提示大模型这是谁发的话
                content = msg['text'] if role == "assistant" else f"[{msg['sender']}说]: {msg['text']}"
                messages.append({"role": role, "content": content})

            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            try:
                # 真实的网络请求！直接向你配置的大模型发起 POST
                req = urllib.request.Request(api_url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
                with urllib.request.urlopen(req, timeout=30) as response:
                    res_body = json.loads(response.read().decode('utf-8'))
                    reply_text = res_body['choices'][0]['message']['content']
                    
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"reply": reply_text}).encode('utf-8'))
            except Exception as e:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, WechatServerHandler)
    print("==================================================")
    print(" 🚀 神思庭·形意 - 真实商业版 Agent 微信服务端运行中")
    print("==================================================")
    print(" 请打开浏览器访问: http://localhost:8080")
    print("\n [双机对抗测试方法]：")
    print(" 1. 在浏览器打开两个 http://localhost:8080 标签页")
    print(" 2. 标签页A 配置为【神思庭】，填入你的API Key，打开【全权托管】")
    print(" 3. 标签页B 配置为【客户】，可以填入另一个API Key和人设，打开【全权托管】")
    print(" 4. 任意一方发送一句'你好'，真实的 LLM 对抗谈判将立即自动开始！")
    print("==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已关闭。")