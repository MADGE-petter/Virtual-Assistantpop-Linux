"""
System Agent - Giám sát và điều khiển hệ thống
CPU, RAM, Disk, Nhiệt độ, Process, Power
"""

import psutil
import sys
import os
from service.agent import BaseAgent, ToolSchema, ToolResult, RiskLevel
from utils.logger import get_logger

logger = get_logger(__name__)


class SystemAgent(BaseAgent):
    """Agent giám sát hệ thống"""
    
    agent_name = "system"
    agent_description = "Giám sát CPU, RAM, Disk, Nhiệt độ, quản lý tiến trình, điều khiển nguồn"
    
    def __init__(self):
        super().__init__()
        
        self.register_tool(
            ToolSchema(
                name="system_status",
                description="Lấy trạng thái hệ thống: CPU%, RAM%, Disk%, Nhiệt độ",
                parameters={},
                risk_level=RiskLevel.SAFE,
                estimated_time=0.5
            ),
            self._system_status
        )
        
        self.register_tool(
            ToolSchema(
                name="top_processes",
                description="Lấy danh sách tiến trình tốn nhiều CPU/RAM nhất",
                parameters={
                    "sort_by": {"type": "string", "description": "cpu hoặc ram"},
                    "limit": {"type": "integer", "description": "Số lượng tiến trình (mặc định 5)"}
                },
                risk_level=RiskLevel.SAFE,
                estimated_time=1.0
            ),
            self._top_processes
        )
        
        self.register_tool(
            ToolSchema(
                name="kill_process",
                description="Tắt 1 tiến trình theo tên",
                parameters={"name": {"type": "string", "description": "Tên tiến trình cần tắt"}},
                risk_level=RiskLevel.DANGEROUS,
                estimated_time=1.0
            ),
            self._kill_process
        )
        
        self.register_tool(
            ToolSchema(
                name="shutdown",
                description="Tắt máy tính",
                parameters={"delay": {"type": "integer", "description": "Delay giây trước khi tắt (mặc định 60)"}},
                risk_level=RiskLevel.DANGEROUS,
                estimated_time=1.0
            ),
            self._shutdown
        )
        
        self.register_tool(
            ToolSchema(
                name="restart",
                description="Khởi động lại máy tính",
                parameters={"delay": {"type": "integer", "description": "Delay giây (mặc định 60)"}},
                risk_level=RiskLevel.DANGEROUS,
                estimated_time=1.0
            ),
            self._restart
        )
        
        self.register_tool(
            ToolSchema(
                name="lock_screen",
                description="Khóa màn hình",
                parameters={},
                risk_level=RiskLevel.SAFE,
                estimated_time=0.5
            ),
            self._lock_screen
        )
    
    def _system_status(self) -> ToolResult:
        """Lấy trạng thái hệ thống"""
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            # Nhiệt độ
            temp = None
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            temp = entries[0].current
                            break
            except Exception as e:
                logger.error(f"[SystemAgent] sensors_temperatures error: {e}")
            
            # Pin
            battery = None
            try:
                bat = psutil.sensors_battery()
                if bat:
                    battery = bat.percent
            except Exception as e:
                logger.error(f"[SystemAgent] sensors_battery error: {e}")
            
            status_text = f"CPU: {cpu}%, RAM: {ram}%, Disk: {disk}%"
            if temp:
                status_text += f", Nhiệt độ: {temp}°C"
            if battery is not None:
                status_text += f", Pin: {battery}%"
            
            return ToolResult(success=True, data={
                "text": status_text,
                "cpu_percent": cpu,
                "ram_percent": ram,
                "disk_percent": disk,
                "temperature": temp,
                "battery": battery
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _top_processes(self, sort_by: str = "cpu", limit: int = 5) -> ToolResult:
        """Lấy top processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except Exception as e:
                    logger.error(f"[SystemAgent] process_iter error: {e}")
            else:
                processes.sort(key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)
            
            top = processes[:limit]
            lines = [f"Top {limit} tiến trình theo {'RAM' if sort_by == 'ram' else 'CPU'}:"]
            for p in top:
                lines.append(f"  {p['name']}: CPU {p.get('cpu_percent', 0) or 0:.1f}%, RAM {p.get('memory_percent', 0) or 0:.1f}%")
            
            return ToolResult(success=True, data={
                "text": "\n".join(lines),
                "processes": top
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _kill_process(self, name: str) -> ToolResult:
        """Tắt tiến trình"""
        try:
            killed = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if name.lower() in proc.info['name'].lower():
                        proc.kill()
                        killed.append(proc.info['name'])
                except Exception as e:
                    logger.error(f"[SystemAgent] kill process error: {e}")
            if killed:
                return ToolResult(success=True, data={"text": f"Đã tắt: {', '.join(killed)}"})
            return ToolResult(success=False, error=f"Không tìm thấy tiến trình: {name}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _shutdown(self, delay: int = 60) -> ToolResult:
        """Tắt máy"""
        try:
            if sys.platform == "win32":
                os.system(f"shutdown /s /t {delay}")
                return ToolResult(success=True, data={"text": f"Máy sẽ tắt sau {delay} giây"})
            else:
                os.system(f"shutdown -h +{delay // 60}")
                return ToolResult(success=True, data={"text": f"Máy sẽ tắt sau {delay} giây"})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _restart(self, delay: int = 60) -> ToolResult:
        """Khởi động lại"""
        try:
            if sys.platform == "win32":
                os.system(f"shutdown /r /t {delay}")
                return ToolResult(success=True, data={"text": f"Máy sẽ khởi động lại sau {delay} giây"})
            else:
                os.system(f"shutdown -r +{delay // 60}")
                return ToolResult(success=True, data={"text": f"Máy sẽ khởi động lại sau {delay} giây"})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _lock_screen(self) -> ToolResult:
        """Khóa màn hình"""
        try:
            if sys.platform == "win32":
                import ctypes
                ctypes.windll.user32.LockWorkStation()
                return ToolResult(success=True, data={"text": "Đã khóa màn hình"})
            else:
                os.system("gnome-screensaver-command -l || dm-tool lock")
                return ToolResult(success=True, data={"text": "Đã khóa màn hình"})
        except Exception as e:
            return ToolResult(success=False, error=str(e))