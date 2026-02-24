import os
import json
from protocol_parser import parser # 引用您已实现的解析器

# ==========================================
# 《形意协议》：第一轮自动博弈逻辑
# ==========================================

def run_negotiation_round_1():
    # 1. 初始化本地灵魂逻辑
    soul = parser.get_soul_logic()
    my_deadline = soul["deadlines"].get("profit_share_min", 0.3)
    system_prompt = soul["prompt"]

    # 2. 模拟接收到的“外部节点”报价 (假设对方开价 20% 分成)
    incoming_offer = 0.20
    print(f"📡 接收到外部节点请求：当前报价 {incoming_offer*100}%")

    # 3. 激活“黑盒博弈”判定
    # 机器人会自动对比本地 protocol.json 中的死线
    if incoming_offer < my_deadline:
        decision = "拒绝并反击"
        # 自动生成符合《山海经》隐喻的回应意图
        counter_response = (
            f"基于底线 {my_deadline*100}%，报价过低。 "
            f"意图：引用《山海经》中'精卫填海'的执着，暗示价值对等，要求重新审视。"
        )
    else:
        decision = "初步达成共识"
        counter_response = "报价符合预期，准备进入下一阶段博弈。"

    # 4. 更新意图数据包至本地 protocol.json
    parser.update_intent(f"谈判状态：{decision}。回应内容：{counter_response}")

    # 5. 输出测试结果
    print(f"🤖 智能体决策：{decision}")
    print(f"📜 意图载荷 (Intent Payload)：{counter_response}")
    print(f"✅ 状态已同步至本地 shensist_protocol.json")

if __name__ == "__main__":
    # 确保环境变量已加载
    if not os.getenv("HF_TOKEN"):
        print("🚨 警告：主权令牌 HF_TOKEN 未检测到，请执行 source ~/.bashrc")
    else:
        run_negotiation_round_1()