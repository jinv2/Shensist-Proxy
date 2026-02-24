import json
import os
from pathlib import Path

class ShensistProtocolParser:
    def __init__(self, protocol_path="shensist_protocol.json"):
        self.protocol_path = Path(protocol_path)
        self.config = self._load_protocol()

    def _load_protocol(self):
        """加载协议文件，若不存在则初始化默认主权模板"""
        if not self.protocol_path.exists():
            print(f"🚨 协议文件缺失，正在初始化神思庭主权模板...")
            return {}
        
        with open(self.protocol_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_soul_logic(self):
        """提取智能体博弈的核心灵魂逻辑"""
        soul = self.config.get("soul_kernel", {})
        return {
            "prompt": f"{soul.get('core_logic')}。风格：{soul.get('interaction_style')}。",
            "deadlines": soul.get("negotiation_deadlines", {})
        }

    def get_api_endpoint(self, slot_name):
        """获取算力插槽地址，优先处理环境变量"""
        slot_value = self.config.get("sensory_slots", {}).get(slot_name, "")
        if "os.getenv" in slot_value:
            # 动态解析环境变量，如 HF_TOKEN
            env_key = slot_value.split("'")[1]
            return os.getenv(env_key)
        return slot_value

    def update_intent(self, task_description):
        """动态更新博弈意图包"""
        self.config["intent_payload"]["current_task"] = task_description
        self.config["intent_payload"]["state"] = "ACTIVE"
        self._save_protocol()

    def _save_protocol(self):
        """将最新的意图状态回写本地，实现'节点记忆'"""
        with open(self.protocol_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

# 实例化解析器，供主程序调用
parser = ShensistProtocolParser()