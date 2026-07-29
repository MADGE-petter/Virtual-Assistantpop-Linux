"""
Memory System - 3 tầng: Working + Short-term + Long-term (Vector)
Lưu trữ context, lịch sử, workflow đã học, sở thích người dùng
"""

import json
import os
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


# === WORKING MEMORY (phiên hiện tại) ===

@dataclass
class WorkingMemory:
    """Bộ nhớ tạm cho phiên hiện tại - RAM only"""
    user_name: str = ""
    current_goal: str = ""
    conversation_history: list[dict] = field(default_factory=list)
    pending_actions: list = field(default_factory=list)
    user_preferences: dict = field(default_factory=dict)
    last_context: dict = field(default_factory=dict)
    
    def add_exchange(self, user_text: str, bot_text: str, intent: str = ""):
        self.conversation_history.append({
            "user": user_text,
            "bot": bot_text,
            "intent": intent,
            "timestamp": time.time()
        })
        # Giữ tối đa 20 exchanges trong working memory
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def get_recent_context(self, n: int = 5) -> str:
        """Lấy n hội thoại gần nhất làm context cho LLM"""
        recent = self.conversation_history[-n:]
        lines = []
        for ex in recent:
            lines.append(f"User: {ex['user']}")
            lines.append(f"Bot: {ex['bot']}")
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "user_name": self.user_name,
            "current_goal": self.current_goal,
            "conversation_history": self.conversation_history,
            "user_preferences": self.user_preferences,
            "last_context": self.last_context
        }


# === SHORT-TERM MEMORY (SQLite, vài ngày) ===

class ShortTermMemory:
    """Lịch sử hội thoại gần đây - dùng SQLite có sẵn"""
    
    def __init__(self, sql_service=None):
        self._sql = sql_service
    
    def set_sql(self, sql_service):
        self._sql = sql_service
    
    def get_recent_conversations(self, limit: int = 10) -> list[dict]:
        """Lấy hội thoại gần đây từ DB"""
        if not self._sql:
            return []
        try:
            return self._sql.get_recent_conversations(limit)
        except:
            return []
    
    def save_exchange(self, user_text: str, bot_text: str, intent: str, session_id: str):
        if self._sql:
            try:
                self._sql.save_conversation(user_text, bot_text, intent, session_id)
            except:
                pass


# === LONG-TERM MEMORY (Vector + Workflow Store) ===

