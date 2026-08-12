"""
Alert Manager - Orchestrator chính (đã gộp InteractiveAlertService)
"""

import re
import threading
import time
from typing import Callable, Dict, List, Optional, Union

import psutil

from database.alert_repository import AlertRepository
from utils.thread_manager import get_thread_manager
from utils.logger import get_logger

logger = get_logger(__name__)

from .checker import BatteryMonitor, CPUMonitor, DiskMonitor, RAMMonitor, TempMonitor
from .notifier import AlertNotifier
from .types import Alert, AlertLevel, AlertThreshold


class AlertManager:
    """Quản lý và điều phối hệ thống cảnh báo"""
    
    # Memory management
    MAX_ALERT_HISTORY = 100  # Giới hạn số lượng alert trong memory
    
    # Ngưỡng mặc định
    DEFAULT_THRESHOLDS = {
        'cpu': AlertThreshold('cpu', warning=80.0, critical=95.0),
        'ram': AlertThreshold('ram', warning=80.0, critical=90.0, danger=95.0),  # Interactive at >=80%
        'disk': AlertThreshold('disk', warning=85.0, critical=90.0, danger=95.0),
        'battery': AlertThreshold('battery', warning=20.0, critical=10.0),
        'temperature': AlertThreshold('temperature', warning=70.0, critical=80.0, danger=90.0)  # Interactive at >=80%
    }
    
    WELLNESS_SETTINGS = {
        'night_start_hour': 23,
        'night_end_hour': 2,
        'rest_suggestions': [
            "Bạn đã làm việc khuya rồi đấy. Nên nghỉ ngơi để giữ sức khỏe nhé!",
            "Khuya rồi! Hãy để mắt và cơ thể nghỉ ngơi nhé.",
            "Bạn có thấy mệt không? Nên ngủ sớm để mai còn làm việc.",
        ]
    }
    
    def __init__(self, audio_service=None, ui_callback: Optional[Callable] = None, 
                 check_interval: int = 60, user_name: str = "bạn", db_path: str = None,
                 interactive_callback: Optional[Callable] = None):
        self.audio_service = audio_service
        self.ui_callback = ui_callback
        self.interactive_callback = interactive_callback
        self.user_name = user_name
        
        # Database for alert persistence
        if db_path is None:
            import os
            self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'conversations.db')
        else:
            self.db_path = db_path
        
        # Initialize repository (Data Access Layer)
        self._alert_repo = AlertRepository(self.db_path)
        self._alert_repo._init_tables()
        
        # Thread safety - use RLock for reentrant locking
        self._lock = threading.RLock()
        
        # Cấu hình
        self.thresholds = dict(self.DEFAULT_THRESHOLDS)
        self.check_interval = check_interval
        self._wellness_enabled = True
        self._is_sleeping = False
        
        # Interactive alert state (merged from InteractiveAlertService)
        self._interactive_alerts: Dict[str, dict] = {}
        self._interactive_lock = threading.RLock()
        
        # Initialize alert persistence
        self._init_alert_persistence()
        
        # Trạng thái
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._alerts: List[Alert] = []
        self._last_alert_time: dict = {}
        self._last_wellness_alert: Optional[float] = None
        
        # Load alerts from database on startup
        self._load_alerts_from_memory()
        
        # Cleanup old alerts to prevent database bloat
        self.cleanup_old_alerts()
        
        # Khởi tạo notifier và monitors
        self.notifier = AlertNotifier(audio_service, ui_callback)
        self.monitors = [
            CPUMonitor(self.thresholds['cpu']),
            RAMMonitor(self.thresholds['ram']),
            DiskMonitor(self.thresholds['disk']),
            TempMonitor(self.thresholds['temperature']),
            BatteryMonitor(self.thresholds['battery'])
        ]
    
    def start(self):
        """Bắt đầu giám sát"""
        if not self._running:
            self._running = True
            self._monitor_thread = get_thread_manager("AlertManager").start_thread(
                self._monitor_loop,
                name="Alert-Monitor"
            )
            logger.info(f"[AlertManager] Started monitoring with {len(self.monitors)} monitors")
    
    def stop(self):
        """Dừng giám sát"""
        if self._running:
            self._running = False
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=5)
            logger.info("[AlertManager] Stopped monitoring")
    
    def _monitor_loop(self):
        """Vòng lặp giám sát chính"""
        while self._running:
            try:
                # Kiểm tra từng monitor
                for monitor in self.monitors:
                    alert, is_recovery = monitor.check()
                    
                    if alert:
                        if self._is_interactive_alert(alert):
                            self._handle_interactive_alert(alert)
                        elif self._should_alert(alert):
                            with self._lock:
                                self._alerts.append(alert)
                                self._record_alert(alert)
                                self._manage_alert_memory()
                                self._save_alert_to_db(alert)
                            self.notifier.notify(alert)
                    
                    elif is_recovery:
                        metric = monitor.threshold.metric
                        self._clear_interactive_alert(metric)
                        from datetime import datetime
                        self.notifier.speak_recovery(metric, f"{metric.upper()} đã trở lại bình thường")
                
                self._check_interactive_reminders()
                self._check_wellness()
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"[AlertManager] Monitor loop error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(self.check_interval)
    
    def _should_alert(self, alert) -> bool:
        """Kiểm tra cooldown 10 phút giữa các cảnh báo cùng metric và level"""
        key = f"{alert.metric}_{alert.level.value}"
        
        with self._lock:
            if key not in self._last_alert_time:
                return True
            
            cooldown = 600  # 10 phút
            return time.time() - self._last_alert_time[key] > cooldown
    
    def _record_alert(self, alert):
        """Ghi lại thời gian cảnh báo theo metric và level"""
        key = f"{alert.metric}_{alert.level.value}"
        with self._lock:
            self._last_alert_time[key] = time.time()
    
    def _manage_alert_memory(self):
        """Quản lý memory - xóa alert cũ nếu cần"""
        while len(self._alerts) > self.MAX_ALERT_HISTORY:
            self._alerts.pop(0)
    
    def get_memory_stats(self) -> dict:
        """Lấy thống kê memory usage"""
        with self._lock:
            return {
                'total_alerts': len(self._alerts),
                'max_history': self.MAX_ALERT_HISTORY,
                'memory_usage_percent': round(len(self._alerts) / self.MAX_ALERT_HISTORY * 100, 1),
                'cooldown_keys': len(self._last_alert_time),
                'oldest_alert_age': (time.time() - (self._alerts[0].timestamp.timestamp() if hasattr(self._alerts[0].timestamp, 'timestamp') else self._alerts[0].timestamp)) if self._alerts else 0
            }
    
    def _init_alert_persistence(self):
        """Khởi tạo alert persistence - delegated to repository"""
        # Tables are initialized in __init__ via self._alert_repo._init_tables()
        pass
    
    def _save_alert_to_db(self, alert: Alert):
        """Lưu alert vào database"""
        self._alert_repo.save_alert(
            alert.id,
            alert.metric,
            alert.level.value,
            alert.value,
            alert.message,
            alert.timestamp.timestamp() if hasattr(alert.timestamp, 'timestamp') else alert.timestamp,
            alert.acknowledged
        )
    
    def _load_alerts_from_db(self, limit: int = 100) -> List[Alert]:
        """Tải alerts từ database"""
        rows = self._alert_repo.load_alerts(limit)
        alerts = []
        for row in rows:
            from datetime import datetime
            alert = Alert(
                id=row['id'],
                metric=row['metric'],
                level=AlertLevel(row['level']),
                value=row['value'],
                message=row['message'],
                timestamp=datetime.fromtimestamp(row['timestamp'])
            )
            alert.acknowledged = row['acknowledged']
            alerts.append(alert)
        return alerts
    
    def _load_alerts_from_memory(self):
        """Tải alerts từ database vào memory khi khởi động"""
        try:
            alerts = self._load_alerts_from_db(self.MAX_ALERT_HISTORY)
            with self._lock:
                self._alerts = alerts
            logger.info(f"[AlertManager] Loaded {len(alerts)} alerts from database")
        except Exception as e:
            logger.error(f"[AlertManager] Error loading alerts from memory: {e}")
            with self._lock:
                self._alerts = []
    
    def _check_wellness(self):
        """Nhắc nghỉ ngơi khi khuya"""
        if not self._wellness_enabled or self._is_sleeping:
            return
            
        from datetime import datetime
        current_hour = datetime.now().hour
        settings = self.WELLNESS_SETTINGS
        
        if settings['night_start_hour'] <= current_hour or current_hour < settings['night_end_hour']:
            # Kiểm tra đã nhắc trong 30 phút chưa
            if self._last_wellness_alert:
                if time.time() - self._last_wellness_alert < 1800:
                    return
            
            import random
            msg = random.choice(settings['rest_suggestions'])
            self._last_wellness_alert = time.time()
            
            if self.audio_service:
                try:
                    self.audio_service.speak(msg)
                except Exception as e:
                    logger.error(f"[AlertManager] speak error: {e}")
    
    # Public API
    def set_sleep_mode(self, enabled: bool):
        self._is_sleeping = enabled
    
    def reset_wellness_timers(self):
        pass
    
    def enable_wellness(self, enabled: bool = True):
        self._wellness_enabled = enabled
    
    def get_active_alerts(self) -> List[Alert]:
        with self._lock:
            return [a for a in self._alerts if not a.acknowledged]
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge alert and sync to database"""
        # Update in RAM
        alert_found = False
        with self._lock:
            for alert in self._alerts:
                if alert.id == alert_id:
                    alert.acknowledged = True
                    alert_found = True
                    break
        
        # Update in database via repository
        if alert_found:
            if self._alert_repo.acknowledge_alert(alert_id):
                logger.info(f"[AlertManager] Alert {alert_id} acknowledged and synced to database")
        else:
            logger.warning(f"[AlertManager] Alert {alert_id} not found for acknowledgment")
    
    def get_system_status(self) -> dict:
        import psutil
        try:
            battery = psutil.sensors_battery()
            battery_info = {
                'percent': battery.percent if battery else None,
                'plugged': battery.power_plugged if battery else None
            }
        except Exception as e:
            logger.error(f"[AlertManager] sensors_battery error: {e}")
            battery_info = {'percent': None, 'plugged': None}
        
        return {
            'cpu': psutil.cpu_percent(interval=0.5),
            'ram': psutil.virtual_memory().percent,
            'disk': {p.mountpoint: psutil.disk_usage(p.mountpoint).percent 
                    for p in psutil.disk_partitions(all=False) 
                    if psutil.disk_usage(p.mountpoint)},
            'battery': battery_info,
            'active_alerts': len(self.get_active_alerts())
        }
    
    def cleanup_old_alerts(self, days_to_keep: int = 30, max_rows: int = 5000):
        """Clean old alerts from database to prevent unlimited growth
        
        Args:
            days_to_keep: Keep alerts newer than this many days
            max_rows: Keep maximum this many rows total
        """
        result = self._alert_repo.cleanup_old_alerts(days_to_keep, max_rows)
        if result['time_deleted'] > 0 or result['row_deleted'] > 0:
            logger.info(f"[AlertManager] Database cleanup completed: {result['time_deleted']} by time, {result['row_deleted']} by count")
        else:
            total = self._alert_repo.get_alert_count()
            logger.info(f"[AlertManager] No cleanup needed (total: {total} rows)")
    
    def clear_all_alerts(self):
        """Clear all alerts from both RAM and database"""
        # Clear RAM
        with self._lock:
            self._alerts.clear()
            self._last_alert_time.clear()
        
        # Clear database via repository
        if self._alert_repo.delete_all_alerts():
            logger.info(f"[AlertManager] Cleared all alerts from database and vacuumed")

    # ===== Interactive Alert Methods (merged from InteractiveAlertService) =====
    
    def _is_interactive_alert(self, alert: Alert) -> bool:
        return alert.metric in ["ram", "temperature"] and alert.value >= 80.0

    def _handle_interactive_alert(self, alert: Alert):
        metric = alert.metric

        with self._interactive_lock:
            if metric not in self._interactive_alerts:
                self._interactive_alerts[metric] = {
                    'alert': alert,
                    'state': 'waiting_confirmation',
                    'last_prompt': time.time(),
                    'reminder_count': 0
                }
                if self.interactive_callback:
                    self.interactive_callback(alert, 'ask_details')
            else:
                state = self._interactive_alerts[metric]
                if time.time() - state['last_prompt'] > 600:
                    state['last_prompt'] = time.time()
                    state['reminder_count'] += 1
                    if self.interactive_callback:
                        self.interactive_callback(alert, 'remind')

    def _check_interactive_reminders(self):
        current_time = time.time()

        with self._interactive_lock:
            for metric, state in list(self._interactive_alerts.items()):
                if current_time - state['last_prompt'] > 600:
                    state['last_prompt'] = current_time
                    state['reminder_count'] += 1
                    if self.interactive_callback:
                        self.interactive_callback(state['alert'], 'remind')

    def _clear_interactive_alert(self, metric: str):
        with self._interactive_lock:
            self._interactive_alerts.pop(metric, None)

    def handle_interactive_response(self, metric: str, response: str, context: dict = None):
        """Xử lý phản hồi từ người dùng cho interactive alert"""
        with self._interactive_lock:
            if metric not in self._interactive_alerts:
                return

            state = self._interactive_alerts[metric]
            alert = state['alert']

            if state['state'] == 'waiting_confirmation':
                if self._is_positive_response(response):
                    state['state'] = 'showing_details'
                    state['last_prompt'] = time.time()
                    if self.interactive_callback:
                        self.interactive_callback(alert, 'show_details')
                else:
                    state['last_prompt'] = time.time()

            elif state['state'] == 'showing_details':
                if self._is_positive_response(response):
                    state['state'] = 'waiting_close_selection'
                    state['last_prompt'] = time.time()
                    if self.interactive_callback:
                        self.interactive_callback(alert, 'ask_close_app')
                else:
                    state['last_prompt'] = time.time()

            elif state['state'] == 'waiting_close_selection':
                apps_to_close = self._parse_app_selection(response, context or {})
                if apps_to_close:
                    if isinstance(apps_to_close, list):
                        results = []
                        for app in apps_to_close:
                            success = self._close_process(app)
                            results.append((app, success))
                        succeeded = [app for app, ok in results if ok]
                        failed = [app for app, ok in results if not ok]
                        if succeeded:
                            del self._interactive_alerts[metric]
                            if self.interactive_callback:
                                self.interactive_callback(alert, 'close_success', {'closed_apps': succeeded, 'failed_apps': failed})
                        elif self.interactive_callback:
                            self.interactive_callback(alert, 'close_failed', {'failed_apps': failed})
                    else:
                        success = self._close_process(apps_to_close)
                        if success:
                            del self._interactive_alerts[metric]
                            if self.interactive_callback:
                                self.interactive_callback(alert, 'close_success', {'closed_app': apps_to_close})
                        else:
                            if self.interactive_callback:
                                self.interactive_callback(alert, 'close_failed', {'failed_app': apps_to_close})
                else:
                    if self.interactive_callback:
                        self.interactive_callback(alert, 'ask_close_app')

    def get_interactive_context(self, metric: str) -> dict:
        """Lấy context cho interactive alert (top processes)"""
        if metric not in self._interactive_alerts:
            return {}

        if self._interactive_alerts[metric]['state'] not in ['showing_details', 'waiting_close_selection']:
            return {}

        if metric == 'ram':
            from service.system_monitoring_service import get_top_ram_processes
            processes = get_top_ram_processes(5)
        else:
            from service.system_monitoring_service import get_top_cpu_processes
            processes = get_top_cpu_processes(5)

        return {'top_processes': processes}

    def get_active_interactive_metrics(self) -> list:
        """Lấy danh sách metric đang có interactive alert"""
        with self._interactive_lock:
            return list(self._interactive_alerts.keys())

    def _is_positive_response(self, response: str) -> bool:
        positive_words = ['có', 'yes', 'ok', 'được', 'ừ', 'vâng', 'tôi muốn', 'show', 'xem', 'đóng']
        negative_words = ['không', 'no', 'khỏi', 'thôi', 'bỏ qua', 'skip']
        response_lower = response.lower()
        for word in negative_words:
            if word in response_lower:
                return False
        for word in positive_words:
            if word in response_lower:
                return True
        return False

    def _parse_app_selection(self, response: str, context: dict) -> Optional[Union[dict, List[dict]]]:
        response_lower = response.lower()

        if 'top_processes' in context:
            top_processes = context['top_processes']
            selected = []

            matches = re.findall(r'\b(?:app|số)?\s*(\d+)\b', response_lower)
            for match in matches:
                app_index = int(match) - 1
                if 0 <= app_index < len(top_processes):
                    proc = top_processes[app_index]
                    if proc not in selected:
                        selected.append(proc)

            for proc in top_processes:
                if proc['name'].lower() in response_lower and proc not in selected:
                    selected.append(proc)

            if selected:
                return selected if len(selected) > 1 else selected[0]

        return None

    def _close_process(self, process_info: dict) -> bool:
        try:
            pid = process_info.get('pid')
            name = process_info.get('name')
            if pid:
                proc = psutil.Process(pid)
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    proc.kill()
                return True
            elif name:
                closed_count = 0
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if proc.info['name'] and name.lower() in proc.info['name'].lower():
                            proc.terminate()
                            closed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                return closed_count > 0
        except Exception as e:
            logger.error(f"[AlertManager] _close_process error: {e}")
            return False
        return False


# Singleton
_alert_manager: Optional[AlertManager] = None

def get_alert_manager(audio_service=None, ui_callback=None) -> AlertManager:
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager(audio_service, ui_callback)
    return _alert_manager
