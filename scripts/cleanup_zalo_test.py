"""
Script xóa dữ liệu test burst habit cho Zalo
Xóa các bản ghi app_usage_logs của Zalo trong ngày hôm nay
"""

import sys
import sqlite3
from pathlib import Path

workspace_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(workspace_root))

from database.db_manager import get_db_manager
from utils.logger import get_logger

logger = get_logger(__name__)

def cleanup_zalo_test_data():
    db = get_db_manager()
    
    logger.info("=" * 50)
    logger.info("  XOA DU LIEU TEST ZALO")
    logger.info("=" * 50)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Xoa app_usage_logs cua Zalo trong hom nay
        cursor.execute("""
            DELETE FROM app_usage_logs 
            WHERE tenUngDung LIKE '%zalo%' 
            AND DATE(thoiGianMo) = DATE('now')
        """)
        deleted_count = cursor.rowcount
        conn.commit()
        
        logger.info(f"  Da xoa: {deleted_count} ban ghi app_usage_logs cua Zalo")
        
        # Kiem tra con lai
        cursor.execute("""
            SELECT COUNT(*) FROM app_usage_logs 
            WHERE tenUngDung LIKE '%zalo%' 
            AND DATE(thoiGianMo) = DATE('now')
        """)
        remaining = cursor.fetchone()[0]
        logger.info(f"  Con lai: {remaining} ban ghi")
    
    logger.info("=" * 50)
    logger.info("  HOAN TAT!")

def check_app_usage():
    """Kiem tra du lieu su dung app hom nay"""
    db = get_db_manager()
    logger.info("\n" + "=" * 50)
    logger.info(" KIEM TRA DU LIEU APP USAGE HOM NAY")
    logger.info("=" * 50)
    with db.get_connection() as conn:
        cursor = conn.cursor()
        # Xem cac ung dung trong app_usage_logs hom nay
        cursor.execute("""
        SELECT DISTINCT tenUngDung, COUNT(*) as so_lan
        FROM app_usage_logs
        WHERE DATE(thoiGianMo) = DATE('now')
        GROUP BY tenUngDung
        """)
        logger.info("Ung dung trong ngay hom nay:")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                logger.info(f" {row[0]}: {row[1]} lan")
        else:
            logger.info(" Khong co du lieu")

        # Kiem tra tong so ban ghi
        cursor.execute("SELECT COUNT(*) FROM app_usage_logs")
        total = cursor.fetchone()[0]
        logger.info(f"\nTong so ban ghi: {total}")
        logger.info("=" * 50)

def check_all_zalo_data():
    """Kiem tra tat ca du lieu Zalo trong database"""
    db = get_db_manager()
    
    logger.info("\n" + "=" * 50)
    logger.info("  KIEM TRA Tat ca DU LIEU ZALO")
    logger.info("=" * 50)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Liet ke tat ca cac bang
        logger.info("\n[0] CAC BANG TRONG DATABASE:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for row in cursor.fetchall():
            logger.info("  %s", row[0])
        
        # Kiem tra user_habits
        logger.info("\n[1] USER_HABITS (zalo):")
        cursor.execute("SELECT * FROM user_habits WHERE tenMucTieu LIKE '%zalo%'")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                logger.info("  %s", row)
        else:
            logger.info("  Khong co du lieu")
        
        # Kiem tra suggestions (neu bang ton tai)
        logger.info("\n[2] SUGGESTIONS (zalo):")
        try:
            cursor.execute("SELECT * FROM suggestions WHERE message LIKE '%zalo%'")
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    logger.info("  %s", row)
            else:
                logger.info("  Khong co du lieu")
        except sqlite3.OperationalError:
            logger.info("  Bang suggestions khong ton tai")
        
        # Kiem tra app_usage_logs (tat ca)
        logger.info("\n[3] APP_USAGE_LOGS (zalo - tat ca):")
        cursor.execute("SELECT COUNT(*) FROM app_usage_logs WHERE tenUngDung LIKE '%zalo%'")
        count = cursor.fetchone()[0]
        logger.info("  Tong so ban ghi: %d", count)
        
        # Xoa tat ca du lieu Zalo
        logger.info("\n[4] XOA TAT CA DU LIEU ZALO:")
        cursor.execute("DELETE FROM app_usage_logs WHERE tenUngDung LIKE '%zalo%'")
        deleted = cursor.rowcount
        conn.commit()
        logger.info("  Da xoa: %d ban ghi", deleted)
        
        cursor.execute("DELETE FROM user_habits WHERE tenMucTieu LIKE '%zalo%'")
        deleted = cursor.rowcount
        conn.commit()
        logger.info("  Da xoa user_habits: %d ban ghi", deleted)
        
        # Xoa suggestions (neu bang ton tai)
        logger.info("\n[5] XOA SUGGESTIONS (zalo):")
        try:
            cursor.execute("DELETE FROM suggestions WHERE message LIKE '%zalo%'")
            deleted = cursor.rowcount
            conn.commit()
            logger.info("  Da xoa suggestions: %d ban ghi", deleted)
        except sqlite3.OperationalError:
            logger.info("  Bang suggestions khong ton tai, bo qua")
    
    logger.info("\n" + "=" * 50)
    logger.info("  HOAN TAT!")
    logger.info("=" * 50)

if __name__ == '__main__':
    cleanup_zalo_test_data()
    check_app_usage()
    check_all_zalo_data()