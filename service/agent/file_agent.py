"""
File Agent - Thao tác với file: mở, tìm, copy, move, rename, delete
"""

import os
import shutil
import glob
from pathlib import Path
from datetime import datetime
from service.agent import BaseAgent, ToolSchema, ToolResult, RiskLevel


class FileAgent(BaseAgent):
    """Agent thao tác file hệ thống"""
    
    agent_name = "file"
    agent_description = "Tìm, mở, copy, move, rename, delete file và folder"
    
    def __init__(self):
        super().__init__()
        
        self.register_tool(
            ToolSchema(
                name="open_file",
                description="Mở file hoặc folder gần đây",
                parameters={"name": {"type": "string", "description": "Tên file hoặc folder"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=1.0
            ),
            self._open_file
        )
        
        self.register_tool(
            ToolSchema(
                name="find_file",
                description="Tìm file theo tên trong thư mục",
                parameters={
                    "name": {"type": "string", "description": "Tên file cần tìm (hỗ trợ wildcard *)"},
                    "folder": {"type": "string", "description": "Thư mục tìm (mặc định Downloads)"}
                },
                risk_level=RiskLevel.SAFE,
                estimated_time=2.0
            ),
            self._find_file
        )
        
        self.register_tool(
            ToolSchema(
                name="copy_file",
                description="Copy file từ nguồn đến đích",
                parameters={
                    "source": {"type": "string", "description": "Đường dẫn nguồn"},
                    "destination": {"type": "string", "description": "Đường dẫn đích"}
                },
                risk_level=RiskLevel.SAFE,
                estimated_time=1.0
            ),
            self._copy_file
        )
        
        self.register_tool(
            ToolSchema(
                name="move_file",
                description="Di chuyển file từ nguồn đến đích",
                parameters={
                    "source": {"type": "string", "description": "Đường dẫn nguồn"},
                    "destination": {"type": "string", "description": "Đường dẫn đích"}
                },
                risk_level=RiskLevel.CONFIRM,
                estimated_time=1.0
            ),
            self._move_file
        )
        
        self.register_tool(
            ToolSchema(
                name="delete_file",
                description="Xóa file hoặc folder",
                parameters={"path": {"type": "string", "description": "Đường dẫn cần xóa"}},
                risk_level=RiskLevel.DANGEROUS,
                estimated_time=0.5
            ),
            self._delete_file
        )
        
        self.register_tool(
            ToolSchema(
                name="list_folder",
                description="Liệt kê nội dung thư mục",
                parameters={"path": {"type": "string", "description": "Đường dẫn thư mục"}},
                risk_level=RiskLevel.SAFE,
                estimated_time=0.5
            ),
            self._list_folder
        )
    
    def _open_file(self, name: str) -> ToolResult:
        """Mở file hoặc folder"""
        try:
            # Tìm trong Downloads và Desktop
            search_paths = [
                str(Path.home() / "Downloads"),
                str(Path.home() / "Desktop"),
                str(Path.home()),
            ]
            
            best_match = None
            best_time = 0
            
            for search_path in search_paths:
                if not os.path.exists(search_path):
                    continue
                for root, dirs, files in os.walk(search_path):
                    # Giới hạn depth
                    depth = root.replace(search_path, "").count(os.sep)
                    if depth > 2:
                        continue
                    
                    for f in files + dirs:
                        if name.lower() in f.lower():
                            full_path = os.path.join(root, f)
                            mtime = os.path.getmtime(full_path)
                            if mtime > best_time:
                                best_time = mtime
                                best_match = full_path
            
            if best_match:
                os.startfile(best_match)
                return ToolResult(success=True, data={"text": f"Đã mở {best_match}", "path": best_match})
            
            return ToolResult(success=False, error=f"Không tìm thấy: {name}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _find_file(self, name: str, folder: str = None) -> ToolResult:
        """Tìm file"""
        try:
            if not folder:
                folder = str(Path.home() / "Downloads")
            
            pattern = os.path.join(folder, f"**/{name}")
            matches = glob.glob(pattern, recursive=True)
            
            if matches:
                matches.sort(key=os.path.getmtime, reverse=True)
                top = matches[:10]
                lines = [f"Tìm thấy {len(matches)} file:"]
                for m in top:
                    size = os.path.getsize(m)
                    mtime = datetime.fromtimestamp(os.path.getmtime(m))
                    lines.append(f"  {m} ({size:,} bytes, {mtime:%Y-%m-%d %H:%M})")
                
                return ToolResult(success=True, data={
                    "text": "\n".join(lines),
                    "files": top,
                    "total": len(matches)
                })
            
            return ToolResult(success=False, error=f"Không tìm thấy file: {name}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _copy_file(self, source: str, destination: str) -> ToolResult:
        """Copy file"""
        try:
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            return ToolResult(success=True, data={"text": f"Đã copy {source} → {destination}"})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _move_file(self, source: str, destination: str) -> ToolResult:
        """Di chuyển file"""
        try:
            shutil.move(source, destination)
            return ToolResult(success=True, data={"text": f"Đã di chuyển {source} → {destination}"})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _delete_file(self, path: str) -> ToolResult:
        """Xóa file"""
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return ToolResult(success=True, data={"text": f"Đã xóa {path}"})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _list_folder(self, path: str) -> ToolResult:
        """Liệt kê thư mục"""
        try:
            items = os.listdir(path)
            files = []
            folders = []
            for item in items:
                full = os.path.join(path, item)
                if os.path.isdir(full):
                    folders.append(item)
                else:
                    size = os.path.getsize(full)
                    files.append((item, size))
            
            lines = [f"Nội dung {path}:"]
            if folders:
                lines.append(f"  📁 {len(folders)} thư mục: {', '.join(folders[:5])}")
            if files:
                files.sort(key=lambda x: x[1], reverse=True)
                lines.append(f"  📄 {len(files)} file:")
                for name, size in files[:10]:
                    lines.append(f"    {name} ({size:,} bytes)")
            
            return ToolResult(success=True, data={"text": "\n".join(lines), "items": items})
        except Exception as e:
            return ToolResult(success=False, error=str(e))