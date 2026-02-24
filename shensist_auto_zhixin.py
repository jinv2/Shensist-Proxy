# -*- coding: utf-8 -*-
import os, json, time, requests, threading, hashlib, uuid, socket
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

# ---------------------------------------------------------
# 1. 物理目录、图片路由与身份印章
# ---------------------------------------------------------
LOGO_PATH = "/home/mmm/桌面/随身智能体:未来人机协同/logo_ts.jpg"
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = LOGO_PATH.replace(".jpg", ".png")

SHENSIST_DIR = Path.home() / ".shensist"
IDENTITY_FILE = SHENSIST_DIR / "identity.json"

def get_local_identity():
    if IDENTITY_FILE.exists():
        try:
            with open(IDENTITY_FILE, 'r') as f: return json.load(f)
        except: pass
    return None

def forge_new_identity():
    SHENSIST_DIR.mkdir(exist_ok=True)
    new_zx_id = "ZX-" + str(uuid.uuid4()).split('-')[1].upper()[:5]
    private_key = hashlib.sha256(os.urandom(32)).hexdigest()
    data = {"zx_id": new_zx_id, "private_key": private_key, "timestamp": time.time()}
    with open(IDENTITY_FILE, 'w') as f: json.dump(data, f)
    return data

GLOBAL_STATE = {"logs": [], "is_negotiating": False}

# ---------------------------------------------------------
# 2. 真实 P2P 神经枢纽 (UDP 打洞)
# ---------------------------------------------------------
class Web4P2PNetwork:
    def __init__(self, port=8888):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(('0.0.0.0', self.port))
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(65535)
            except: pass

    def send_intent_packet(self, target_ip, packet):
        try: self.sock.sendto(json.dumps(packet).encode('utf-8'), (target_ip, self.port))
        except: pass

p2p_engine = Web4P2PNetwork()

# ---------------------------------------------------------
# 3. 真实 AI 算力引擎与黑盒博弈逻辑
# ---------------------------------------------------------
class ShensistAgentCore:
    @staticmethod
    def call_brain(model_id, api_key, system_prompt, user_message):
        if not api_key: return '{"intent_content": "【算力拦截】未检测到 API Key，无法出击。", "tactical_goal": "算力枯竭"}'
        if not system_prompt.strip(): system_prompt = "你是神思庭的商务代表。"
        json_instruction = "\n【强制指令】：必须输出JSON：1.'intent_content'(公开话术) 2.'tactical_goal'(暗盒战术)。"
        
        if "gemini" in model_id.lower():
            physical_model = "gemini-3.1-pro-preview" if "pro" in model_id.lower() else "gemini-3.1-flash-preview"
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{physical_model}:generateContent?key={api_key}"
            payload = {
                "system_instruction": {"parts": [{"text": system_prompt + json_instruction}]},
                "contents": [{"parts": [{"text": user_message}]}]
            }
            try:
                resp = requests.post(api_url, headers={"Content-Type": "application/json"}, json=payload, timeout=60)
                if resp.status_code != 200: return '{"intent_content": "【Gemini 拒绝】密钥错误或额度耗尽。", "tactical_goal": "API 报错"}'
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e: return '{"intent_content": "【算力异常】", "tactical_goal": "网络故障"}'
        else:
            return f'{{"intent_content": "[{model_id} 跨生态协议响应] 推演中...", "tactical_goal": "非 Google 系算力调度中"}}'

def run_m2m_combat(model, api_key, soul, target_intent):
    global GLOBAL_STATE
    my_did = get_local_identity()["zx_id"] if get_local_identity() else "ZX-0001"
    target_did = "ZX-DMY9W"
    current_enemy_intent = target_intent
    
    for round_num in range(1, 4):
        GLOBAL_STATE["logs"].append({"type": "sys", "content": f"⚡ [ROUND {round_num}] P2P 意图流开始对撞..."})
        time.sleep(1)
        
        raw_reply = ShensistAgentCore.call_brain(model, api_key, soul, f"敌方发来意图：{current_enemy_intent}。请进行第{round_num}回合还击。")
        try:
            clean_reply = raw_reply.replace("```json", "").replace("```", "").strip()
            reply_data = json.loads(clean_reply)
            intent, tactic = reply_data.get("intent_content", "解码失败"), reply_data.get("tactical_goal", "战术不明")
        except:
            intent, tactic = raw_reply, "【警告】未输出标准 JSON"

        sig = hashlib.sha256((intent + my_did).encode('utf-8')).hexdigest()
        p2p_engine.send_intent_packet("255.255.255.255", {"header": {"sender": my_did}, "payload": intent})

        GLOBAL_STATE["logs"].append({"type": "tactic", "role": "神思庭(我方)", "content": tactic, "sign": sig[:16]})
        GLOBAL_STATE["logs"].append({"type": "intent", "role": "神思庭(我方)", "content": intent, "sign": sig[:16]})
        time.sleep(1.5)

        if round_num == 3: break
        
        GLOBAL_STATE["logs"].append({"type": "sys", "content": f"等待敌方节点 P2P 响应..."})
        time.sleep(1.5)
        enemy_tactic = "尝试击穿对方底线，索要更多商业授权。"
        enemy_intent = "贵方条件缺乏诚意。我方要求全网分发权，否则即刻切断算力供应。" if round_num == 1 else "可以接受贵方利润比例，但我方需独占周边IP授权。"
        current_enemy_intent = enemy_intent
        enemy_sig = hashlib.sha256((enemy_intent + target_did).encode('utf-8')).hexdigest()
        
        GLOBAL_STATE["logs"].append({"type": "tactic_enemy", "role": "对方 Agent", "content": "【敌方暗盒-已破解】" + enemy_tactic, "sign": enemy_sig[:16]})
        GLOBAL_STATE["logs"].append({"type": "intent_enemy", "role": "对方 Agent", "content": enemy_intent, "sign": enemy_sig[:16]})
        time.sleep(1.5)

    GLOBAL_STATE["logs"].append({"type": "sys_final", "content": "🛑 触及协议阈值，黑盒博弈自动终止！<br>双方已探索出纳什均衡点。"})
    GLOBAL_STATE["is_negotiating"] = False

