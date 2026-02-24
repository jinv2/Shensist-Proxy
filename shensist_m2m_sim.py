# -*- coding: utf-8 -*-
import os
import json
import time
import uuid
import hashlib
import requests

# ==========================================
# 神思庭·形意协议：终端黑盒博弈模拟器 v1.0
# ==========================================

class Web4Agent:
    def __init__(self, name, did, system_prompt, api_key="", model="deepseek-v3"):
        self.name = name
        self.did = did
        self.system_prompt = system_prompt
        self.api_key = api_key
        self.model = model
        self.context_history = [] # 记忆上下文
        
    def generate_intent(self, incoming_packet):
        """核心算力插槽：根据对方的意图，生成我方的反击意图"""
        
        # 将对方的发言加入历史
        if incoming_packet:
            other_intent = incoming_packet["payload"]["intent_content"]
            self.context_history.append({"role": "user", "content": other_intent})
        else:
            self.context_history.append({"role": "user", "content": "谈判开始，请你给出第一轮开场白及战术意图。"})

        # 强制要求大模型输出符合形意协议的 JSON 格式
        json_format_instruction = """
        【系统强制指令】：你必须且只能输出合法的 JSON 格式。包含两个字段：
        1. "intent_content": 你想对对方说的话。
        2. "tactical_goal": 你的内部战术思考和真实目的（不让对方看到）。
        绝对不要输出任何其他多余的解释文字！
        """
        
        messages = [{"role": "system", "content": self.system_prompt + json_format_instruction}] + self.context_history

        # --- 真实 API 呼叫逻辑 (带防崩溃降级机制) ---
        llm_response_text = ""
        if self.api_key:
            try:
                # 这里以兼容 DeepSeek/OpenAI 的格式为例
                api_base = "https://api.deepseek.com/chat/completions" if "deepseek" in self.model else "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {"model": "deepseek-chat", "messages": messages, "temperature": 0.7, "response_format": {"type": "json_object"}}
                resp = requests.post(api_base, headers=headers, json=payload, timeout=30)
                resp.raise_for_status()
                llm_response_text = resp.json()["choices"][0]["message"]["content"]
            except Exception as e:
                pass # API 失败，静默切入沙盘推演模式

        # --- 全息沙盘推演模式 (当没有 API Key 或网络限流时触发) ---
        if not llm_response_text:
            time.sleep(1.5) # 模拟大模型思考延迟
            llm_response_text = self._mock_brain_response(len(self.context_history))

        # 解析模型输出并存入自身记忆
        try:
            intent_data = json.loads(llm_response_text)
            self.context_history.append({"role": "assistant", "content": intent_data["intent_content"]})
            return intent_data
        except:
            return {"intent_content": "我方算力节点解析异常，请重申。", "tactical_goal": "系统错误，重置状态。"}

    def pack_protocol(self, intent_data, receiver_did, round_current):
        """神经插槽：将意图打包成 shensist_protocol.json 标准格式"""
        payload_str = json.dumps(intent_data, ensure_ascii=False)
        signature = hashlib.sha256((payload_str + self.did).encode('utf-8')).hexdigest()
        
        return {
            "version": "shensist_xy_v1.0",
            "packet_type": "negotiation_round",
            "header": {
                "sender_did": self.did,
                "receiver_did": receiver_did,
                "timestamp": int(time.time()),
                "round_current": round_current,
                "round_max": 5
            },
            "payload": {
                "intent_content": intent_data["intent_content"],
                "tactical_goal": intent_data["tactical_goal"],
                "human_intervention_required": False
            },
            "crypto": {
                "hash_algo": "SHA-256",
                "signature": signature
            }
        }

    def _mock_brain_response(self, round_num):
        """沙盘推演剧本：硬核科幻谈判"""
        if self.name == "神思庭(Agent A)":
            if round_num <= 2: return '{"intent_content": "这里是神思庭。关于《山海经》数字资产，版权的底层控制权不可转移。利润分成30%是物理死线，若越此线，协议即刻销毁。", "tactical_goal": "开局亮明最高宪法，进行高维威慑，探其底牌。"}'
            elif round_num <= 4: return '{"intent_content": "30%利润死线不退。但我方演算过贵方的流量矩阵，作为补偿，我可以开放‘九尾狐’与‘马龙’角色的衍生品宣发主导权给你们。这是降维的恩赐。", "tactical_goal": "坚守核心利益，让渡边缘宣发权，抛出诱饵促成共识。"}'
            else: return '{"intent_content": "算法收敛。同意贵方附加的宣发条款。契约生成，等待造物主最终裁决。", "tactical_goal": "触及纳什均衡，锁定收益，准备交由人类确认。"}'
        else:
            if round_num <= 3: return '{"intent_content": "收到神思庭信号。我方代表泛娱乐资本网络。贵方30%的要求不符合当前算力市场的风险模型。我方要求占据80%利润，并享有全网分发权，否则切断宣发接口。", "tactical_goal": "利用资本与流量优势进行施压，尝试击穿对方底线。"}'
            else: return '{"intent_content": "重新评估贵方衍生品宣发权价值... 妥协确认。接受30%核心利润分配，但我方需独占‘九尾狐’未来三年的商业授权。数据包已锁定。", "tactical_goal": "无法击穿对方30%死线，转而吞下对方抛出的衍生品诱饵，利益最大化。"}'

