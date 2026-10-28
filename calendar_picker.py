"""달력 및 시간(년/월/일/시/분/초) 선택 팝업 모듈"""
import calendar
from datetime import datetime
import tkinter as tk
from tkinter import ttk


class CalendarPopup(tk.Toplevel):
    """달력 클릭 및 시/분/초를 선택할 수 있는 팝업 대화상자"""
    def __init__(self, parent, target_entry, parse_fn):
        super().__init__(parent)
        self.target = target_entry
        self.parse_fn = parse_fn
        self.title("마감 일시 선택")
        self.geometry("290x320")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        existing = self.parse_fn(self.target.get()) or datetime.now()
        self.year, self.month = existing.year, existing.month

        # 상단 년/월 이동 헤더
        hdr = ttk.Frame(self, padding=4)
        hdr.pack(fill="x")
        ttk.Button(hdr, text="<", width=3, command=self.prev_m).pack(side="left")
        self.title_lbl = ttk.Label(hdr, font=("맑은 고딕", 10, "bold"))
        self.title_lbl.pack(side="left", expand=True)
        ttk.Button(hdr, text=">", width=3, command=self.next_m).pack(side="right")

        # 달력 그리드 영역
        self.cal_frame = ttk.Frame(self, padding=4)
        self.cal_frame.pack(fill="both", expand=True)

        # 하단 시/분/초 입력 영역
        t_bar = ttk.Frame(self, padding=6)
        t_bar.pack(fill="x")
        ttk.Label(t_bar, text="시간(시:분:초):").pack(side="left")

        self.h_sp = ttk.Spinbox(t_bar, from_=0, to=23, width=3, format="%02.0f")
        self.h_sp.set(f"{existing.hour:02d}")
        self.h_sp.pack(side="left", padx=1)
        ttk.Label(t_bar, text=":").pack(side="left")

        self.m_sp = ttk.Spinbox(t_bar, from_=0, to=59, width=3, format="%02.0f")
        self.m_sp.set(f"{existing.minute:02d}")
        self.m_sp.pack(side="left", padx=1)
        ttk.Label(t_bar, text=":").pack(side="left")

        self.s_sp = ttk.Spinbox(t_bar, from_=0, to=59, width=3, format="%02.0f")
        self.s_sp.set(f"{existing.second:02d}")
        self.s_sp.pack(side="left", padx=1)

        self.render()

    def render(self):
        for w in self.cal_frame.winfo_children():
            w.destroy()
        self.title_lbl.config(text=f"{self.year}년 {self.month}월")

        days = ["월", "화", "수", "목", "금", "토", "일"]
        for i, d in enumerate(days):
            fg = "blue" if i == 5 else ("red" if i == 6 else "black")
            tk.Label(self.cal_frame, text=d, fg=fg, font=("맑은 고딕", 9, "bold")).grid(row=0, column=i, pady=1)

        weeks = calendar.monthcalendar(self.year, self.month)
        for r, week in enumerate(weeks, 1):
            for c, day in enumerate(week):
                if day != 0:
                    btn = tk.Button(self.cal_frame, text=str(day), width=3, relief="groove",
                                    command=lambda d=day: self.pick(d))
                    btn.grid(row=r, column=c, padx=1, pady=1)

    def prev_m(self):
        self.month, self.year = (12, self.year - 1) if self.month == 1 else (self.month - 1, self.year)
        self.render()

    def next_m(self):
        self.month, self.year = (1, self.year + 1) if self.month == 12 else (self.month + 1, self.year)
        self.render()

    def pick(self, day):
        try:
            h = int(self.h_sp.get())
            m = int(self.m_sp.get())
            s = int(self.s_sp.get())
        except ValueError:
            h, m, s = 23, 59, 59
        self.target.delete(0, "end")
        self.target.insert(0, f"{self.year:04d}-{self.month:02d}-{day:02d} {h:02d}:{m:02d}:{s:02d}")
        self.destroy()