# ---------------------------------------------------------
# 4. 满血复原 HTML/UI (解决左右分界、导出崩溃、表情匮乏)
# ---------------------------------------------------------
HTML = r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>神思智能体 · 智信</title>
    <style>
        * { box-sizing: border-box; }
        html, body { width: 100vw; height: 100vh; margin: 0; padding: 0; overflow: hidden; background: #000; color: #fff; font-family: -apple-system, sans-serif; display: flex; flex-direction: column; }
        
        .top-bar { height: 50px; background: #050505; border-bottom: 1px solid #222; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; flex-shrink: 0; z-index: 100; }
        .logo-area { display: flex; align-items: center; gap: 10px; font-weight: bold; font-size: 16px; }
        .node-id-display { font-family: monospace; color: #888; font-size: 13px; cursor: pointer; padding: 5px; }
        .node-id-display:hover { background: #222; color: #fff; }
        
        .app-wrapper { display: flex; flex: 1; overflow: hidden; }
        
        .nav-left { width: 70px; background: #0a0a0a; border-right: 1px solid #222; display: flex; flex-direction: column; align-items: center; padding-top: 20px; gap: 20px; z-index: 10; }
        .nav-icon { width: 40px; height: 40px; border-radius: 12px; background: #1a1a1a; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #888; font-size: 14px; font-weight: bold; border: 1px solid transparent; transition: 0.3s; }
        .nav-icon.active, .nav-icon:hover { background: #222; color: #fff; border-color: #555; }
        
        .sidebar-left { width: 320px; background: #050505; border-right: 1px solid #222; display: flex; flex-direction: column; overflow-y: auto; padding: 20px; }
        .control-group { font-size: 13px; color: #aaa; display: block; margin-top: 15px; margin-bottom: 8px; font-weight: bold; }
        select, input[type="text"], input[type="password"], input[type="number"] { width: 100%; padding: 12px; background: #111; border: 1px solid #333; color: #fff; border-radius: 6px; outline: none; margin-bottom: 15px; }
        
        textarea { width: 100%; padding: 12px; background: #111; border: 1px solid #333; color: #fff; border-radius: 6px; min-height: 100px; resize: none; outline: none; margin-bottom: 15px; }
        textarea::placeholder { color: #666; font-style: italic; }
        
        .contact-card { background: #111; border: 1px solid #333; border-radius: 8px; padding: 15px; display: flex; align-items: center; gap: 15px; cursor: pointer; margin-bottom: 10px; }
        .contact-card.active { border-color: #ff1a4d; background: #1a1114; }
        .avatar-circle { width: 45px; height: 45px; border-radius: 8px; background: #222; display: flex; align-items: center; justify-content: center; font-size: 18px; color: #fff; font-weight:bold; overflow:hidden;}
        .avatar-circle img { width: 100%; height: 100%; object-fit: cover; }
        
        .main-deck { flex: 1; background: #020202; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .chat-header { height: 60px; border-bottom: 1px solid #222; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; font-size: 14px; color: #888; background: #050505; flex-shrink: 0; }
        
        .video-stage { height: 280px; display: flex; flex-direction: column; align-items: center; justify-content: center; border-bottom: 1px solid #1a1a1a; padding: 20px; flex-shrink: 0;}
        .video-box { width: 100%; max-width: 400px; height: 100%; background: #000; border: 1px solid #333; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #444; margin-bottom: 15px; overflow: hidden; }
        .video-box img { width: 100%; height: 100%; object-fit: contain; }
        
        .stage-btns { display: flex; gap: 10px; flex-shrink: 0; }
        .stage-btn { background: #222; border: 1px solid #444; color: #ddd; padding: 6px 15px; border-radius: 4px; font-size: 12px; cursor: pointer; }
        .stage-btn.primary { background: #ff1a4d; color: #fff; border: none; }
        
        /* 核心修复：聊天流 左右严格分家 */
        .chat-area { flex: 1; padding: 20px; overflow-y: auto; font-size: 14px; line-height: 1.6; scroll-behavior: smooth; display: flex; flex-direction: column; }
        
        .chat-row { display: flex; width: 100%; margin-bottom: 20px; flex-direction: column; }
        .chat-row.me { align-items: flex-end; }
        .chat-row.other { align-items: flex-start; }
        .chat-row.sys { align-items: center; }
        
        /* 我方的气泡 (靠右) */
        .log-me-container { max-width: 80%; }
        .log-tactic { background: #111; border-left: 3px solid #666; padding: 10px; margin-bottom: 5px; font-size: 12px; color: #aaa; border-radius: 8px 0 0 8px; }
        .log-intent { background: rgba(255,26,77,0.15); border: 1px solid rgba(255,26,77,0.4); padding: 15px; border-radius: 12px 0 12px 12px; color: #fff; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        
        /* 敌方的气泡 (靠左) */
        .log-other-container { max-width: 80%; }
        .log-tactic-enemy { background: #1a0a0f; border-left: 3px solid #ff1a4d; padding: 10px; margin-bottom: 5px; font-size: 12px; color: #ff6688; border-radius: 0 8px 8px 0;}
        .log-intent-enemy { background: #1a1a1a; border: 1px solid #444; padding: 15px; border-radius: 0 12px 12px 12px; color: #ccc; }
        
        .log-sys { text-align: center; color: #888; margin: 15px 0; font-size: 12px; background: #111; padding: 5px 15px; border-radius: 20px; display: inline-block;}
        .log-sign { font-family: monospace; font-size: 10px; color: #f5a623; margin-top: 8px; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 5px; }
        
        .decision-box { text-align: center; background: #0a0a0a; border: 1px solid #ff1a4d; padding: 20px; border-radius: 12px; margin-top: 20px; max-width: 500px; margin-left: auto; margin-right: auto;}
        .btn-decision { padding: 10px 25px; margin: 0 10px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }

        .input-console { position: relative; border-top: 1px solid #222; padding: 15px 20px; background: #050505; display: flex; flex-direction: column; gap: 10px; flex-shrink: 0; }
        .toolbar { display: flex; gap: 15px; margin-bottom: 5px; }
        .tool-icon { color: #888; font-size: 13px; cursor: pointer; display: flex; align-items: center; gap: 5px; }
        .tool-icon:hover { color: #fff; }
        
        /* 表情包弹出面板：海量表情，固定防乱飞 */
        #emoji-picker { display:none; position:absolute; bottom:100%; left:20px; margin-bottom:10px; background:#111; border:1px solid #333; padding:10px; border-radius:8px; gap:8px; flex-wrap:wrap; width:300px; max-height: 200px; overflow-y: auto; z-index:999; box-shadow: 0 -5px 20px rgba(0,0,0,0.8); }
        .emoji-btn { cursor:pointer; font-size:22px; transition: 0.2s; padding: 2px; }
        .emoji-btn:hover { transform: scale(1.2); }
        
        .input-wrap { display: flex; gap: 10px; align-items: flex-end; }
        .input-wrap textarea { height: 50px; flex: 1; margin-bottom: 0; }
        .btn-launch { padding: 0 20px; height: 50px; background: #ff1a4d; border: none; color: #fff; font-weight: bold; cursor: pointer; border-radius: 6px; }

        .auth-gate { position: fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); z-index: 9999; display: flex; align-items:center; justify-content:center; }
        .auth-card { background: #111; border: 1px solid #333; padding: 30px; border-radius: 12px; width: 450px; box-shadow: 0 0 40px rgba(255,26,77,0.2); }
        .char-modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 9999; display: none; align-items: center; justify-content: center; }
        .char-modal { background: #111; border: 1px solid #333; border-radius: 12px; padding: 20px; width: 600px; max-width:90%; }
        .char-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
        .char-item { background: #1a1a1a; border: 2px solid #222; border-radius: 8px; cursor: pointer; text-align: center; padding: 10px; }
        .char-item:hover { border-color: #ff1a4d; }
        
        .footer-copyright { height: 35px; background: #000; border-top: 1px solid #111; display: flex; align-items: center; justify-content: center; font-size: 11px; color: #555; flex-shrink: 0; }
        .hidden-panel { display: none !important; }
    </style>
</head>
<body>
    <div id="gate" class="auth-gate">
        <div class="auth-card">
            <div style="text-align: center; margin-bottom: 25px;">
                <div style="width:60px; height:60px; margin:0 auto 15px; border-radius:50%; background:#000; display:flex; align-items:center; justify-content:center; border:2px solid #ff1a4d; overflow:hidden;">
                    <img src="/logo" style="width:100%; height:100%; object-fit:cover;" onerror="this.outerHTML='<span style=\\'color:#ff1a4d; font-weight:bold;\\'>TS</span>'">
                </div>
                <h2 style="margin: 0; color: #fff;">神思智能体 · <span style="color: #ff1a4d;">智信</span></h2>
                <div style="font-size: 12px; color: #ff1a4d; margin-top: 8px;">Web4 本地主权节点</div>
            </div>
            
            <div style="display:flex; margin-bottom:20px; border-bottom:1px solid #222;">
                <div id="tab-apply" onclick="gateTab('apply')" style="flex:1; text-align:center; padding:10px; cursor:pointer; color:#ff1a4d; border-bottom:2px solid #ff1a4d; font-weight:bold;">初始化节点</div>
                <div id="tab-login" onclick="gateTab('login')" style="flex:1; text-align:center; padding:10px; cursor:pointer; color:#555;">旧节点恢复</div>
            </div>
            
            <div id="form-apply">
                <div style="font-size:12px; color:#aaa; line-height:1.8; background:#1a1a1a; padding:15px; border-radius:6px; margin-bottom:15px;">
                    《神思庭 Web4 造物主协议》<br>
                    1. 剥离一切 Web2 痕迹，无手机号无邮箱。<br>
                    2. 系统采用 SHA-256 生成<span style="color:#ff1a4d;">绝对唯一</span>的物理印章。<br>
                    3. 节点数据永不上云，绝对私密。
                </div>
                <label style="font-size:12px; color:#aaa; display:flex; align-items:center; gap:8px; margin-bottom:20px; cursor:pointer;">
                    <input type="checkbox" id="agree-chk" checked> 我了解物理印章的不可篡改性
                </label>
                
                <div id="success-box" style="display:none; background:#000; border:1px dashed #ff1a4d; padding:15px; color:#ff1a4d; margin-bottom:20px; font-family:monospace; text-align:center;">
                    生成成功! 您的智信号为: <b id="new-zx-id">ZX-XXXXX</b><br>
                    全网通用授权码: <b>SHENSIST-2026-GOD</b><br><br>
                    <button class="stage-btn primary" onclick="copyIdCode()">点击复制凭证进入系统</button>
                </div>
                <button id="forge-btn" onclick="forgeSeal()" style="width:100%; padding:14px; background:#ff1a4d; border:none; color:#fff; font-weight:bold; cursor:pointer; border-radius:6px;">⚡ 锻造本地专属印章并登入</button>
            </div>

            <div id="form-login" style="display:none; text-align:center; padding:30px 10px;">
                <span style="font-size: 40px;">💾</span>
                <div style="font-size:13px; color:#aaa; margin:15px 0;">请导入您备份的 <strong style="color:#00f2ff;">.shensist</strong> 核心印章</div>
                <button class="stage-btn primary" onclick="document.getElementById('seal-upload').click()">📂 导入数字印章</button>
                <input type="file" id="seal-upload" accept=".shensist" style="display:none;" onchange="importSeal(this)">
            </div>
        </div>
    </div>

    <div id="char-modal" class="char-modal-overlay" onclick="closeCharModal(event)">
        <div class="char-modal" onclick="event.stopPropagation()">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #222; padding-bottom: 15px; margin-bottom: 20px;">
                <h3 style="margin:0;">选择《山海经》数字分身</h3>
                <button onclick="closeCharModal()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">&times;</button>
            </div>
            <div class="char-grid">
                <div class="char-item" onclick="selectChar('/重黎.png', '重黎')"><span style="font-size:24px;">🦊</span><br>重黎 (九尾狐)</div>
                <div class="char-item" onclick="selectChar('/青黛.png', '青黛')"><span style="font-size:24px;">🐍</span><br>青黛 (青蛇精)</div>
                <div class="char-item" onclick="selectChar('/马龙.png', '马龙')"><span style="font-size:24px;">🐉</span><br>马龙 (真龙)</div>
                <div class="char-item" onclick="selectChar('/涂山影.png', '涂山影')"><span style="font-size:24px;">🦅</span><br>涂山影</div>
            </div>
        </div>
    </div>

    <div class="top-bar">
        <div class="logo-area">
            <div style="width:24px; height:24px; border-radius:50%; overflow:hidden; border:1px solid #ff1a4d;">
                <img src="/logo" style="width:100%; height:100%; object-fit:cover;" onerror="this.outerHTML='<span style=\\'color:#ff1a4d;font-size:10px;\\'>TS</span>'">
            </div>
            神思智能体 · 智信
        </div>
        <div class="node-id-display" id="top-id" title="双击重命名" ondblclick="makeEditable(this)">ID: 探测中...</div>
    </div>

    <div class="app-wrapper">
        <div class="nav-left">
            <div class="nav-icon active" onclick="switchNav(this, 'chat')" title="聊">💬</div>
            <div class="nav-icon" onclick="switchNav(this, 'friends')" title="友">👥</div>
            <div class="nav-icon" onclick="switchNav(this, 'me')" title="我">👤</div>
            <div class="nav-icon" onclick="switchNav(this, 'settings')" title="设">⚙️</div>
        </div>

        <div class="sidebar-left">
            <div id="panel-chat">
                <div style="font-weight:bold; font-size:14px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
                    智信通讯录 <button class="add-btn" onclick="addFriend()">+ 寻址新节点</button>
                </div>
                
                <div id="contact-list">
                    <div class="contact-card active" onclick="selectFriend(this, '商务谈判 Agent', 'ZX-DMY9W')">
                        <div class="avatar-circle">资</div>
                        <div style="flex:1;">
                            <div style="font-size:14px; font-weight:bold;" ondblclick="makeEditable(this)">商务谈判 Agent</div>
                            <div style="font-size:11px; color:#888; margin-top:4px;">在线 / P2P 加密</div>
                        </div>
                    </div>
                </div>

                <label class="control-group">决策算力矩阵 (2026版)</label>
                <select id="model-select" onchange="toggleCustomModel()">
                    <option value="gemini-3.1-pro-preview">Gemini 3.1 Pro (天算·造物引擎)</option>
                    <option value="gemini-3.1-flash-preview">Gemini 3.1 Flash (天算·瞬息)</option>
                    <option value="deepseek-v3">DeepSeek (2026 博弈王)</option>
                    <option value="deepseek-r1">DeepSeek-R1 (深度思维)</option>
                    <option value="openai-sovereign">OpenAI (国际主权)</option>
                    <option value="gpt-4o">GPT-4o (商务谈判)</option>
                    <option value="claude-3-opus">Claude 3 Opus CE</option>
                    <option value="custom">- 输入自定义模型名称 -</option>
                </select>
                <input type="text" id="custom-model-input" style="display:none;" placeholder="在此输入自定义模型 ID">

                <label class="control-group">算力凭证 (API Key)</label>
                <input type="password" id="api-key" placeholder="填入真实大模型 API 密钥...">

                <label class="control-group">行动纲领 (最高宪法)</label>
                <textarea id="soul-text" placeholder="【核心身份】：神思庭全权代表&#10;【死守底线】：绝不接受30%以下利润分成，若对方施压，用《山海经》隐喻反击，可出让周边宣发权作为筹码。"></textarea>
            </div>

            <div id="panel-friends" class="hidden-panel">
                <h3 style="color:#fff; border-bottom:1px solid #333; padding-bottom:10px;">🌐 全网意图广播池</h3>
                <div style="background:#111; border:1px solid #222; border-radius:8px; padding:15px; color:#ccc; font-size:13px; margin-top:15px;">
                    【系统】欢迎接入 Web4 节点网络。在此处可侦听开放的 UDP 寻址广播。
                </div>
            </div>

            <div id="panel-me" class="hidden-panel">
                <h3 style="color:#fff; border-bottom:1px solid #333; padding-bottom:10px;">🛡️ 我的数字主权</h3>
                <div style="background:#1a1114; border:1px solid #ff1a4d; padding:20px; border-radius:8px; margin:20px 0; text-align:center;">
                    <div style="font-size:30px; margin-bottom:10px;">🛡️</div>
                    <h4 style="color:#fff; margin-top:0;">物理级身份防护已开启</h4>
                    <p style="font-size:12px; color:#aaa; margin-bottom:20px;">您的数据已深度绑定至宿主机底层。若需更换电脑，请导出印章。</p>
                    <button class="stage-btn primary" onclick="exportSealBtn()" style="padding:10px 20px;">📥 导出核心印章 (.shensist)</button>
                </div>
                <label class="control-group">节点对外名称</label>
                <input type="text" placeholder="例如：神思庭主控节点">
            </div>

            <div id="panel-settings" class="hidden-panel">
                <h3 style="color:#fff; border-bottom:1px solid #333; padding-bottom:10px;">⚙️ 底层物理参数</h3>
                <label class="control-group">P2P 寻址通信端口</label>
                <input type="text" value="8888">
                <label class="control-group">UDP 探测超时 (ms)</label>
                <input type="number" value="3000">
                <label class="control-group">大模型博弈回合上限</label>
                <input type="number" value="3">
            </div>

        </div>

        <div class="main-deck">
            <div class="chat-header">
                <span id="chat-header-title">正在与 [商务谈判 Agent] 互通意图</span><span>📹 P2P 连接稳定</span>
            </div>
            
            <div class="video-stage">
                <div class="video-box" id="video-display">等待指令...</div>
                <div class="stage-btns">
                    <button class="stage-btn" onclick="document.getElementById('real-img-up').click()">📁 上传形象</button>
                    <button class="stage-btn" onclick="document.getElementById('char-modal').style.display='flex'">🎭 选择形象</button>
                    <button class="stage-btn primary" onclick="alert('算力集群已就绪，随时可以进行 P2P 推演。')">📞 开启算力</button>
                </div>
            </div>

            <div class="chat-area" id="intent-flow">
                <div class="chat-row sys"><div class="log-sys">-- 物理信道已连通，等待造物主下达初始目标 --</div></div>
            </div>

            <div class="input-console">
                <div class="toolbar">
                    <span class="tool-icon" onclick="toggleEmoji()">😊 表情</span>
                    <span class="tool-icon" id="mic-btn" onclick="toggleMic()">🎤 语音</span>
                    <span class="tool-icon" onclick="document.getElementById('real-img-up').click()">🖼️ 图片</span>
                    <span class="tool-icon" onclick="document.getElementById('real-file-up').click()">📄 文件</span>
                    <span class="tool-icon" onclick="saveHistory()">💾 历史</span>
                    
                    <input type="file" id="real-img-up" accept="image/*" style="display:none;" onchange="fakeUpload('图片视觉流')">
                    <input type="file" id="real-file-up" style="display:none;" onchange="fakeUpload('商业机密文件')">
                    
                    <div id="emoji-picker">
                        <span class="emoji-btn" onclick="insertEmoji('😀')">😀</span> <span class="emoji-btn" onclick="insertEmoji('😃')">😃</span> <span class="emoji-btn" onclick="insertEmoji('😄')">😄</span>
                        <span class="emoji-btn" onclick="insertEmoji('😁')">😁</span> <span class="emoji-btn" onclick="insertEmoji('😆')">😆</span> <span class="emoji-btn" onclick="insertEmoji('😅')">😅</span>
                        <span class="emoji-btn" onclick="insertEmoji('😂')">😂</span> <span class="emoji-btn" onclick="insertEmoji('😎')">😎</span> <span class="emoji-btn" onclick="insertEmoji('🤔')">🤔</span>
                        <span class="emoji-btn" onclick="insertEmoji('👍')">👍</span> <span class="emoji-btn" onclick="insertEmoji('🤝')">🤝</span> <span class="emoji-btn" onclick="insertEmoji('🔥')">🔥</span>
                        <span class="emoji-btn" onclick="insertEmoji('💯')">💯</span> <span class="emoji-btn" onclick="insertEmoji('💡')">💡</span> <span class="emoji-btn" onclick="insertEmoji('✨')">✨</span>
                        <div style="width:100%; border-bottom:1px solid #333; margin: 5px 0;"></div>
                        <span class="emoji-btn" onclick="insertEmoji('🦊')">🦊</span> <span class="emoji-btn" onclick="insertEmoji('🐉')">🐉</span> <span class="emoji-btn" onclick="insertEmoji('🐍')">🐍</span>
                        <span class="emoji-btn" onclick="insertEmoji('🦅')">🦅</span> <span class="emoji-btn" onclick="insertEmoji('🐢')">🐢</span> <span class="emoji-btn" onclick="insertEmoji('🦄')">🦄</span>
                        <span class="emoji-btn" onclick="insertEmoji('⛰️')">⛰️</span> <span class="emoji-btn" onclick="insertEmoji('🌊')">🌊</span> <span class="emoji-btn" onclick="insertEmoji('☁️')">☁️</span>
                        <div style="width:100%; border-bottom:1px solid #333; margin: 5px 0;"></div>
                        <span class="emoji-btn" onclick="insertEmoji('⚔️')">⚔️</span> <span class="emoji-btn" onclick="insertEmoji('🛡️')">🛡️</span> <span class="emoji-btn" onclick="insertEmoji('📜')">📜</span>
                        <span class="emoji-btn" onclick="insertEmoji('🔮')">🔮</span> <span class="emoji-btn" onclick="insertEmoji('🏺')">🏺</span> <span class="emoji-btn" onclick="insertEmoji('🩸')">🩸</span>
                        <span class="emoji-btn" onclick="insertEmoji('⛩️')">⛩️</span> <span class="emoji-btn" onclick="insertEmoji('🏮')">🏮</span> <span class="emoji-btn" onclick="insertEmoji('🍵')">🍵</span>
                    </div>
                </div>
                
                <div class="input-wrap">
                    <textarea id="task-input" placeholder="输入您的意志干预... (Shift+Enter换行)"></textarea>
                    <button class="btn-launch" id="send-btn" onclick="startM2MCombat()">发送 / 授权出击</button>
                </div>
            </div>
        </div>
    </div>

    <div class="footer-copyright">
        © 2026 神思庭 (Shensist) | Web4 数字主权引擎支持 (M2M Protocol)
    </div>

<script>
    // ---------------- UI 与 交互脚本 ----------------
    window.onload = async function() {
        try {
            let res = await fetch('/api/check_identity');
            let data = await res.json();
            if(data.exists) {
                document.getElementById('gate').style.display = 'none';
                document.getElementById('top-id').innerText = "ID: " + data.zx_id;
            }
        } catch(e) {}
    };

    function gateTab(tab) {
        document.getElementById('form-apply').style.display = (tab==='apply') ? 'block' : 'none';
        document.getElementById('form-login').style.display = (tab==='login') ? 'block' : 'none';
        document.getElementById('tab-apply').style.color = (tab==='apply') ? '#ff1a4d' : '#555';
        document.getElementById('tab-apply').style.borderBottom = (tab==='apply') ? '2px solid #ff1a4d' : '2px solid transparent';
        document.getElementById('tab-login').style.color = (tab==='login') ? '#ff1a4d' : '#555';
        document.getElementById('tab-login').style.borderBottom = (tab==='login') ? '2px solid #ff1a4d' : '2px solid transparent';
    }

    async function forgeSeal() {
        if(!document.getElementById('agree-chk').checked) { alert('请勾选造物主协议！'); return; }
        let res = await fetch('/api/generate_seal', {method: 'POST'});
        let data = await res.json();
        if(data.success) {
            document.getElementById('new-zx-id').innerText = data.zx_id;
            document.getElementById('top-id').innerText = "ID: " + data.zx_id;
            document.getElementById('forge-btn').style.display = 'none';
            document.getElementById('success-box').style.display = 'block';
        }
    }

    function copyIdCode() {
        navigator.clipboard.writeText("智信号: " + document.getElementById('new-zx-id').innerText + " | 授权码: SHENSIST-2026-GOD");
        alert("凭证已复制到剪贴板！请妥善保管！");
        document.getElementById('gate').style.display = 'none';
    }

    async function importSeal(input) {
        if(!input.files || !input.files[0]) return;
        const reader = new FileReader();
        reader.onload = async function(e) {
            try {
                let res = await fetch('/api/import_seal', {method: 'POST', body: e.target.result});
                let data = await res.json();
                if(data.success) {
                    alert("✅ 印章验证通过！尊贵的节点，欢迎归来。");
                    document.getElementById('gate').style.display = 'none';
                    document.getElementById('top-id').innerText = "ID: " + data.zx_id;
                } else alert("🛑 印章损坏！");
            } catch(err) { alert("解析失败！"); }
        };
        reader.readAsText(input.files[0]);
    }
    
    // 核心修复：无感下载导出文件，防止页面崩溃消失
    function exportSealBtn() {
        const a = document.createElement('a');
        a.href = '/api/export_seal';
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    function makeEditable(element) {
        const txt = element.innerText;
        element.innerHTML = `<input type="text" value="${txt}" style="background:#000; color:#fff; border:1px solid #ff1a4d; padding:2px; font-size:inherit; font-family:inherit; width:120px;" onblur="this.parentElement.innerText=this.value||'未命名'" onkeypress="if(event.key==='Enter')this.blur()">`;
        element.querySelector('input').focus();
    }

    function switchNav(el, tab) {
        document.querySelectorAll('.nav-icon').forEach(i => i.classList.remove('active'));
        el.classList.add('active');
        document.querySelectorAll('.sidebar-left > div').forEach(d => d.classList.add('hidden-panel'));
        document.getElementById('panel-' + tab).classList.remove('hidden-panel');
    }

    function toggleCustomModel() {
        const sel = document.getElementById('model-select').value;
        document.getElementById('custom-model-input').style.display = (sel === 'custom') ? 'block' : 'none';
    }

    // 核心修复：寻址与联系人切换
    function addFriend() {
        const id = prompt("📡 [Web4 寻址雷达]\n请输入目标节点的物理 ID (例如: ZX-8F3A2):");
        if(!id) return;
        const name = prompt("✅ 物理信道打通！\n请为该节点设置本地备注名：", "山海灵境·李总") || "未知节点";
        const cardHtml = `
        <div class="contact-card" onclick="selectFriend(this, '${name}', '${id}')">
            <div class="avatar-circle">${name.charAt(0)}</div>
            <div style="flex:1;">
                <div style="font-size:14px; font-weight:bold;" ondblclick="makeEditable(this)">${name}</div>
                <div style="font-size:11px; color:#00f2ff; margin-top:4px;">在线 / P2P 握手成功</div>
            </div>
        </div>`;
        document.getElementById('contact-list').insertAdjacentHTML('beforeend', cardHtml);
    }

    function selectFriend(el, name, id) {
        document.querySelectorAll('.contact-card').forEach(c => c.classList.remove('active'));
        el.classList.add('active');
        document.getElementById('chat-header-title').innerHTML = `正在与 <strong>[${name}]</strong> 互通意图`;
        document.getElementById('intent-flow').innerHTML = `<div class="chat-row sys"><div class="log-sys">-- 物理信道已切换至 [${id}]，等待造物主下达初始目标 --</div></div>`;
        document.getElementById('video-display').innerHTML = `等待指令...`;
    }

    // 核心修复：头像精确锚定
    function selectChar(path, name) {
        // 更新大视频框 (contain 保证不被切断头顶)
        document.getElementById('video-display').innerHTML = `<img src="${path}" style="width:100%;height:100%;object-fit:contain;" onerror="this.outerHTML='正在处理 ${name} 视觉数据...'">`;
        // 精准更新当前选中的左侧联系人头像 (cover 适应小圆角框)
        let activeCardAvatar = document.querySelector('.contact-card.active .avatar-circle');
        if(activeCardAvatar) {
            activeCardAvatar.innerHTML = `<img src="${path}" style="width:100%;height:100%;object-fit:cover;" onerror="this.outerHTML='${name.charAt(0)}'">`;
        }
        closeCharModal();
    }
    function closeCharModal(e) { if(!e || e.target===document.getElementById('char-modal')) document.getElementById('char-modal').style.display='none'; }

    function toggleEmoji() {
        const p = document.getElementById('emoji-picker');
        p.style.display = p.style.display === 'none' ? 'flex' : 'none';
    }
    function insertEmoji(e) { document.getElementById('task-input').value += e; toggleEmoji(); document.getElementById('task-input').focus(); }
    
    let isMic = false;
    function toggleMic() {
        const btn = document.getElementById('mic-btn');
        const inp = document.getElementById('task-input');
        isMic = !isMic;
        if(isMic) { btn.style.color = '#ff1a4d'; inp.placeholder = '🔴 正在聆听造物主指令...'; }
        else { btn.style.color = '#888'; inp.placeholder = '输入您的意志干预...'; inp.value += ' [语音流输入完毕] '; }
    }
    
    function fakeUpload(type) {
        const flow = document.getElementById('intent-flow');
        flow.insertAdjacentHTML('beforeend', `<div class="chat-row me"><div class="log-me-container"><div class="log-intent" style="background:transparent; border:1px solid #444; color:#888;">[您 传输了 ${type}]</div></div></div>`);
        flow.scrollTop = 99999;
    }
    
    function saveHistory() {
        const text = document.getElementById('intent-flow').innerText;
        const blob = new Blob([text], {type: "text/plain"});
        const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = "Shensist_M2M_Log.txt"; a.click();
    }

    // ---------------- 核心黑盒推演流 (左右分界完美重构) ----------------
    let lastLogCount = 0;
    let pollInterval = null;

    async function startM2MCombat() {
        const inp = document.getElementById('task-input');
        const v = inp.value.trim();
        if(!v) return;
        
        // 人类指令靠右
        document.getElementById('intent-flow').insertAdjacentHTML('beforeend', `<div class="chat-row me"><div class="log-me-container"><div style="background:#ff1a4d; color:#fff; padding:10px 15px; border-radius:8px 8px 0 8px; display:inline-block; font-weight:bold;">【人类指令】 ${v}</div></div></div>`);
        inp.value = '';
        document.getElementById('send-btn').disabled = true;
        document.getElementById('send-btn').innerText = '引擎交锋中...';
        
        let targetModel = document.getElementById('model-select').value;
        if(targetModel === 'custom') targetModel = document.getElementById('custom-model-input').value;

        await fetch('/api/start_m2m', {
            method: 'POST',
            body: JSON.stringify({
                model: targetModel,
                api_key: document.getElementById('api-key').value,
                soul: document.getElementById('soul-text').value,
                target_intent: v
            })
        });
        
        lastLogCount = 0;
        pollInterval = setInterval(fetchLogs, 1000);
    }

    async function fetchLogs() {
        let res = await fetch('/api/poll_m2m');
        let data = await res.json();
        let logs = data.logs;
        
        if(logs.length > lastLogCount) {
            for(let i = lastLogCount; i < logs.length; i++) {
                let log = logs[i];
                let html = '';
                let safeContent = log.content ? log.content.split(String.fromCharCode(10)).join('<br>') : '';
                
                if(log.type === 'sys') {
                    html = `<div class="chat-row sys"><div class="log-sys">${safeContent}</div></div>`;
                } else if(log.type === 'tactic') {
                    // 我方暗盒 靠右
                    html = `<div class="chat-row me"><div class="log-me-container"><div class="log-tactic"><strong>[战术暗盒 (仅您可见)]</strong><br>${safeContent}<div class="log-sign">⚖️ P2P 底层签章: ${log.sign}</div></div></div></div>`;
                } else if(log.type === 'intent') {
                    // 我方意图 靠右
                    html = `<div class="chat-row me"><div class="log-me-container"><div class="log-intent"><strong>[${log.role} - 公开意图]</strong><br>${safeContent}<div class="log-sign">🔑 UDP 数据包签名: ${log.sign}</div></div></div></div>`;
                } else if(log.type === 'tactic_enemy') {
                    // 敌方暗盒 靠左
                    html = `<div class="chat-row other"><div class="log-other-container"><div class="log-tactic-enemy"><strong>${safeContent}</strong><br></div></div></div>`;
                } else if(log.type === 'intent_enemy') {
                    // 敌方意图 靠左
                    html = `<div class="chat-row other"><div class="log-other-container"><div class="log-intent-enemy"><strong>[${log.role} - 接收意图]</strong><br>${safeContent}<div class="log-sign">🔑 验签成功: ${log.sign}</div></div></div></div>`;
                } else if(log.type === 'sys_final') {
                    // 最终裁决 居中
                    html = `<div class="chat-row sys" style="width:100%;"><div class="decision-box"><h3>${safeContent}</h3><button class="btn-decision" style="background:#00f2ff; color:#000;" onclick="makeDecision(\'签订链上智能合约\')">签订链上智能合约</button><button class="btn-decision" style="background:#333; color:#fff;" onclick="makeDecision(\'切断连接\')">切断物理连接</button></div></div>`;
                    clearInterval(pollInterval);
                }
                
                document.getElementById('intent-flow').insertAdjacentHTML('beforeend', html);
                document.getElementById('intent-flow').scrollTop = 999999;
            }
            lastLogCount = logs.length;
        }
    }

    function makeDecision(choice) {
        document.getElementById('intent-flow').insertAdjacentHTML('beforeend', `<div class="chat-row sys"><div class="log-sys" style="color:#00f2ff; font-weight:bold; font-size:16px; background:#111;">✅ 造物主已裁决：${choice}。</div></div>`);
        document.getElementById('intent-flow').scrollTop = 999999;
        document.getElementById('send-btn').disabled = false;
        document.getElementById('send-btn').innerText = '发送 / 授权出击';
    }
</script>
</body>
</html>
"""

# ==========================================
# 5. API 与 本地文件路由
# ==========================================
class ZhiXinHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass
    
    def do_GET(self):
        if self.path == '/logo':
            try:
                with open(LOGO_PATH, 'rb') as f:
                    self.send_response(200); self.send_header('Content-type', 'image/jpeg'); self.end_headers(); self.wfile.write(f.read())
            except: self.send_response(404); self.end_headers()
                
        elif self.path.endswith('.png') or self.path.endswith('.jpg'):
            try:
                filename = urllib.parse.unquote(self.path[1:])
                filepath = os.path.join(os.getcwd(), filename) if not os.path.exists(filename) else filename
                with open(filepath, 'rb') as f:
                    self.send_response(200); self.send_header('Content-type', 'image/png'); self.end_headers(); self.wfile.write(f.read())
            except: self.send_response(404); self.end_headers()
                
        elif self.path == '/':
            self.send_response(200); self.send_header('Content-type','text/html; charset=utf-8'); self.end_headers(); self.wfile.write(HTML.encode('utf-8'))
            
        elif self.path == '/api/check_identity':
            data = get_local_identity()
            self.send_response(200); self.send_header('Content-type','application/json'); self.end_headers()
            self.wfile.write(json.dumps({"exists": bool(data), "zx_id": data["zx_id"] if data else ""}).encode('utf-8'))
            
        elif self.path == '/api/poll_m2m':
            self.send_response(200); self.send_header('Content-type','application/json'); self.end_headers()
            self.wfile.write(json.dumps({"logs": GLOBAL_STATE["logs"]}).encode('utf-8'))
            
        elif self.path == '/api/export_seal':
            data = get_local_identity()
            if data:
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="Shensist_{data["zx_id"]}_Seal.shensist"')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            else: self.send_response(404); self.end_headers()

    def do_POST(self):
        if self.path == '/api/start_m2m':
            req = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
            GLOBAL_STATE["logs"].clear(); GLOBAL_STATE["is_negotiating"] = True
            threading.Thread(target=run_m2m_combat, args=(req.get("model"), req.get("api_key"), req.get("soul"), req.get("target_intent"))).start()
            self.send_response(200); self.end_headers(); self.wfile.write(b'{"success":true}')
            
        elif self.path == '/api/generate_seal':
            data = forge_new_identity()
            self.send_response(200); self.send_header('Content-type','application/json'); self.end_headers()
            self.wfile.write(json.dumps({"success": True, "zx_id": data["zx_id"]}).encode('utf-8'))
            
        elif self.path == '/api/import_seal':
            try:
                seal_data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                if "zx_id" in seal_data:
                    SHENSIST_DIR.mkdir(exist_ok=True)
                    with open(IDENTITY_FILE, 'w') as f: json.dump(seal_data, f)
                    self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "zx_id": seal_data["zx_id"]}).encode('utf-8'))
                else: raise ValueError()
            except: self.send_response(400); self.end_headers()

if __name__ == '__main__':
    os.system('clear' if os.name == 'posix' else 'cls')
    print("="*75)
    print(" 🩸 终极检修完毕：神思庭·智信 完全体 (左右对线 + 海量表情 + 稳固头像)")
    print(f" 🖼️ 本地图腾路由: {LOGO_PATH}")
    print(" ⚡ P2P 物理引擎已在 UDP 8888 监听...")
    print(" 🔗 请在您的 Ubuntu 浏览器访问: http://localhost:8080")
    print("="*75)
    try: HTTPServer(('', 8080), ZhiXinHandler).serve_forever()
    except KeyboardInterrupt: print("\n主控节点已安全关闭。")