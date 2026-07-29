"""
Code Agent - Thao tác với code: git, terminal, VSCode, build, run
"""

import os
import subprocess
import sys
from pathlib import Path
from service.agent import BaseAgent, ToolSchema, ToolResult, RiskLevel


class CodeAgent(BaseAgent):
    """Agent thao tác code & terminal"""
    
    agent_name = "code"
    agent_description = "Git, terminal, VSCode, build, run project"
    
    def __init__(self):
        super().__init__()
        
        self.register_tool(
            ToolSchema(
                name="run_command",
                description="Chạy lệnh terminal và trả về output",
                parameters={
                    "command": {"type": "string", "description": "Lệnh cần chạy"},
                    "cwd": {"type": "string", "description": "Working directory (tùy chọn)"}
                },
                risk_level=RiskLevel.CONFIRM,
                estimated_time=5.0
            ),
            self._run_command
        )
        
        self.register_tool(
            ToolSchema(
                name="open_terminal",
                description="Mở terminal mới tại thư mục chỉ định",
                parameters={"path": {"type": "string", "description": "Đường dẫn mở terminal"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=1.0
            ),
            self._open_terminal
        )
        
        self.register_tool(
            ToolSchema(
                name="git_status",
                description="Kiểm tra trạng thái git repository",
                parameters={"path": {"type": "string", "description": "Đường dẫn repo (mặc định: current)"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=1.0
            ),
            self._git_status
        )
        
        self.register_tool(
            ToolSchema(
                name="git_pull",
                description="Git pull từ remote",
                parameters={"path": {"type": "string", "description": "Đường dẫn repo"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=5.0
            ),
            self._git_pull
        )
        
        self.register_tool(
            ToolSchema(
                name="git_push",
                description="Git push lên remote",
                parameters={
                    "path": {"type": "string", "description": "Đường dẫn repo"},
                    "message": {"type": "string", "description": "Commit message"}
                },
                risk_level=RiskLevel.CONFIRM,
                estimated_time=5.0
            ),
            self._git_push
        )
        
        self.register_tool(
            ToolSchema(
                name="open_vscode",
                description="Mở VSCode tại thư mục hoặc file",
                parameters={"path": {"type": "string", "description": "Đường dẫn mở trong VSCode"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=2.0
            ),
            self._open_vscode
        )
        
        self.register_tool(
            ToolSchema(
                name="run_python",
                description="Chạy file Python",
                parameters={
                    "file": {"type": "string", "description": "Đường dẫn file .py"},
                    "args": {"type": "string", "description": "Arguments (tùy chọn)"}
                },
                risk_level=RiskLevel.CONFIRM,
                estimated_time=10.0
            ),
            self._run_python
        )
    
    def _run_command(self, command: str, cwd: str = None) -> ToolResult:
        """Chạy lệnh terminal"""
        try:
            result = subprocess.run(
                command, shell=True, cwd=cwd,
                capture_output=True, text=True, timeout=30
            )
            output = result.stdout.strip() or result.stderr.strip()
            if not output:
                output = f"Lệnh hoàn thành (exit code: {result.returncode})"
            
            return ToolResult(success=result.returncode == 0, data={
                "text": output,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            })
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Lệnh chạy quá 30 giây, đã timeout")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _open_terminal(self, path: str = None) -> ToolResult:
        """Mở terminal"""
        try:
            if not path:
                path = os.getcwd()
            
            if sys.platform == "win32":
                subprocess.Popen(["wt", "-d", path] if self._has_wt() else ["start", "cmd", "/k", f"cd /d {path}"], shell=True)
            else:
                subprocess.Popen(["gnome-terminal", "--working-directory", path])
            
            return ToolResult(success=True, data={"text": f"Đã mở terminal tại {path}"})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _has_wt(self):
        try:
            result = subprocess.run(["where", "wt"], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _git_status(self, path: str = None) -> ToolResult:
        """Git status"""
        try:
            if not path:
                path = os.getcwd()
            result = subprocess.run(["git", "status", "--short"], cwd=path, capture_output=True, text=True)
            output = result.stdout.strip()
            if not output:
                output = "Working tree clean"
            return ToolResult(success=True, data={"text": output, "changes": output.split("\n") if output else []})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _git_pull(self, path: str = None) -> ToolResult:
        """Git pull"""
        try:
            if not path:
                path = os.getcwd()
            result = subprocess.run(["git", "pull"], cwd=path, capture_output=True, text=True, timeout=30)
            output = result.stdout.strip() or result.stderr.strip()
            return ToolResult(success=result.returncode == 0, data={"text": output})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _git_push(self, path: str = None, message: str = "Update") -> ToolResult:
        """Git push"""
        try:
            if not path:
                path = os.getcwd()
            subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
            subprocess.run(["git", "commit", "-m", message], cwd=path, capture_output=True)
            result = subprocess.run(["git", "push"], cwd=path, capture_output=True, text=True, timeout=30)
            output = result.stdout.strip() or result.stderr.strip()
            return ToolResult(success=result.returncode == 0, data={"text": output})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _open_vscode(self, path: str) -> ToolResult:
        """Mở VSCode"""
        try:
            subprocess.Popen(["code", path], shell=True)
            return ToolResult(success=True, data={"text": f"Đã mở VSCode tại {path}"})
        except Exception as e:
            # Fallback: mở folder bằng explorer
            try:
                os.startfile(path)
                return ToolResult(success=True, data={"text": f"Đã mở {path} (không tìm thấy VSCode)"})
            except:
                return ToolResult(success=False, error=str(e))
    
    def _run_python(self, file: str, args: str = "") -> ToolResult:
        """Chạy file Python"""
        try:
            cmd = f"{sys.executable} {file} {args}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            output = result.stdout.strip() or result.stderr.strip()
            return ToolResult(success=result.returncode == 0, data={
                "text": output,
                "exit_code": result.returncode
            })
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Script chạy quá 60 giây")
        except Exception as e:
            return ToolResult(success=False, error=str(e))