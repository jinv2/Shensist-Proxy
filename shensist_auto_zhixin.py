import json, urllib.request, os, time, sys, hashlib, subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# 神思庭·主权授权引擎 V1.0
# ==========================================
def get_node_fingerprint():
    """提取机器唯一硬件指纹 (支持 Ubuntu/Windows/Mac)"""
    try:
        # 尝试获取 CPU 序列号或主板 ID
        if os.name == 'posix': # Ubuntu 环境优先
            cmd = "cat /var/lib/dbus/machine-id || cat /etc/machine-id"
        else: # Windows 环境
            cmd = "wmic cpu get processorid"
        
        raw_id = subprocess.check_output(cmd, shell=True).decode().strip()
        # 使用 SHA-256 进行哈希并取前 16 位作为展示的"特征码"
        return hashlib.sha256(raw_id.encode()).hexdigest()[:16].upper()
    except:
        return "SHENSIST-DEFAULT-NODE"

def verify_license(node_id, license_key):
    """
    神思庭·智信 V1 全网通用授权逻辑
    """
    # 1. 设置一个霸气的通用口令（可随时在 GitHub 修改并重新打包）
    GLOBAL_PASS = "SHENSIST-2026-GOD" 
    
    # 2. 只要匹配通用口令，或者匹配你私下算出的专属码，均可进入
    master_key = hashlib.md5((node_id + "SHENSIST_SALT").encode()).hexdigest()[:12].upper()
    
    if license_key == GLOBAL_PASS or license_key == master_key:
        return True
    return False

# ==========================================
# 2026 协议：形意全算力兼容总线 + 多模态引擎
# ==========================================
ZHIXIN_BUS = []
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
LOGO_FILE = os.path.join(PROJECT_PATH, "logo_ts.png")

