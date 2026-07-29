"""
Test Burst Habit Activation - Demo cho thuyết trình

Mô phỏng: TẤT CẢ user mở 1 app 6 lần trong ngày hôm nay
→ Burst detection kích hoạt → Thói quen được tạo với confidence cao
→ Khi mở app, bot tự động gợi ý trong lời chào

Cách dùng:
    python tests/test_burst_habit.py [app_name] [times]
    python tests/test_burst_habit.py chrome 6        # Mặc định
    python tests/test_burst_habit.py vscode 8         # App + số lần khác
    python tests/test_burst_habit.py --all            # Áp dụng cho TẤT CẢ account
    python tests/test_burst_habit.py --all chrome 6   # Tất cả account + app cụ thể
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

workspace_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(workspace_root))

from controller.habit_tracker import get_habit_tracker
from database.habit_repository import HabitRepository
from service.habit.habit_learning_service import HabitLearningService


def get_all_user_ids(repo: HabitRepository) -> list:
    """Lấy danh sách tất cả user_id từ database (từ mọi bảng có thể)."""
    ids = set()
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Từ bảng users (cột maNguoiDung)
            try:
                cursor.execute("SELECT maNguoiDung FROM users")
                for row in cursor.fetchall():
                    ids.add(row[0])
            except Exception:
                pass
            
            # 2. Từ bảng sessions (cột maNguoiDung)
            try:
                cursor.execute("SELECT DISTINCT maNguoiDung FROM sessions")
                for row in cursor.fetchall():
                    ids.add(row[0])
            except Exception:
                pass
            
            # 3. Từ bảng conversations (cột maNguoiDung)
            try:
                cursor.execute("SELECT DISTINCT maNguoiDung FROM conversations")
                for row in cursor.fetchall():
                    ids.add(row[0])
            except Exception:
                pass
            
            # 4. Từ bảng app_usage_logs (cột maNguoiDung)
            try:
                cursor.execute("SELECT DISTINCT maNguoiDung FROM app_usage_logs")
                for row in cursor.fetchall():
                    ids.add(row[0])
            except Exception:
                pass
            
            # 5. Từ bảng user_habits (cột maNguoiDung)
            try:
                cursor.execute("SELECT DISTINCT maNguoiDung FROM user_habits")
                for row in cursor.fetchall():
                    ids.add(row[0])
            except Exception:
                pass
            
            # Luôn có ít nhất user_id=1
            if not ids:
                ids = {1}
            
            return sorted(ids)
    except Exception as e:
        print(f"    Lỗi lấy danh sách user: {e}")
        return [1]


def simulate_burst_for_user(tracker, repo, user_id: int, app_name: str, times: int, verbose: bool = True):
    """Mô phỏng burst usage cho 1 user cụ thể."""
    now = datetime.now()
    
    # Xóa dữ liệu cũ của app này trong hôm nay
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM app_usage_logs
                WHERE maNguoiDung = ? AND tenUngDung = ? AND DATE(thoiGianMo) = DATE('now')
            """, (user_id, app_name))
            conn.commit()
    except Exception:
        pass
    
    # Mô phỏng mở app N lần
    for i in range(times):
        tracker.log_app_opened(user_id, app_name)
    
    # Kiểm tra kết quả
    today_count = repo.get_today_app_count(user_id, app_name)
    habit = repo.find_habit(user_id, 'app_usage', app_name, now.hour, now.weekday())
    
    if habit:
        _, freq, conf, _ = habit
        if verbose:
            status = "BURST ACTIVATED!" if conf >= HabitLearningService.BURST_CONFIDENCE_BOOST else f"conf={conf:.3f}"
            print(f"    User {user_id:3d}: {app_name} - {today_count} lần, {status}")
        return True, conf
    else:
        if verbose:
            print(f"    User {user_id:3d}: {app_name} - {today_count} lần, chưa có habit")
        return False, 0.0


def simulate_burst_usage_all(app_name: str = "chrome", times: int = 6):
    """
    Áp dụng burst usage cho TẤT CẢ account hiện có trong database.
    """
    tracker = get_habit_tracker()
    repo = tracker._repo
    
    print("=" * 60)
    print("  BURST HABIT - ÁP DỤNG CHO TẤT CẢ ACCOUNT")
    print("=" * 60)
    print(f"  App        : {app_name}")
    print(f"  Số lần mở  : {times}")
    print(f"  Ngưỡng kích hoạt: {HabitLearningService.BURST_THRESHOLD} lần/ngày")
    print("=" * 60)
    print()
    
    # Lấy tất cả user
    all_users = get_all_user_ids(repo)
    print(f"[1] Tìm thấy {len(all_users)} account: {all_users}")
    print()
    
    # Áp dụng cho từng user
    print(f"[2] Mô phỏng mở '{app_name}' {times} lần cho từng account...")
    success_count = 0
    results = {}
    
    for user_id in all_users:
        ok, conf = simulate_burst_for_user(tracker, repo, user_id, app_name, times)
        results[user_id] = (ok, conf)
        if ok and conf >= HabitLearningService.BURST_CONFIDENCE_BOOST:
            success_count += 1
    
    # Tổng kết
    print(f"\n[3] KẾT QUẢ:")
    print("-" * 40)
    print(f"    Tổng account: {len(all_users)}")
    print(f"    Đã kích hoạt: {success_count}")
    print(f"    Thất bại    : {len(all_users) - success_count}")
    
    # Hiển thị gợi ý cho từng user
    print(f"\n[4] GỢI Ý CHO TỪNG ACCOUNT:")
    print("-" * 40)
    for user_id in all_users:
        suggestions = tracker.get_suggestions(user_id)
        if suggestions:
            top = suggestions[0]
            print(f"    User {user_id}: {top.get('message', 'N/A')}")
        else:
            print(f"    User {user_id}: Chưa có gợi ý")
    
    print(f"\n{'=' * 60}")
    print(f"  HOÀN TẤT! {success_count}/{len(all_users)} account đã sẵn sàng!")
    print(f"  Khi mở app với bất kỳ account nào, bot sẽ gợi ý '{app_name}'")
    print(f"  Account mới cũng sẽ được tự động thêm khi chạy lại test!")
    print(f"{'=' * 60}")
    
    return results


