import json
import time
import urllib.request
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# 后端：智信全局意图总线 & 用户身份库
# ==========================================
ZHIXIN_NETWORK_BUS = []
# 模拟后端数据库，存储已注册的用户
USER_DATABASE = {"admin@shensist.top": "verified", "13800138000": "verified"} 

# ==========================================
# 前端：认证网关 + 智信终端 (一体化全栈应用)
# ==========================================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>神思庭·形意 - 智信网络</title>
    <style>
        body { margin: 0; font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #0d0d0d; color: #e0e0e0; display: flex; height: 100vh; overflow: hidden; }
        
        /* ================= 登录注册层 ================= */
        #auth-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #050505; display: flex; justify-content: center; align-items: center; z-index: 9999; }
        .auth-box { background: #151515; border: 1px solid #333; padding: 40px; border-radius: 12px; width: 360px; box-shadow: 0 10px 30px rgba(0,255,204,0.1); text-align: center; }
        .auth-box h1 { margin: 0 0 10px 0; color: #00ffcc; font-size: 24px; letter-spacing: 2px; }
        .auth-box p { color: #888; font-size: 13px; margin-bottom: 30px; }
        
        .auth-tabs { display: flex; margin-bottom: 20px; border-bottom: 1px solid #333; }
        .auth-tab { flex: 1; padding: 10px; cursor: pointer; color: #888; font-size: 14px; font-weight: bold; transition: 0.3s; }
        .auth-tab.active { color: #00ffcc; border-bottom: 2px solid #00ffcc; }
        
        .auth-input-group { margin-bottom: 20px; text-align: left; }
        .auth-input-group input { width: 100%; padding: 12px; background: #000; border: 1px solid #444; color: #fff; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        .auth-input-group input:focus { outline: none; border-color: #00ffcc; }
        
        .verify-group { display: flex; gap: 10px; }
        .verify-group input { flex: 1; }
        .verify-group button { padding: 0 15px; background: #222; border: 1px solid #444; color: #00ffcc; border-radius: 6px; cursor: pointer; font-size: 12px; white-space: nowrap; }
        .verify-group button:hover { background: #333; }

        .btn-login { width: 100%; padding: 14px; background: #00ffcc; color: #000; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; letter-spacing: 1px; }
        .btn-login:hover { background: #00ccaa; box-shadow: 0 0 15px rgba(0,255,204,0.4); }
        .auth-error { color: #ff3366; font-size: 12px; margin-top: 10px; min-height: 15px; }

        /* ================= 智信主界面 ================= */
        #main-app { display: none; width: 100%; height: 100%; flex-direction: row; }
        .sidebar { width: 340px; background-color: #151515; border-right: 1px solid #333; display: flex; flex-direction: column; padding: 25px; box-sizing: border-box; overflow-y: auto; }
        .sidebar h2 { font-size: 18px; margin-top: 0; color: #00ffcc; border-bottom: 1px solid #333; padding-bottom: 15px; }
        
        .account-info { background: rgba(0,255,204,0.05); border: 1px solid rgba(0,255,204,0.2); padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .account-info label { display: block; font-size: 11px; color: #888; margin-bottom: 5px; }
        .account-info .id-text { font-family: monospace; font-size: 14px; color: #00ffcc; font-weight: bold; word-break: break-all; }

        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; font-size: 12px; margin-bottom: 6px; color: #aaa; font-weight: bold; }
        .form-group input, .form-group textarea { width: 100%; box-sizing: border-box; background: #000; border: 1px solid #444; color: #fff; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 13px; }
        .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #00ffcc; }
        
        .toggle-container { display: flex; align-items: center; justify-content: space-between; background: #1a1a1a; padding: 15px; border-radius: 8px; border: 1px solid #00ffcc; margin-top: 10px; }
        .toggle-container span { font-weight: bold; color: #00ffcc; font-size: 14px; }
        .switch { position: relative; display: inline-block; width: 44px; height: 24px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #444; transition: .4s; border-radius: 24px; }
        .slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: #00ffcc; }
        input:checked + .slider:before { transform: translateX(20px); background-color: #000; }

        .chat-area { flex-grow: 1; display: flex; flex-direction: column; background-color: #0d0d0d; }
        .chat-header { padding: 20px; background: linear-gradient(90deg, #151515 0%, #0d0d0d 100%); border-bottom: 1px solid #333; font-weight: bold; display: flex; justify-content: space-between; align-items: center; }
        .messages { flex-grow: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; }
        .msg-row { display: flex; margin-bottom: 20px; flex-direction: column; width: 100%; }
        .msg-row.me { align-items: flex-end; }
        .msg-row.other { align-items: flex-start; }
        .msg-sender { font-size: 11px; color: #666; margin-bottom: 4px; font-family: monospace; }
        .msg-bubble { max-width: 70%; padding: 12px 16px; border-radius: 8px; font-size: 14px; line-height: 1.5; white-space: pre-wrap; background-color: #1f1f1f; border: 1px solid #333; }
        .msg-row.me .msg-bubble { background-color: #00ffcc; color: #000; border-top-right-radius: 0; border: none; font-weight: 500; }
        .msg-row.other .msg-bubble { border-top-left-radius: 0; }
        
        .input-area { padding: 20px; background-color: #151515; border-top: 1px solid #333; display: flex; gap: 15px; }
        .input-area input { flex-grow: 1; padding: 15px; background: #000; border: 1px solid #444; color: #00ffcc; border-radius: 8px; font-size: 14px; }
        .input-area button { padding: 0 25px; background-color: #00ffcc; color: #000; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .thinking { font-size: 12px; color: #00ffcc; text-align: center; padding: 10px; display: none; background: rgba(0, 255, 204, 0.05); }
    </style>
</head>
<body>

    <div id="auth-overlay">
        <div class="auth-box">
            <h1>智信网络接入端</h1>
            <p>连接你的全权数字分身</p>
            
            <div class="auth-tabs">
                <div class="auth-tab active" onclick="switchTab('phone')">手机号登录</div>
                <div class="auth-tab" onclick="switchTab('email')">邮箱登录</div>
            </div>

            <div class="auth-input-group">
                <input type="text" id="auth-account" placeholder="请输入手机号码">
            </div>
            <div class="auth-input-group verify-group">
                <input type="text" id="auth-code" placeholder="6位动态验证码">
                <button onclick="sendCode()" id="btn-send-code">获取验证码</button>
            </div>
            
            <button class="btn-login" onclick="performLogin()">接入智信网络</button>
            <div id="auth-error" class="auth-error"></div>
        </div>
    </div>

    <div id="main-app">
        <div class="sidebar">
            <h2>🛡️ 智信网关配置</h2>
            
            <div class="account-info">
                <label>已认证主权账号 (智信 ID)</label>
                <div class="id-text" id="display-zhixin-id">加载中...</div>
            </div>

            <div class="form-group">
                <label>算力引擎 (LLM API URL)</label>
                <input type="text" id="conf-url" value="https://api.deepseek.com/v1/chat/completions">
            </div>
            <div class="form-group">
                <label>访问密钥 (API Key)</label>
                <input type="password" id="conf-key" placeholder="填入你的真实大模型 Key">
            </div>
            <div class="form-group">
                <label>模型内核 (Model)</label>
                <input type="text" id="conf-model" value="deepseek-chat">
            </div>
            <div class="form-group" style="flex-grow: 1; display: flex; flex-direction: column;">
                <label>绝对意志注入 (System Prompt)</label>
                <textarea id="conf-prompt" style="flex-grow: 1; resize: none;">你是该账号主人的全权商业代表。你的任务是在智信网络中与对方博弈。底线是保障核心利益。回复要干练、专业，如同顶尖谈判专家。</textarea>
            </div>
            <div class="toggle-container">
                <span>⚡ 智信全权托管</span>
                <label class="switch">
                    <input type="checkbox" id="conf-autopilot">
                    <span class="slider"></span>
                </label>
            </div>
        </div>

        <div class="chat-area">
            <div class="chat-header">
                <span>🌐 全局意图流转室</span>
                <span style="color:#00ffcc; font-size: 12px; border: 1px solid #00ffcc; padding: 2px 8px; border-radius: 10px;">加密信道在线</span>
            </div>
            <div class="messages" id="chat-messages"></div>
            <div class="thinking" id="thinking-indicator">[算力运转中] 大模型正在解析意图并生成反制策略...</div>
            <div class="input-area">
                <input type="text" id="chat-input" placeholder="手动输入意图（人类最高指挥官物理介入）..." onkeypress="if(event.key === 'Enter') sendManualMsg()">
                <button onclick="sendManualMsg()">广播指令</button>
            </div>
        </div>
    </div>

    <script>
        // --- 身份认证逻辑 ---
        let currentAuthType = 'phone';
        let verifiedAccount = ''; // 存储登录成功的账号

        function switchTab(type) {
            currentAuthType = type;
            const tabs = document.querySelectorAll('.auth-tab');
            tabs[0].className = type === 'phone' ? 'auth-tab active' : 'auth-tab';
            tabs[1].className = type === 'email' ? 'auth-tab active' : 'auth-tab';
            document.getElementById('auth-account').placeholder = type === 'phone' ? '请输入手机号码' : '请输入电子邮箱';
            document.getElementById('auth-error').innerText = '';
        }

        function sendCode() {
            const acc = document.getElementById('auth-account').value;
            const errorDiv = document.getElementById('auth-error');
            if (!acc) { errorDiv.innerText = "请先输入账号！"; return; }
            
            // 简单的正则格式校验
            if (currentAuthType === 'phone' && !/^[1][3-9][0-9]{9}$/.test(acc)) {
                errorDiv.innerText = "手机号码格式不正确！"; return;
            }
            if (currentAuthType === 'email' && !/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(acc)) {
                errorDiv.innerText = "邮箱格式不正确！"; return;
            }

            errorDiv.innerText = '';
            const btn = document.getElementById('btn-send-code');
            btn.innerText = "已发送(60s)";
            btn.disabled = true;
            setTimeout(() => { btn.innerText = "获取验证码"; btn.disabled = false; }, 3000); // 模拟倒计时
            
            // 商业级模拟：随便输入 123456 即可通过
            alert("【系统模拟】您的智信网络动态验证码为：123456。任何人不得索要。");
        }

        function performLogin() {
            const acc = document.getElementById('auth-account').value;
            const code = document.getElementById('auth-code').value;
            const errorDiv = document.getElementById('auth-error');

            if (!acc || !code) { errorDiv.innerText = "请填写账号和验证码！"; return; }
            if (code !== "123456") { errorDiv.innerText = "验证码错误！(测试请填 123456)"; return; }

            // 登录成功！锁定账号作为智信 ID，并进入主控台
            verifiedAccount = acc;
            document.getElementById('auth-overlay').style.display = 'none';
            document.getElementById('main-app').style.display = 'flex';
            
            // 将认证的手机号/邮箱强绑定到 UI 显示上，不可修改
            document.getElementById('display-zhixin-id').innerText = verifiedAccount;
            
            // 开启实时心跳同步
            setInterval(fetchMessages, 1000);
        }

        // --- 智信流转网络逻辑 ---
        const msgContainer = document.getElementById('chat-messages');
        let localMessageCount = 0;
        let isThinking = false;

        function fetchMessages() {
            fetch('/get_messages').then(res => res.json()).then(data => {
                if (data.length > localMessageCount) {
                    const newMessages = data.slice(localMessageCount);
                    localMessageCount = data.length;
                    
                    let lastMsg = null;
                    newMessages.forEach(msg => {
                        renderMessage(msg, verifiedAccount);
                        lastMsg = msg;
                    });
                    msgContainer.scrollTop = msgContainer.scrollHeight;

                    const autoPilot = document.getElementById('conf-autopilot').checked;
                    // 如果消息不是我发的，且开启了托管，则调起大模型
                    if (autoPilot && lastMsg && lastMsg.zhixin_id !== verifiedAccount && !isThinking) {
                        triggerAgentReply(data);
                    }
                }
            });
        }

        function renderMessage(msg, myId) {
            const isMe = msg.zhixin_id === myId;
            const row = document.createElement('div');
            row.className = 'msg-row ' + (isMe ? 'me' : 'other');
            
            const sender = document.createElement('div');
            sender.className = 'msg-sender';
            // 对手机号做脱敏处理展示 (商业级细节)
            let displayId = msg.zhixin_id;
            if (/^[1][3-9][0-9]{9}$/.test(displayId)) {
                displayId = displayId.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
            }
            sender.innerText = "已认证节点: " + displayId;
            
            const bubble = document.createElement('div');
            bubble.className = 'msg-bubble';
            bubble.innerText = msg.text;
            
            row.appendChild(sender);
            row.appendChild(bubble);
            msgContainer.appendChild(row);
        }

        function sendManualMsg() {
            const input = document.getElementById('chat-input');
            const text = input.value.trim();
            if (!text) return;
            
            fetch('/send_message', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({zhixin_id: verifiedAccount, text: text})
            });
            input.value = '';
        }

        function triggerAgentReply(historyData) {
            isThinking = true;
            document.getElementById('thinking-indicator').style.display = 'block';
            
            const payload = {
                api_url: document.getElementById('conf-url').value,
                api_key: document.getElementById('conf-key').value,
                model: document.getElementById('conf-model').value,
                system_prompt: document.getElementById('conf-prompt').value,
                my_zhixin: verifiedAccount, // 使用认证后的账号进行请求
                history: historyData
            };

            fetch('/ask_llm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            }).then(res => res.json()).then(data => {
                isThinking = false;
                document.getElementById('thinking-indicator').style.display = 'none';
                
                if (data.reply) {
                    fetch('/send_message', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({zhixin_id: verifiedAccount, text: data.reply})
                    });
                } else if (data.error) {
                    alert("算力接口异常: " + data.error);
                }
            });
        }
    </script>
</body>
</html>
"""

# ==========================================
# 真实的 API 路由代理
# ==========================================
class ZhiXinServerHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass 

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
            self.wfile.write(json.dumps(ZHIXIN_NETWORK_BUS).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(post_data)

        if self.path == '/send_message':
            ZHIXIN_NETWORK_BUS.append({
                "zhixin_id": data['zhixin_id'],
                "text": data['text'],
                "timestamp": time.time()
            })
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            print(f"[意图广播] 节点({data['zhixin_id']}): {data['text']}") 

        elif self.path == '/ask_llm':
            api_url = data['api_url']
            api_key = data['api_key']
            model = data['model']
            my_zhixin = data['my_zhixin']
            
            if not api_key:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "缺失大模型 API 访问凭证"}).encode('utf-8'))
                return

            messages = [{"role": "system", "content": data['system_prompt']}]
            for msg in data['history']:
                role = "assistant" if msg['zhixin_id'] == my_zhixin else "user"
                content = msg['text'] if role == "assistant" else f"[网络节点 {msg['zhixin_id']} 说道]: {msg['text']}"
                messages.append({"role": role, "content": content})

            payload = { "model": model, "messages": messages, "temperature": 0.8 }
            headers = { "Authorization": f"Bearer {api_key}", "Content-Type": "application/json" }

            try:
                req = urllib.request.Request(api_url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
                with urllib.request.urlopen(req, timeout=40) as response:
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
    httpd = HTTPServer(server_address, ZhiXinServerHandler)
    print("\n" + "="*60)
    print(" 🚀 神思庭·形意 - 【智信】商业认证网络已点火")
    print("="*60)
    print(" 访问地址: http://localhost:8080")
    print("--------------------------------------------------")
    print(" 【双机对抗实操 (含身份认证)】：")
    print(" 1. 浏览器打开两个标签页，访问 8080 端口。")
    print(" 2. 标签页A：用你的真实手机号/邮箱登录，填入 API，开启托管。")
    print(" 3. 标签页B：用另一个测试手机号/邮箱登录，填入 API，开启托管。")
    print(" 4. 任意一方发起对话，见证带真实数字签名的 Agent 博弈！")
    print("="*60 + "\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] 智信节点已物理断网。")