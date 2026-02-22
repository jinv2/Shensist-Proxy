import json
import time
import os

def load_protocol(filepath):
    print(f"[*] 节点系统自检中...")
    time.sleep(0.5)
    print(f"[*] 正在挂载本地意图协议文件: {filepath}")
    
    if not os.path.exists(filepath):
        print("[-] 致命错误：未找到协议文件，节点启动中止。")
        return None
        
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data

def simulate_web4_broadcast(intent_data):
    # 提取协议中的关键信息
    sender = intent_data['header']['sender_pubkey']
    receiver = intent_data['header']['receiver_pubkey']
    action = intent_data['intent_body']['action_type']
    demand = intent_data['intent_body']['core_demand']
    
    print("\n==================================================")
    print("      《神思庭·形意》 Web4 节点在线 (Ubuntu 25)      ")
    print("==================================================")
    print(f"[+] 本地节点身份凭证: {sender}")
    print("[+] 正在初始化去中心化 P2P 路由...")
    time.sleep(1) # 模拟寻址延迟
    
    print(f"\n[>] 发现目标节点: {receiver}")
    print("[>] 正在建立加密信道...")
    time.sleep(0.5)
    
    print("\n[>>>] 开始向网络广播加密意图 (Intent) [>>>]")
    print(f"      动作指令: {action}")
    print(f"      核心诉求: {demand}")
    print(f"      多模态通道状态: 语音 WSS 监听中...")
    
    print("\n[*] 意图数据包发送完毕。")
    print("[*] 节点进入静默监听状态，等待目标大模型 API 返回博弈结果...\n")

if __name__ == "__main__":
    protocol_file = "shensist_protocol.json"
    
    # 1. 读取刚才同步过来的 JSON 协议
    intent_payload = load_protocol(protocol_file)
    
    # 2. 如果读取成功，执行广播动作
    if intent_payload:
         simulate_web4_broadcast(intent_payload)