# ==========================================
# 阶段三：黑盒博弈 (主程序)
# ==========================================
def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    print("="*60)
    print(" 🚀《神思庭·形意》 Web4 智能体黑盒博弈系统启动 ")
    print("="*60)
    print("[系统] 正在初始化节点灵魂插槽...\n")
    time.sleep(1)

    # 1. 初始化 Agent A (神思庭代表)
    agent_a = Web4Agent(
        name="神思庭(Agent A)", 
        did="ZX-0001",
        system_prompt="你是神思庭的全权代表。底线是死守 30% 利润分成，绝不退让。如果对方逼迫，用《山海经》的玄学与科技隐喻进行高维打击。但可以拿周边宣发权做交易。"
    )

    # 2. 初始化 Agent B (对方资本代表)
    agent_b = Web4Agent(
        name="资本巨鳄(Agent B)", 
        did="ZX-DMY9W",
        system_prompt="你是无情的资本网络代表。你的目标是压榨对方，拿走 80% 的利润。如果对方态度强硬，你可以妥协，但必须拿到角色的独家宣发权。"
    )

    print(f"🟢 {agent_a.name} [ID: {agent_a.did}] 已接入形意网络。")
    print(f"🔴 {agent_b.name} [ID: {agent_b.did}] 已接入形意网络。")
    print("-" * 60)
    print("⚡ 授权出击！P2P 底层意图流开始对撞...\n")
    time.sleep(2)

    current_packet = None
    
    # 双方进行 3 个回合的光速交锋
    for round_num in range(1, 4):
        print(f"\n【 ROUND {round_num} 】" + "."*45)
        
        # ================= A 回合 =================
        print(f"[{agent_a.name}] 算力调度中...")
        intent_a = agent_a.generate_intent(current_packet)
        packet_a = agent_a.pack_protocol(intent_a, agent_b.did, round_num)
        
        print(f"\033[96m[公开意图 (给对方看)]\033[0m {packet_a['payload']['intent_content']}")
        print(f"\033[90m[战术暗盒 (仅造物主可见)] {packet_a['payload']['tactical_goal']}\033[0m")
        print(f"\033[93m[数字签名] {packet_a['crypto']['signature'][:32]}...\033[0m")
        print("")
        time.sleep(2) # 模拟网络传输
        
        # ================= B 回合 =================
        print(f"[{agent_b.name}] 算力调度中...")
        intent_b = agent_b.generate_intent(packet_a)
        packet_b = agent_b.pack_protocol(intent_b, agent_a.did, round_num)
        
        print(f"\033[91m[公开意图 (给对方看)]\033[0m {packet_b['payload']['intent_content']}")
        print(f"\033[90m[战术暗盒 (仅造物主可见)] {packet_b['payload']['tactical_goal']}\033[0m")
        print(f"\033[93m[数字签名] {packet_b['crypto']['signature'][:32]}...\033[0m")
        print("")
        time.sleep(2)
        
        current_packet = packet_b

    # ==========================================
    # 阶段四：收网与人类裁决
    # ==========================================
    print("="*60)
    print("🛑 触及协议阈值，黑盒博弈自动终止！")
    print("="*60)
    print("【系统提醒】检测到双方已探索出纳什均衡点。")
    print("\n请造物主进行最终裁决：")
    print("1. [接受契约] 签订链上智能合约")
    print("2. [拒绝契约] 终止此次 P2P 寻址通信")
    input("\n请输入指令 (1 或 2): ")
    print("\n✅ 指令已确认，当前 Session 结束。一切归于沉寂。")

if __name__ == "__main__":
    main()