def simulate_burst_usage_single(user_id: int = 1, app_name: str = "chrome", times: int = 6):
    """Mô phỏng burst usage cho 1 user (giữ lại để tương thích)."""
    tracker = get_habit_tracker()
    repo = tracker._repo
    
    print("=" * 60)
    print("  BURST HABIT ACTIVATION TEST - DEMO THUYẾT TRÌNH")
    print("=" * 60)
    print(f"  User ID    : {user_id}")
    print(f"  App        : {app_name}")
    print(f"  Số lần mở  : {times}")
    print(f"  Ngưỡng kích hoạt: {HabitLearningService.BURST_THRESHOLD} lần/ngày")
    print("=" * 60)
    print()
    
    ok, conf = simulate_burst_for_user(tracker, repo, user_id, app_name, times)
    
    # Kết quả
    now = datetime.now()
    today_count = repo.get_today_app_count(user_id, app_name)
    habit = repo.find_habit(user_id, 'app_usage', app_name, now.hour, now.weekday())
    
    print(f"\n[KẾT QUẢ]")
    print(f"    Số lần mở hôm nay: {today_count}")
    if habit:
        _, freq, conf_val, _ = habit
        print(f"    Thói quen: frequency={freq}, confidence={conf_val:.3f}")
        if conf_val >= 0.6:
            print(f"\n   *** THÓI QUEN ĐÃ ĐƯỢC KÍCH HOẠT! ***")
    
    suggestions = tracker.get_suggestions(user_id)
    if suggestions:
        print(f"\n[GỢI Ý] {suggestions[0].get('message', '')}")
    
    print(f"\n{'=' * 60}")
    print(f"  Mở app để bot tự động gợi ý '{app_name}'!")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    args = sys.argv[1:]
    
    # Lấy repo trước để có danh sách user
    tracker = get_habit_tracker()
    repo = tracker._repo
    all_users = get_all_user_ids(repo)
    
    # Kiểm tra flag --all
    if '--all' in args:
        args.remove('--all')
        app_name = args[0] if len(args) > 0 else "chrome"
        times = int(args[1]) if len(args) > 1 else 6
        simulate_burst_usage_all(app_name, times)
    elif '--list' in args:
        # Hiển thị danh sách account
        print("=" * 50)
        print("  DANH SÁCH ACCOUNT")
        print("=" * 50)
        with repo._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT maNguoiDung, tenNguoiDung FROM users ORDER BY maNguoiDung")
            for row in c.fetchall():
                print(f"  ID={row[0]:3d}  |  {row[1]}")
        print("=" * 50)
        print(f"  Tổng: {len(all_users)} account")
        print()
        print("Dùng: python tests/test_burst_habit.py <ID> <app> <số_lần>")
        print("Hoặc: python tests/test_burst_habit.py --all")
    elif len(args) == 0:
        # Interactive mode: cho người dùng chọn account
        print("=" * 50)
        print("  BURST HABIT TEST - CHỌN ACCOUNT")
        print("=" * 50)
        with repo._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT maNguoiDung, tenNguoiDung FROM users ORDER BY maNguoiDung")
            users_list = c.fetchall()
            for row in users_list:
                print(f"  [{row[0]:3d}] {row[1]}")
        print(f"  [ 0 ] TẤT CẢ ({len(users_list)} account)")
        print("-" * 50)
        
        try:
            choice = input("  Chọn ID (0 = tất cả, Enter = 1): ").strip()
            if choice == '':
                user_id = 1
            else:
                user_id = int(choice)
        except (ValueError, EOFError):
            user_id = 1
        
        app_name = input("  App (Enter = chrome): ").strip() or "chrome"
        try:
            times = int(input("  Số lần mở (Enter = 6): ").strip() or "6")
        except ValueError:
            times = 6
        
        print()
        if user_id == 0:
            simulate_burst_usage_all(app_name, times)
        else:
            simulate_burst_usage_single(user_id, app_name, times)
    else:
        # Chế độ command line: python test_burst_habit.py <user_id> <app> <times>
        user_id = int(args[0]) if len(args) > 0 else 1
        app_name = args[1] if len(args) > 1 else "chrome"
        times = int(args[2]) if len(args) > 2 else 6
        simulate_burst_usage_single(user_id, app_name, times)