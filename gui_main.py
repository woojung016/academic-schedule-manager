"""대학생 과제 및 시험 관리 프로그램 (GUI 메인 실행 모듈)
기획안(장우정_3주차_기획안작성.md) 요구사항 기반 구현
"""
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, ttk

from calendar_picker import CalendarPopup
from schedule_model import (
    format_countdown_label,
    get_deadline_info,
    load_schedules,
    parse_deadline,
    save_schedules,
)


class ScheduleManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("대학생 과제 및 시험 관리 프로그램")
        self.root.geometry("940x590")
        self.root.minsize(820, 500)
        self.root.configure(bg="#f5f6fa")

        self.schedules = load_schedules()
        self.display_order = []

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure(".", font=("맑은 고딕", 10))
        style.configure("Treeview", rowheight=30, background="white")
        style.configure("Treeview.Heading", font=("맑은 고딕", 10, "bold"))

        self._build_ui()
        self.refresh_list()
        self._tick_second()

    def _build_ui(self):
        body = ttk.Frame(self.root, padding=14)
        body.pack(fill="both", expand=True)

        header = ttk.Frame(body)
        header.pack(fill="x", pady=(0, 8))
        ttk.Label(header, text="📝 대학생 과제 및 시험 관리", font=("맑은 고딕", 15, "bold")).pack(side="left")

        # 새 일정 등록 폼
        form = ttk.LabelFrame(body, text="새 일정 등록", padding=10)
        form.pack(fill="x", pady=(0, 8))

        ttk.Label(form, text="과목명:").grid(row=0, column=0, padx=4, pady=3, sticky="w")
        self.entry_sub = ttk.Entry(form, width=14)
        self.entry_sub.grid(row=0, column=1, padx=4, pady=3, sticky="ew")

        ttk.Label(form, text="과제/시험 내용:").grid(row=0, column=2, padx=4, pady=3, sticky="w")
        self.entry_title = ttk.Entry(form, width=24)
        self.entry_title.grid(row=0, column=3, padx=4, pady=3, sticky="ew")

        ttk.Label(form, text="종류:").grid(row=0, column=4, padx=4, pady=3, sticky="w")
        self.combo_kind = ttk.Combobox(form, values=("과제", "시험", "발표", "팀플", "기타"), width=7, state="readonly")
        self.combo_kind.set("과제")
        self.combo_kind.grid(row=0, column=5, padx=4, pady=3)

        ttk.Label(form, text="마감일시:").grid(row=1, column=0, padx=4, pady=3, sticky="w")
        self.entry_dt = ttk.Entry(form, width=20)
        self.entry_dt.insert(0, (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d 23:59:59"))
        self.entry_dt.grid(row=1, column=1, padx=4, pady=3, sticky="ew")

        # 마감일시 옆 달력 버튼 및 실시간 남은 시간 표시
        dt_bar = ttk.Frame(form)
        dt_bar.grid(row=1, column=2, columnspan=2, padx=4, pady=3, sticky="w")
        ttk.Button(dt_bar, text="📅 달력", width=6,
                   command=lambda: CalendarPopup(self.root, self.entry_dt, parse_deadline)).pack(side="left")
        self.lbl_countdown = tk.Label(dt_bar, text="", font=("맑은 고딕", 9, "bold"), anchor="w")
        self.lbl_countdown.pack(side="left", padx=(8, 0))

        ttk.Button(form, text="➕ 일정 추가", command=self.add_item).grid(row=1, column=4, columnspan=2, padx=4, pady=3, sticky="e")
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=2)

        # 일정 목록 테이블
        table_frame = ttk.Frame(body)
        table_frame.pack(fill="both", expand=True)

        cols = ("idx", "subject", "title", "kind", "deadline", "urgency")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        for c, t, w, a in (("idx", "번호", 45, "center"), ("subject", "과목명", 130, "w"),
                           ("title", "과제 / 시험 내용", 190, "w"), ("kind", "종류", 65, "center"),
                           ("deadline", "마감 일시", 155, "center"), ("urgency", "실시간 남은 시간 및 상태", 220, "center")):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor=a)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for tag, bg, fg in (("urgent", "#fff0f0", "black"), ("normal", "#ffffff", "black"),
                            ("done", "#f0f0f0", "#888888"), ("overdue", "#ffebee", "#c62828")):
            self.tree.tag_configure(tag, background=bg, foreground=fg)
        self.tree.bind("<Double-1>", lambda _: self.toggle_done())

        # 하단 툴바
        toolbar = ttk.Frame(body)
        toolbar.pack(fill="x", pady=(8, 2))
        self.var_hide_done = tk.BooleanVar(value=False)
        ttk.Checkbutton(toolbar, text="미완료만 보기", variable=self.var_hide_done, command=self.refresh_list).pack(side="left")
        ttk.Button(toolbar, text="새로고침", command=self.refresh_list).pack(side="right", padx=3)
        ttk.Button(toolbar, text="선택 삭제", command=self.delete_item).pack(side="right", padx=3)
        ttk.Button(toolbar, text="완료 / 미완료 전환 (더블클릭)", command=self.toggle_done).pack(side="right", padx=3)

        self.status_lbl = ttk.Label(body, text="", font=("맑은 고딕", 9), foreground="#555555")
        self.status_lbl.pack(fill="x", pady=(2, 0))

    def _tick_second(self):
        """1초마다 마감일시 옆 라벨 및 테이블 실시간 남은 시간 갱신"""
        txt, fg = format_countdown_label(self.entry_dt.get())
        self.lbl_countdown.config(text=txt, fg=fg)
        for disp_idx, item_id in enumerate(self.tree.get_children()):
            if disp_idx < len(self.display_order):
                task = self.schedules[self.display_order[disp_idx]]
                urgency, tag = get_deadline_info(task.get("deadline", ""), task.get("done", False))
                self.tree.set(item_id, "urgency", urgency)
                self.tree.item(item_id, tags=(tag,))
        self.root.after(1000, self._tick_second)

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        sorted_pairs = sorted(enumerate(self.schedules), key=lambda x: (x[1].get("done", False), x[1].get("deadline", "")))
        self.display_order = []
        disp_idx = 1
        for orig_idx, item in sorted_pairs:
            if self.var_hide_done.get() and item.get("done", False):
                continue
            urgency, tag = get_deadline_info(item.get("deadline", ""), item.get("done", False))
            self.tree.insert("", "end", iid=str(disp_idx),
                             values=(disp_idx, item["subject"], item.get("title") or item.get("name") or "-",
                                     item["kind"], item.get("deadline", "-"), urgency), tags=(tag,))
            self.display_order.append(orig_idx)
            disp_idx += 1

        pending = [x for x in self.schedules if not x.get("done", False)]
        status = f"전체 {len(self.schedules)}개 | 미완료 {len(pending)}개 | 완료 {len(self.schedules) - len(pending)}개"
        if pending:
            first = min(pending, key=lambda x: x.get("deadline", "9999"))
            status += f"  (가장 가까운 마감: {first['subject']} - {first.get('title', first['kind'])} [{first.get('deadline', '')}])"
        self.status_lbl.config(text=status)

    def add_item(self):
        sub, title = self.entry_sub.get().strip(), self.entry_title.get().strip()
        kind, dt_raw = self.combo_kind.get().strip(), self.entry_dt.get().strip()
        if not sub:
            messagebox.showwarning("입력 오류", "과목명을 입력해주세요.")
            return self.entry_sub.focus_set()
        if not title:
            messagebox.showwarning("입력 오류", "과제/시험 내용을 입력해주세요.")
            return self.entry_title.focus_set()
        parsed = parse_deadline(dt_raw)
        if not parsed:
            messagebox.showwarning("날짜 형식 오류", "올바른 날짜/시간을 입력하세요.\n예: 2026-10-15 23:59:59")
            return
        self.schedules.append({"subject": sub, "title": title, "kind": kind,
                               "deadline": parsed.strftime("%Y-%m-%d %H:%M:%S"), "done": False})
        save_schedules(self.schedules)
        self.entry_title.delete(0, "end")
        self.refresh_list()

    def toggle_done(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showinfo("선택 확인", "목록에서 일정을 먼저 선택해주세요.")
        idx = self.display_order[int(sel[0]) - 1]
        self.schedules[idx]["done"] = not self.schedules[idx].get("done", False)
        save_schedules(self.schedules)
        self.refresh_list()

    def delete_item(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showinfo("선택 확인", "목록에서 일정을 먼저 선택해주세요.")
        idx = self.display_order[int(sel[0]) - 1]
        t = self.schedules[idx]
        if messagebox.askyesno("삭제 확인", f"'{t['subject']} - {t.get('title', t['kind'])}' 일정을 삭제하시겠습니까?"):
            self.schedules.pop(idx)
            save_schedules(self.schedules)
            self.refresh_list()


def main():
    root = tk.Tk()
    ScheduleManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