class LongTermMemory:
    """
    Bộ nhớ dài hạn:
    - Vector memory: sự kiện, sở thích, facts về user
    - Workflow store: lưu workflow đã học để tái sử dụng
    """
    
    def __init__(self, storage_dir: str = "memory"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.workflow_file = self.storage_dir / "workflows.json"
        self.facts_file = self.storage_dir / "facts.json"
        self.preferences_file = self.storage_dir / "preferences.json"
        
        self._workflows: dict[str, dict] = self._load_json(self.workflow_file)
        self._facts: list[dict] = self._load_json(self.facts_file)
        self._preferences: dict = self._load_json(self.preferences_file)
    
    def _load_json(self, path: Path) -> dict | list:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {} if 'workflow' in path.name or 'preferences' in path.name else []
    
    def _save_json(self, path: Path, data):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    # === WORKFLOW STORE ===
    
    def save_workflow(self, name: str, plan: dict):
        """Lưu workflow để tái sử dụng"""
        self._workflows[name] = {
            "name": name,
            "plan": plan,
            "created_at": time.time(),
            "last_used": time.time(),
            "use_count": self._workflows.get(name, {}).get("use_count", 0) + 1
        }
        self._save_json(self.workflow_file, self._workflows)
    
    def get_workflow(self, name: str) -> Optional[dict]:
        """Lấy workflow đã lưu"""
        wf = self._workflows.get(name)
        if wf:
            wf["last_used"] = time.time()
            self._save_json(self.workflow_file, self._workflows)
        return wf
    
    def find_workflow(self, query: str) -> Optional[dict]:
        """Tìm workflow gần nhất với query (fuzzy match)"""
        query_lower = query.lower()
        best_match = None
        best_score = 0
        
        for name, wf in self._workflows.items():
            # Simple word overlap score
            name_words = set(name.lower().split())
            query_words = set(query_lower.split())
            overlap = len(name_words & query_words)
            if overlap > best_score:
                best_score = overlap
                best_match = wf
        
        return best_match if best_score >= 2 else None
    
    def list_workflows(self) -> list[str]:
        return list(self._workflows.keys())
    
    def delete_workflow(self, name: str):
        if name in self._workflows:
            del self._workflows[name]
            self._save_json(self.workflow_file, self._workflows)
    
    # === FACTS ===
    
    def add_fact(self, fact: str, category: str = "general", source: str = "conversation"):
        """Lưu 1 fact về user hoặc thế giới"""
        self._facts.append({
            "fact": fact,
            "category": category,
            "source": source,
            "timestamp": time.time()
        })
        # Giới hạn 1000 facts
        if len(self._facts) > 1000:
            self._facts = self._facts[-1000:]
        self._save_json(self.facts_file, self._facts)
    
    def get_facts(self, category: str = None, limit: int = 20) -> list[str]:
        """Lấy facts, có thể lọc theo category"""
        facts = self._facts
        if category:
            facts = [f for f in facts if f.get("category") == category]
        return [f["fact"] for f in facts[-limit:]]
    
    def search_facts(self, query: str, limit: int = 5) -> list[str]:
        """Tìm facts liên quan (simple keyword search)"""
        query_words = set(query.lower().split())
        scored = []
        for f in self._facts:
            fact_words = set(f["fact"].lower().split())
            score = len(query_words & fact_words)
            if score > 0:
                scored.append((score, f["fact"]))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [f[1] for f in scored[:limit]]
    
    # === PREFERENCES ===
    
    def set_preference(self, key: str, value):
        self._preferences[key] = value
        self._save_json(self.preferences_file, self._preferences)
    
    def get_preference(self, key: str, default=None):
        return self._preferences.get(key, default)
    
    def get_all_preferences(self) -> dict:
        return dict(self._preferences)


# === MEMORY AGENT ===

class MemoryAgent:
    """
    Memory Agent - quản lý tất cả các tầng memory.
    Cung cấp context cho Planner và lưu kết quả học được.
    """
    
    agent_name = "memory"
    agent_description = "Quản lý bộ nhớ ngắn hạn, dài hạn và workflow"
    
    def __init__(self, sql_service=None, storage_dir: str = "memory"):
        self.working = WorkingMemory()
        self.short_term = ShortTermMemory(sql_service)
        self.long_term = LongTermMemory(storage_dir)
        self._login_username = None
        self._display_name = None
    
    def set_sql(self, sql_service):
        self.short_term.set_sql(sql_service)
    
    def set_user_context(self, login_username: str = None, display_name: str = None):
        """Set user context cho memory"""
        self._login_username = login_username
        self._display_name = display_name or "bạn"
        self.working.user_name = login_username or display_name or "bạn"
    
    # === Context cho Planner ===
    
    def get_planner_context(self) -> dict:
        """Tổng hợp context cho Planner Agent"""
        return {
            "user_name": self.working.user_name,
            "recent_conversation": self.working.get_recent_context(5),
            "user_preferences": self.long_term.get_all_preferences(),
            "relevant_facts": self._get_relevant_facts(),
            "saved_workflows": self.long_term.list_workflows(),
            "current_goal": self.working.current_goal
        }
    
    def _get_relevant_facts(self) -> list[str]:
        """Lấy facts liên quan đến context hiện tại"""
        if self.working.conversation_history:
            last_user = self.working.conversation_history[-1].get("user", "")
            return self.long_term.search_facts(last_user, limit=3)
        return self.long_term.get_facts(limit=5)
    
    # === Học từ hội thoại ===
    
    def learn_from_exchange(self, user_text: str, bot_text: str, intent: str):
        """Học từ mỗi lượt hội thoại"""
        self.working.add_exchange(user_text, bot_text, intent)
        
        # Trích xuất facts đơn giản
        if "tôi là" in user_text.lower() or "tên tôi là" in user_text.lower():
            import re
            name_match = re.search(r'(?:tôi là|tên tôi là|gọi tôi là)\s+(\w+)', user_text.lower())
            if name_match:
                name = name_match.group(1)
                self.working.user_name = name
                self.long_term.add_fact(f"User tên là {name}", "user_info")
                self.long_term.set_preference("user_name", name)
        
        if "thích" in user_text.lower():
            self.long_term.add_fact(user_text, "preference")
    
    def learn_workflow(self, name: str, plan_dict: dict):
        """Lưu workflow đã thực hiện thành công"""
        self.long_term.save_workflow(name, plan_dict)
    
    def find_saved_workflow(self, user_request: str) -> Optional[dict]:
        """Tìm workflow đã lưu khớp với yêu cầu"""
        return self.long_term.find_workflow(user_request)