"""일정 데이터 저장 및 긴급도 실시간 계산 모듈"""
from datetime import datetime
import json
import os
from pathlib import Path

DATA_FILE = Path(__file__).resolve().with_name("schedules.json")


def load_schedules():
    """저장된 일정 데이터 불러오기"""
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_schedules(tasks):
    """일정 데이터를 안전하게 저장"""
    try:
        tmp = DATA_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        os.replace(tmp, DATA_FILE)
        return True
    except OSError:
        return False


def parse_deadline(text):
    """년/월/일 시:분:초 텍스트 파싱"""
    text = text.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(text, fmt)
            if fmt == "%Y-%m-%d":
                dt = dt.replace(hour=23, minute=59, second=59)
            elif fmt == "%Y-%m-%d %H:%M":
                dt = dt.replace(second=0)
            return dt
        except ValueError:
            pass
    return None


def calc_time_diff(dt):
    """현재 컴퓨터 시각과의 차이를 계산하여 일/시/분/초 반환"""
    diff = dt - datetime.now()
    secs = int(diff.total_seconds())
    is_past = secs < 0
    d, rem = divmod(abs(secs), 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    return is_past, d, h, m, s


def format_countdown_label(dt_str):
    """마감일시 입력창 옆에 실시간 표시할 남은 시간 안내 문자열 및 색상"""
    dt = parse_deadline(dt_str)
    if not dt:
        return "(날짜 형식: YYYY-MM-DD HH:MM:SS)", "#777777"
    is_past, d, h, m, s = calc_time_diff(dt)
    time_str = f"{h:02d}:{m:02d}:{s:02d}"
    if is_past:
        return f"⚠️ 마감 지남 ({d}일 {time_str} 전)", "#c62828"
    if d == 0:
        return f"🚨 오늘 마감 ({time_str} 남음)", "#d32f2f"
    if d <= 3:
        return f"⚠️ 긴급 D-{d} ({time_str} 남음)", "#e65100"
    return f"⏳ D-{d} ({time_str} 남음)", "#1565c0"


def get_deadline_info(dt_str, done):
    """테이블 목록에 실시간 표시할 상태 및 스타일 태그 반환"""
    if done:
        return "완료", "done"
    dt = parse_deadline(dt_str)
    if not dt:
        return "날짜 오류", "normal"

    is_past, d, h, m, s = calc_time_diff(dt)
    t_str = f"{h:02d}:{m:02d}:{s:02d}"
    if is_past:
        return f"마감 지남 ({d}일 {t_str} 전)", "overdue"
    if d == 0:
        return f"🚨 오늘 마감 ({t_str} 남음)", "urgent"
    if d <= 3:
        return f"⚠️ 긴급 D-{d} ({t_str})", "urgent"
    if d <= 7:
        return f"📌 보통 D-{d} ({t_str})", "normal"
    return f"🟢 여유 D-{d} ({t_str})", "normal"
