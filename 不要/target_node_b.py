import json
import time
import os

def receive_and_process_intent(filepath, my_pubkey):
    print("\n==================================================")
    print("      《神思庭·形意》 接收节点 B 上线 (Ubuntu)      ")
    print("==================================================")
    print(f"[*] 本地节点身份凭证: {my_pubkey}")
    print("[*] 正在监听 P2P 网络意图广播...\n")
    time.sleep(1.5) # 模拟网络监听延迟
    
    if not os.path.exists(filepath):
        print("[-] 未检测到网络广播信号。")
        return
        
    print("[+] 截获加密意图数据包！正在解密...")
    time.sleep(0.5)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        intent_data = json.load(f)
        
    # 核心安全机制：验证这个包是不是发给我的
    if intent_data['header']['receiver_pubkey'] != my_pubkey:
        print("[-] 警告：该意图不是发送给本节点的，已将其丢弃。")
        return
        
    sender = intent_data['header']['sender_pubkey']
    action = intent_data['intent_body']['action_type']
    demand = intent_data['intent_body']['core_demand']
    tone = intent_data['intent_body']['strategic_tone']
    
    print(f"\n[>>>] 成功解析来自 {sender} 的商业意图 [>>>]")
    print(f"      对方动作: {action}")
    print(f"      对方诉求: {demand}")
    print(f"      对方策略情绪: {tone}")
    
    print("\n[*] 正在触发本地权限库与商业底线限制...")
    time.sleep(1)
    print("[*] 正在调用大模型 API (云端算力) 构思反击策略...")
    time.sleep(2) # 模拟大模型思考与生成时间
    
    print("\n[<<<] 节点 B 决策生成完毕 [<<<]")
    print("      回复动作: COUNTER_OFFER (反向出价)")
    print("      回复意图: 同意神思庭《山海经》项目的独立署名权，但 30% 首付超出我方风控标准。提议 20% 首付，尾款按进度支付。")
    print("      多模态通道: 准备向 WSS 通道推流虚拟人面部反驳视频...")
    print("      执行状态: 已将反向意图加密并向网络广播！")
    print("\n==================================================")

if __name__ == "__main__":
    # 为了演示极简通信，这里通过读取刚才的 JSON 文件来模拟接收网络广播
    protocol_file = "shensist_protocol.json"
    
    # 节点 B 的公钥必须和协议里 target 的公钥对得上，否则会拒收
    my_node_pubkey = "0xShensist_Target_B_9999" 
    
    receive_and_process_intent(protocol_file, my_node_pubkey)