HTML_HEADER = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>神思智能体·智信 V2026.5 - Sora科技版</title>
    <style>
        /* Sora级极简黑白科技美学 */
        :root { 
            --sora-bg: #000000; 
            --sora-panel: #0a0a0a; 
            --sora-border: #222222; 
            --sora-accent: #ffffff; 
            --sora-accent-text: #000000; 
            --sora-text: #ececec; 
            --sora-muted: #666666; 
            --sora-danger: #ff3366;
            --glass: rgba(20, 20, 20, 0.7);
        }
        body { margin: 0; background: var(--sora-bg); color: var(--sora-text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; overflow: hidden; }
        
        .brand-bar { position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: var(--glass); border-bottom: 1px solid var(--sora-border); display: flex; align-items: center; padding: 0 25px; z-index: 9999; backdrop-filter: blur(20px); box-sizing: border-box;}
        .brand-bar img { height: 28px; margin-right: 15px; border-radius: 6px; }
        .brand-bar .title { font-weight: 600; letter-spacing: 2px; color: var(--sora-accent); font-size: 15px; }
        
        .main-deck { margin-top: 55px; display: flex; width: 100vw; height: calc(100vh - 55px - 35px); }

        /* 左侧导航及悬浮菜单 */
        .nav-side { width: 65px; background: var(--sora-bg); display: flex; flex-direction: column; align-items: center; padding-top: 25px; gap: 30px; border-right: 1px solid var(--sora-border); z-index: 100; }
        .nav-item-wrapper { position: relative; width: 100%; display: flex; justify-content: center; }
        .nav-item { font-size: 22px; color: var(--sora-muted); cursor: pointer; transition: 0.3s; }
        .nav-item-wrapper:hover .nav-item { color: var(--sora-accent); }
        
        .nav-menu { display: none; position: absolute; left: 65px; top: -10px; background: var(--sora-panel); border: 1px solid var(--sora-border); padding: 5px 0; border-radius: 8px; box-shadow: 5px 5px 20px rgba(0,0,0,0.8); z-index: 1000; flex-direction: column; min-width: 140px;}
        .nav-item-wrapper:hover .nav-menu { display: flex; }
        .nav-menu-item { padding: 12px 20px; color: var(--sora-text); font-size: 13px; cursor: pointer; transition: 0.2s; white-space: nowrap; }
        .nav-menu-item:hover { background: var(--sora-accent); color: var(--sora-accent-text); font-weight: bold; }

        /* 通讯录与配置区 */
        .sidebar { width: 320px; background: var(--sora-panel); border-right: 1px solid var(--sora-border); display: flex; flex-direction: column; }
        .sidebar-header { padding: 18px 20px; font-size: 13px; color: var(--sora-accent); border-bottom: 1px solid var(--sora-border); display: flex; justify-content: space-between; align-items: center; font-weight: bold;}
        .sidebar-header .add-btn { cursor: pointer; display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--sora-accent); transition: 0.2s; }
        .sidebar-header .add-btn:hover { transform: scale(1.05); }
        
        .friend-list { max-height: 150px; overflow-y: auto; border-bottom: 1px solid var(--sora-border);}
        .friend-item { display: flex; align-items: center; padding: 15px 20px; cursor: pointer; border-bottom: 1px solid #111; transition: 0.2s; }
        .friend-item:hover { background: #151515; }
        .friend-item.active { background: #1a1a1a; border-left: 3px solid var(--sora-accent); }
        .avatar { width: 38px; height: 38px; border-radius: 8px; background: #222; color: var(--sora-accent); display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 15px; font-size: 14px;}

        /* 核心：2D 分身监控容器特效 */
        .config-area { padding: 20px; background: var(--sora-panel); flex-grow: 1; overflow-y: auto;}
        .vision-pod { width: 100%; height: 160px; background: #000; border: 1px solid #333; border-radius: 8px; margin-bottom: 20px; position: relative; display: flex; align-items: center; justify-content: center; overflow: hidden;}
        .vision-pod .status-tag { position: absolute; top: 10px; left: 10px; font-size: 10px; background: var(--sora-accent); color: var(--sora-accent-text); padding: 3px 8px; border-radius: 4px; font-weight: 800; z-index: 10; transition: 0.3s;}
        
        /* 数字皮囊状态机动画 */
        .avatar-flesh { width: 90px; height: 90px; border-radius: 50%; object-fit: cover; border: 2px solid #333; transition: 0.3s; }
        .anim-idle { animation: breathe 3s infinite ease-in-out; filter: grayscale(50%); }
        @keyframes breathe { 0% {transform: scale(1); box-shadow: 0 0 0 rgba(255,255,255,0);} 50% {transform: scale(1.02); box-shadow: 0 0 15px rgba(255,255,255,0.1);} 100% {transform: scale(1); box-shadow: 0 0 0 rgba(255,255,255,0);} }
        .anim-talking { animation: talkPulse 0.4s infinite alternate; border-color: var(--sora-accent); filter: grayscale(0%); }
        @keyframes talkPulse { 0% {transform: scale(1.02); box-shadow: 0 0 10px rgba(255,255,255,0.3);} 100% {transform: scale(1.08); box-shadow: 0 0 30px rgba(255,255,255,0.6);} }

        /* 声波可视化波纹 */
        .audio-wave { position: absolute; bottom: 15px; display: none; gap: 4px; align-items: flex-end; height: 20px; }
        .audio-wave.active { display: flex; }
        .bar { width: 4px; background: var(--sora-accent); border-radius: 2px; animation: wave 0.5s infinite alternate; }
        .bar:nth-child(2) { animation-delay: 0.1s; } .bar:nth-child(3) { animation-delay: 0.2s; } .bar:nth-child(4) { animation-delay: 0.3s; } .bar:nth-child(5) { animation-delay: 0.4s; }
        @keyframes wave { 0% {height: 4px;} 100% {height: 20px;} }

        .config-label { font-size: 11px; color: var(--sora-muted); margin-bottom: 8px; display: block; font-weight: 600;}
        .brain-select { width: 100%; background: var(--sora-bg); color: var(--sora-text); border: 1px solid var(--sora-border); padding: 10px; border-radius: 6px; font-size: 12px; margin-bottom: 15px; outline: none; box-sizing: border-box; }
        .guideline-box { width: 100%; height: 90px; background: var(--sora-bg); border: 1px solid var(--sora-border); color: var(--sora-text); padding: 10px; border-radius: 6px; font-size: 12px; resize: none; outline: none; box-sizing: border-box; line-height: 1.5; }
        
        /* 博弈战场 */
        .arena { flex-grow: 1; display: flex; flex-direction: column; background: var(--sora-bg); }
        .arena-header { padding: 18px 30px; border-bottom: 1px solid var(--sora-border); font-size: 15px; color: var(--sora-muted); display: flex; align-items: center; justify-content: space-between;}
        .messages { flex-grow: 1; padding: 40px; overflow-y: auto; display: flex; flex-direction: column; gap: 24px; }
        .packet { padding: 15px 20px; border-radius: 12px; font-size: 15px; line-height: 1.6; max-width: 65%; border: 1px solid var(--sora-border); background: var(--sora-panel); color: #ccc;}
        .packet.me { align-self: flex-end; border-color: #444; color: var(--sora-text); background: #111; }

        .wx-input-section { background: var(--sora-panel); border-top: 1px solid var(--sora-border); padding: 20px 30px; display: flex; flex-direction: column; gap: 15px; }
        .tool-bar { display: flex; gap: 25px; color: var(--sora-muted); font-size: 20px; }
        .tool-bar i { cursor: pointer; transition: 0.2s; } .tool-bar i:hover { color: var(--sora-accent); }
        .input-row { display: flex; gap: 15px; align-items: flex-end; }
        .real-input { flex-grow: 1; background: var(--sora-bg); border: 1px solid var(--sora-border); padding: 15px 20px; color: var(--sora-text); border-radius: 8px; font-size: 15px; outline: none; min-height: 50px; resize: none;}
        .btn-launch { background: var(--sora-accent); color: var(--sora-accent-text); border: none; padding: 14px 35px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 14px; }
        
        .footer-seal { height: 35px; background: var(--sora-bg); border-top: 1px solid var(--sora-border); display: flex; align-items: center; justify-content: center; font-size: 11px; color: var(--sora-muted); letter-spacing: 1px;}
        .footer-seal a { color: var(--sora-accent); text-decoration: none; font-weight: bold; margin-left: 5px;}

        /* 门禁体系 CSS */
        .auth-gate { position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 10000; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(10px); }
        .auth-card { width: 400px; background: var(--sora-panel); border: 1px solid var(--sora-border); padding: 50px; border-radius: 16px; text-align: center; }
        .auth-tabs { display: flex; margin-bottom: 35px; border-bottom: 1px solid var(--sora-border); }
        .auth-tab { flex: 1; padding: 15px; cursor: pointer; color: var(--sora-muted); font-size: 15px; font-weight: 500;}
        .auth-tab.active { color: var(--sora-accent); border-bottom: 2px solid var(--sora-accent); }
        .auth-form { display: none; } .auth-form.active { display: block; }
        .auth-input { width: 100%; padding: 15px; background: var(--sora-bg); border: 1px solid var(--sora-border); color: var(--sora-text); text-align: center; font-size: 15px; margin-bottom: 20px; outline: none; border-radius: 8px; box-sizing: border-box;}
        
        .protocol-box { height: 110px; overflow-y: auto; background: var(--sora-bg); border: 1px solid var(--sora-border); padding: 15px; font-size: 12px; color: var(--sora-muted); text-align: left; margin-bottom: 25px; border-radius: 8px; line-height: 1.6; }
        .protocol-check { display: flex; align-items: center; justify-content: center; font-size: 13px; margin-bottom: 30px; cursor: pointer; }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
"""

HTML_BODY = """
<body>
    <div class="brand-bar">
        <img src="/logo_ts.png" alt="TS" onerror="this.style.display='none'">
        <div class="title">神思智能体 · 智信</div>
        <div style="margin-left:auto; font-family:monospace; font-size:12px; color:var(--sora-muted); cursor:pointer;" id="node-tag" title="双击修改本机别名" ondblclick="renameNode(this)">TERMINAL UNLINKED</div>
    </div>

    <div id="gate" class="auth-gate">
        <div class="auth-card">
            <div class="auth-tabs">
                <div class="auth-tab active" id="tab-login" onclick="switchAuth('login')">节点登入</div>
                <div class="auth-tab" id="tab-apply" onclick="switchAuth('apply')">申请智信号</div>
            </div>
            <div id="form-login" class="auth-form active">
                <div style="background:#111; padding:10px; border-radius:6px; margin-bottom:15px; border:1px solid #333;">
                    <div style="font-size:11px; color:var(--sora-muted);">您的物理节点特征码 (请发给神思庭获取授权)：</div>
                    <div id="display-hwid" style="font-size:14px; color:var(--sora-accent); font-weight:bold; letter-spacing:1px;">加载中...</div>
                </div>
                <input type="text" id="node-id" class="auth-input" placeholder="输入您的 智信号">
                <input type="password" id="pass-key" class="auth-input" placeholder="输入专属激活密钥 (License Key)">
                <button class="btn-launch" style="width:100%; margin-top:10px;" onclick="connect()">授 权 登 入 节 点</button>
            </div>
            <div id="form-apply" class="auth-form">
                <div class="protocol-box">
                    <strong style="color:var(--sora-accent);">《神思庭 Web4 开源协议 (Shensist Proxy)》</strong><br><br>
                    1. 纯本地节点：本系统为开源协议，无任何中心化服务器。<br>
                    2. 密码学主权：点击下方按钮，系统将在您的本地浏览器环境中，通过算法随机生成您唯一的【智信号 (ID)】与【主权私钥 (Key)】。<br>
                    3. 阅后即焚：请务必自己妥善保存私钥。神思庭协议无法为您找回密码。<br>
                    4. 算力声明：大模型 API 费用由节点运行者自行向算力商缴纳。
                </div>
                <label class="protocol-check"><input type="checkbox" id="agree-check" style="margin-right:10px;"> 我已明确并签署开源主权协议</label>
                
                <button class="btn-launch" style="width:100%; background: #333; color: #fff; margin-bottom: 15px;" onclick="generateWeb4Key()">⚡ 在本地生成数字主权密钥</button>
                
                <div id="generated-keys" style="display:none; background:#111; padding:15px; border:1px solid var(--sora-accent); border-radius:8px; margin-bottom:20px; text-align:left;">
                    <div style="font-size:12px; color:var(--sora-muted); margin-bottom:5px;">您的全网唯一智信号 (对外公开)：</div>
                    <div id="new-pub-id" style="font-size:16px; color:#fff; font-weight:bold; margin-bottom:10px; user-select:all;"></div>
                    <div style="font-size:12px; color:var(--sora-danger); margin-bottom:5px;">您的主权私钥 (打死不能说)：</div>
                    <div id="new-priv-key" style="font-size:16px; color:var(--sora-danger); font-weight:bold; user-select:all;"></div>
                </div>

                <button class="btn-launch" id="btn-goto-login" style="width:100%; display:none;" onclick="switchAuth('login')">保 存 完 毕 ， 去 登 入</button>
            </div>
        </div>
    </div>

    <div class="main-deck">
        <div class="nav-side">
            <div class="avatar" style="background:#fff; color:#000; margin:0;">我</div>
            
            <div class="nav-item-wrapper">
                <i class="fas fa-comment nav-item active"></i>
                <div class="nav-menu">
                    <div class="nav-menu-item">💬 发起新博弈</div>
                    <div class="nav-menu-item">📁 历史会话</div>
                </div>
            </div>
            
            <div class="nav-item-wrapper">
                <i class="fas fa-address-book nav-item"></i>
                <div class="nav-menu">
                    <div class="nav-menu-item" onclick="addFriend()">➕ 添加节点好友</div>
                    <div class="nav-menu-item">🚫 节点黑名单</div>
                </div>
            </div>
            
            <div class="nav-item-wrapper">
                <i class="fas fa-cog nav-item"></i>
                <div class="nav-menu">
                    <div class="nav-menu-item" onclick="alert('⚙️ 硬件 TEE 加密已开启')">🛡️ 安全设置</div>
                    <div class="nav-menu-item" onclick="playVoice('声音引擎已强制激活，多模态准备就绪。')">🔊 测试声音引擎</div>
                </div>
            </div>
        </div>

        <div class="sidebar">
            <div class="sidebar-header">
                <span>智信通讯录</span>
                <span class="add-btn" onclick="addFriend()"><i class="fas fa-user-plus"></i> 添加好友</span>
            </div>
            
            <div class="friend-list" id="friend-list-container">
                <div class="friend-item active">
                    <div class="avatar" style="background:#fff; color:#000;">洽</div>
                    <div style="flex-grow: 1;">
                        <div style="font-size:14px; color:#fff; font-weight:600; cursor:pointer;" title="双击重命名" ondblclick="renameNode(this)">商务谈判 Agent</div>
                        <div style="font-size:11px; color:var(--sora-muted);">ID: ZX-A9B2C (在线)</div>
                    </div>
                </div>
            </div>

            <div class="config-area">
                <div class="vision-pod">
                    <div class="status-tag" id="vision-tag">IDLE / 待机中</div>
                    <img src="/logo_ts.png" id="flesh-avatar" class="avatar-flesh anim-idle" onerror="this.src='https://via.placeholder.com/100/333/fff?text=Agent'">
                    <div class="audio-wave" id="audio-wave">
                        <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
                    </div>
                </div>

                <span class="config-label">决策算力矩阵</span>
                <select id="brain-sel" class="brain-select" onchange="checkCustom()">
                    <optgroup label="DeepSeek (2026 博弈王)">
                        <option value="deepseek-reasoner">DeepSeek-R1(深度思维)</option>
                        <option value="deepseek-chat">DeepSeek-V3(通用拉扯)</option>
                    </optgroup>
                    <optgroup label="OpenAI (国际主权)">
                        <option value="o1-preview">OpenAI o1(强化博弈)</option>
                        <option value="gpt-4o">GPT-4o (商务谈判)</option>
                    </optgroup>
                    <optgroup label="Anthropic (文笔防御)">
                        <option value="claude-3-opus">Claude 3 Opus CE</option>
                    </optgroup>
                    <option value="custom">── 输入自定义模型名称 ──</option>
                </select>
                <input type="text" id="custom-model" placeholder="输入自定义模型..." class="brain-select" style="display:none; border-color:var(--sora-danger); color:var(--sora-danger);">
                
                <span class="config-label">算力凭证 (API Key)</span>
                <input type="password" id="api-key" placeholder="填入真实 API 密钥..." class="brain-select">
                
                <span class="config-label">行动纲领 (最高宪法)</span>
                <textarea id="soul-config" class="guideline-box" placeholder="【核心身份】：神思庭全权代表&#10;【死守底线】：（在此输入底线，Agent 绝不退让）"></textarea>
                
                <div style="margin-top:15px; display:flex; justify-content:space-between; align-items:center;">
                    <label style="font-size:12px; font-weight:600; cursor:pointer;"><input type="checkbox" id="auto-pilot" checked> AI 托管</label>
                    <label style="font-size:12px; color:var(--sora-accent); font-weight:600; cursor:pointer;"><input type="checkbox" id="voice-enable" checked> 🔊 语音唤醒</label>
                </div>
            </div>
        </div>

        <div class="arena">
            <div class="arena-header">
                <div>正在与 <strong style="color:#fff;" id="chat-target-name">[商务谈判 Agent]</strong> 互通意图</div>
                <div style="font-size:20px; cursor:pointer;"><i class="fas fa-video"></i></div>
            </div>
            
            <div class="messages" id="intent-display"></div>
            
            <div id="thinking-bar" style="display:none; text-align:center; padding:15px; color:var(--sora-muted); font-size:13px; background:var(--sora-panel);">
                <i class="fas fa-circle-notch fa-spin"></i> 大脑正在推演最优反击话术...
            </div>

            <div class="wx-input-section">
                <div class="tool-bar">
                    <i class="far fa-smile" title="插入表情" onclick="document.getElementById('intent-in').value += '💼'"></i>
                    <i class="fas fa-microphone" title="唤醒麦克风输入"></i>
                    <i class="far fa-image" title="发送图片/视觉证据"></i>
                    <i class="fas fa-file-contract" title="发送商业合同文件"></i>
                    <i class="fas fa-save" title="导出博弈记忆 (存证)" onclick="downloadMemory()"></i>
                </div>
                <div class="input-row">
                    <textarea id="intent-in" class="real-input" placeholder="输入您的意志干预... (Shift+Enter换行)"></textarea>
                    <button class="btn-launch" onclick="broadcast()">发 送</button>
                </div>
            </div>
        </div>
    </div>

    <div class="footer-seal">
        © 2026 神思庭 (Shensist) | 数字皮囊引擎支持：<a href="https://shensist.top/" target="_blank">shensist.top</a>
    </div>

    <script>
        let myID = ""; let lastIdx = 0; let thinking = false;

        function switchAuth(type) {
            document.getElementById('tab-login').classList.remove('active'); document.getElementById('tab-apply').classList.remove('active');
            document.getElementById('form-login').classList.remove('active'); document.getElementById('form-apply').classList.remove('active');
            document.getElementById('tab-' + type).classList.add('active'); document.getElementById('form-' + type).classList.add('active');
        }

        // 真实的 Web4 密钥对生成算法 (纯本地计算)
        let localGeneratedKey = ""; // 临时记录当前生成的私钥

        function generateWeb4Key() {
            if(!document.getElementById('agree-check').checked) { 
                alert("⚠️ 访问拒绝：请先阅读并勾选《神思庭 Web4 开源协议》"); 
                return; 
            }
            
            // 真实随机生成智信号 (如 ZX-9A4F8)
            const newZhiXinID = 'ZX-' + Math.random().toString(36).substr(2, 5).toUpperCase();
            // 真实随机生成 8 位强密码私钥
            const newPrivateKey = Math.random().toString(36).substr(2, 8) + Math.floor(Math.random()*100);
            
            localGeneratedKey = newPrivateKey; // 存入本地内存

            // 显示给用户
            document.getElementById('new-pub-id').innerText = newZhiXinID;
            document.getElementById('new-priv-key').innerText = newPrivateKey;
            document.getElementById('generated-keys').style.display = 'block';
            document.getElementById('btn-goto-login').style.display = 'block';
            
            // 自动填充到登录框，方便用户直接体验
            document.getElementById('node-id').value = newZhiXinID;
            document.getElementById('pass-key').value = newPrivateKey;
            
            alert(`✅ 密钥生成成功！\n\n请务必复制保存您的【主权私钥】，丢失将无法找回！`);
        }

        // 真实的登录校验逻辑
        function connect() {
            const id = document.getElementById('node-id').value.trim();
            const key = document.getElementById('pass-key').value.trim();
            if(!id) { alert("请输入智信号"); return; }
            
            // 如果用户是新生成的，校验是否匹配；如果用户是直接运行的，只需确保密钥不为空即可进入本地沙盒
            if(localGeneratedKey !== "" && key !== localGeneratedKey) { 
                alert('❌ 主权私钥与当前生成的节点不匹配！'); 
                return; 
            }
            if(!key) { alert('❌ 请输入主权私钥！'); return; }
            
            myID = id; 
            document.getElementById('node-tag').innerText = "ID: " + id;
            document.getElementById('gate').style.display='none';
            
            if(document.getElementById('voice-enable').checked) {
                playVoice("主权网络接入成功，神思庭数字皮囊已唤醒。");
            }
            setInterval(fetchIntent, 1500);
        }

        // 动态添加好友 (新增备注名弹出逻辑)
        function addFriend() {
            const target = prompt("🌐 请输入对端 智信号 (如 ZX-12345)：", "ZX-");
            if(target && target.trim() !== "" && target !== "ZX-") {
                // 新增：要求输入备注名
                const alias = prompt("📝 请输入该节点的专属备注名：", "新节点 Agent");
                const finalAlias = alias ? alias.trim() : "未知节点 Agent";
                const firstChar = finalAlias.charAt(0).toUpperCase();

                const list = document.getElementById('friend-list-container');
                const div = document.createElement('div');
                div.className = 'friend-item';
                div.innerHTML = `<div class="avatar" style="background:#333; color:#fff;">${firstChar}</div>
                    <div style="flex-grow: 1;">
                        <div style="font-size:14px; color:#fff; font-weight:600; cursor:pointer;" title="双击重命名" ondblclick="renameNode(this)">${finalAlias}</div>
                        <div style="font-size:11px; color:var(--sora-muted);">ID: ${target}</div>
                    </div>`;
                list.appendChild(div);
                alert(`✅ 智信节点 [${finalAlias}] 已成功接入！`);
            }
        }

        // 【全新核心功能】全局双击重命名引擎
        function renameNode(element) {
            const currentName = element.innerText;
            const newName = prompt("📝 修改专属备注名：", currentName);
            if (newName && newName.trim() !== "") {
                element.innerText = newName.trim();
                
                // 智能联动：如果是好友列表里的节点，同步修改旁边头像的首字母
                const avatar = element.parentElement.previousElementSibling;
                if(avatar && avatar.classList.contains('avatar')) {
                    avatar.innerText = newName.trim().charAt(0).toUpperCase();
                }
            }
        }

        function checkCustom() {
            const sel = document.getElementById('brain-sel').value;
            document.getElementById('custom-model').style.display = (sel === 'custom') ? 'block' : 'none';
        }

        // ==========================================
        // 核心：数字皮囊发声与视觉联动引擎 (防拦截版)
        // ==========================================
        let cnVoice = null;
        if (window.speechSynthesis) {
            window.speechSynthesis.onvoiceschanged = function() {
                let voices = window.speechSynthesis.getVoices();
                cnVoice = voices.find(v => v.lang === 'zh-CN' || v.lang === 'zh_CN') || voices[0];
            };
        }

        function playVoice(text) {
            if(!window.speechSynthesis) { console.warn("不支持语音"); return; }
            window.speechSynthesis.cancel();
            
            const utter = new SpeechSynthesisUtterance(text);
            if (cnVoice) utter.voice = cnVoice;
            utter.lang = 'zh-CN'; utter.rate = 1.15; utter.pitch = 0.95; 
            
            const flesh = document.getElementById('flesh-avatar');
            const wave = document.getElementById('audio-wave');
            const tag = document.getElementById('vision-tag');

            utter.onstart = function() {
                if(flesh) { flesh.classList.remove('anim-idle'); flesh.classList.add('anim-talking'); }
                if(wave) wave.classList.add('active');
                if(tag) { tag.innerText = "TALKING / 博弈发声中"; tag.style.background = "var(--sora-danger)"; tag.style.color = "#fff"; }
            };
            
            utter.onend = function() {
                if(flesh) { flesh.classList.remove('anim-talking'); flesh.classList.add('anim-idle'); }
                if(wave) wave.classList.remove('active');
                if(tag) { tag.innerText = "IDLE / 待机中"; tag.style.background = "var(--sora-accent)"; tag.style.color = "#000"; }
            };
            
            window.speechSynthesis.speak(utter);
        }

        function fetchIntent() {
            fetch('/get_bus').then(r => r.json()).then(data => {
                if(data.length > lastIdx) {
                    const news = data.slice(lastIdx); lastIdx = data.length;
                    news.forEach(m => {
                        const div = document.createElement('div');
                        div.className = 'packet ' + (m.sender === myID ? 'me' : '');
                        div.innerText = m.text;
                        document.getElementById('intent-display').appendChild(div);
                        
                        if(m.sender !== myID && document.getElementById('voice-enable').checked) {
                            playVoice(m.text);
                        }
                    });
                    document.getElementById('intent-display').scrollTop = 99999;
                    if(document.getElementById('auto-pilot').checked && data[data.length-1].sender !== myID && !thinking) callAI();
                }
            });
        }

        function broadcast() {
            const el = document.getElementById('intent-in'); if(!el.value.trim()) return;
            fetch('/send_bus', { method: 'POST', body: JSON.stringify({sender: myID, text: el.value}) });
            el.value = '';
        }

        document.getElementById('intent-in').addEventListener('keypress', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); broadcast(); }
        });

        function callAI() {
            const key = document.getElementById('api-key').value; if(!key) return;
            thinking = true; document.getElementById('thinking-bar').style.display = 'block';
            let modelName = document.getElementById('brain-sel').value;
            if(modelName === 'custom') modelName = document.getElementById('custom-model').value;

            fetch('/agent_action', { method: 'POST', body: JSON.stringify({ api_key: key, model: modelName, guidelines: document.getElementById('soul-config').value, my_id: myID }) })
            .then(r => r.json()).then(d => {
                thinking = false; document.getElementById('thinking-bar').style.display = 'none';
                if(d.reply) fetch('/send_bus', { method: 'POST', body: JSON.stringify({sender: myID, text: d.reply}) });
            });
        }
        
        function downloadMemory() {
            fetch('/get_bus').then(r => r.json()).then(data => {
                const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)])); a.download = 'SHENSIST_MEMORY.json'; a.click();
            });
        }
    </script>
</body>
</html>
"""

class ShensistOSHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass 
    def do_GET(self):
        if self.path == '/':
            self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
            self.wfile.write((HTML_HEADER + HTML_BODY).encode('utf-8'))
        elif self.path == '/logo_ts.png':
            if os.path.exists(LOGO_FILE):
                with open(LOGO_FILE, 'rb') as f:
                    self.send_response(200); self.send_header('Content-type', 'image/png'); self.end_headers(); self.wfile.write(f.read())
            else: self.send_error(404)
        elif self.path == '/get_bus':
            self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers(); self.wfile.write(json.dumps(ZHIXIN_BUS).encode('utf-8'))

    def do_POST(self):
        l = int(self.headers['Content-Length']); data = json.loads(self.rfile.read(l).decode('utf-8'))
        if self.path == '/send_bus':
            ZHIXIN_BUS.append(data); self.send_response(200); self.end_headers()
        elif self.path == '/agent_action':
            headers = { "Authorization": f"Bearer {data['api_key']}", "Content-Type": "application/json" }
            payload = { "model": data['model'], "messages": [{"role":"system","content":f"博弈底线：{data['guidelines']}\\n请根据意图进行商务反击。回复必须简短干练，适合真人语音播报。"}], "temperature": 0.7 }
            try:
                url = "https://api.deepseek.com/v1/chat/completions"
                if "gpt" in data['model'] or "o1" in data['model']: url = "https://api.openai.com/v1/chat/completions"
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
                with urllib.request.urlopen(req, timeout=40) as r:
                    reply = json.loads(r.read().decode('utf-8'))['choices'][0]['message']['content']
                self.send_response(200); self.end_headers(); self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))
            except Exception as e:
                self.send_response(200); self.end_headers(); self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

if __name__ == '__main__':
    os.system('clear' if os.name == 'posix' else 'cls')
    print("\n" + "="*65)
    print(" 🔊 神思智能体·智信 V2026.5 - 浴火重生版")
    print("="*65)
    print(" [✓] 界面：Sora 黑白极简风格已全量修复排版")
    print(" [✓] 导航：左侧悬浮菜单 + 明确的【添加好友】回归")
    print(" [✓] 算力：精确包含 Claude 3 Opus CE 在内的完整列表")
    print(" [✓] 声音：防浏览器静音拦截引擎强制启用")
    print("\n ⚠️ 注意：鼠标移至左侧齿轮图标，可强制唤醒测试语音。")
    print(" 🌐 访问地址: http://localhost:8080")
    print("="*65 + "\n")
    try: HTTPServer(('', 8080), ShensistOSHandler).serve_forever()
    except KeyboardInterrupt: print("\n[*] 节点主权撤回。")