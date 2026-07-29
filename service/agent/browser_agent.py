"""
Browser Agent - Thao tác với trình duyệt: mở URL, tìm kiếm, download
"""

import webbrowser
import sys
import subprocess
from service.agent import BaseAgent, ToolSchema, ToolResult, RiskLevel


class BrowserAgent(BaseAgent):
    """Agent điều khiển trình duyệt"""
    
    agent_name = "browser"
    agent_description = "Mở URL, tìm kiếm web, YouTube, download"
    
    def __init__(self):
        super().__init__()
        
        self.register_tool(
            ToolSchema(
                name="open_website",
                description="Mở website trong trình duyệt mặc định",
                parameters={"url": {"type": "string", "description": "URL hoặc tên website (vd: github.com, youtube)"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=2.0
            ),
            self._open_website
        )
        
        self.register_tool(
            ToolSchema(
                name="web_search",
                description="Tìm kiếm trên Google",
                parameters={"query": {"type": "string", "description": "Từ khóa tìm kiếm"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=2.0
            ),
            self._web_search
        )
        
        self.register_tool(
            ToolSchema(
                name="youtube_search",
                description="Tìm kiếm trên YouTube",
                parameters={"query": {"type": "string", "description": "Từ khóa tìm kiếm"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=2.0
            ),
            self._youtube_search
        )
        
        self.register_tool(
            ToolSchema(
                name="open_chrome",
                description="Mở Chrome với URL cụ thể",
                parameters={"url": {"type": "string", "description": "URL cần mở (tùy chọn)"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=2.0
            ),
            self._open_chrome
        )
    
    def _normalize_url(self, url: str) -> str:
        """Chuẩn hóa URL"""
        url = url.strip()
        
        # Domain mapping
        domain_map = {
            "google": "google.com",
            "youtube": "youtube.com",
            "facebook": "facebook.com",
            "github": "github.com",
            "gmail": "gmail.com",
            "outlook": "outlook.com",
            "twitter": "twitter.com",
            "instagram": "instagram.com",
            "reddit": "reddit.com",
            "stackoverflow": "stackoverflow.com",
            "chatgpt": "chat.openai.com",
            "copilot": "copilot.microsoft.com",
            "zalo": "zalo.me",
        }
        
        url_lower = url.lower().rstrip('/')
        if url_lower in domain_map:
            url = domain_map[url_lower]
        
        if not url.startswith("http"):
            url = "https://" + url
        
        return url
    
    def _open_website(self, url: str) -> ToolResult:
        """Mở website"""
        try:
            url = self._normalize_url(url)
            webbrowser.open(url)
            return ToolResult(success=True, data={"text": f"Đã mở {url}", "url": url})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _web_search(self, query: str) -> ToolResult:
        """Tìm kiếm Google"""
        try:
            import urllib.parse
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(search_url)
            return ToolResult(success=True, data={"text": f"Đã tìm kiếm: {query}", "url": search_url})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _youtube_search(self, query: str) -> ToolResult:
        """Tìm kiếm YouTube"""
        try:
            import urllib.parse
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            webbrowser.open(search_url)
            return ToolResult(success=True, data={"text": f"Đã tìm YouTube: {query}", "url": search_url})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _open_chrome(self, url: str = "") -> ToolResult:
        """Mở Chrome"""
        try:
            chrome_paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
            ]
            
            chrome_exe = None
            for path in chrome_paths:
                import os
                if os.path.exists(path):
                    chrome_exe = path
                    break
            
            if not chrome_exe:
                # Fallback: dùng webbrowser
                if url:
                    url = self._normalize_url(url)
                webbrowser.open(url or "https://google.com")
                return ToolResult(success=True, data={"text": "Đã mở trình duyệt"})
            
            if url:
                url = self._normalize_url(url)
                subprocess.Popen([chrome_exe, url])
            else:
                subprocess.Popen([chrome_exe])
            
            return ToolResult(success=True, data={"text": f"Đã mở Chrome {url if url else ''}"})
        except Exception as e:
            return ToolResult(success=False, error=str(e))