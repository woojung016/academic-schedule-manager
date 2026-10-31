Academic Schedule Manager
Python Tkinter 기반 과제 및 시험 일정 관리 프로그램 이다. 
기존의 기능으로는 마감일 저장, 실시간 카운트다운 및 완료 상태가 있었다.
9주차에는 Nager.Holidays API를 이용해 대한민국 공휴일 조회 기능을 추가했다.API 결과는 기존 일정과 분리해 표시한다.

1. 실행 및 프로젝트 구조
환경: Python 3.13 (.python-version), uv, Tkinter, requests
API Key: 불필요
인터넷: 공휴일 조회 시 필요, 이외는 불필요
</> powershell
git clone https://github.com/woojung016/academic-schedule-manager.git
cd academic-schedule-manager
uv sync
uv run python gui_main.py
# API 단독 확인: uv run python api_client.py
1) gui_main.py: 사용자 이벤트 처리, 화면 갱신, API 결과 출력
2) schedule_model.py: JSON 읽기 및 쓰기, 날짜 해석, 마감 상태 계산
3) calendar_picker.py: 날짜 및 시간 선택을 위한 CalendarPopup
4) api_client.py: HTTP 요청, JSON 응답 선별, 공휴일 목록 반환
5) schedules.json: 일정의 영속 데이터 저장소
6) pyproject.toml / uv.lock: 의존성 선언 및 동일 환경 재현
# 실행 순서: main( ) -> tk.Tk( ) -> ScheduleManagerGUI(root) -> load_schedules( ) -> _build_ui( ) -> refresh_list ( ) -> _tick_second( ) -> root.mainloop( )
여기서 mainloop ( )는 이벤트 루프이며, 버튼 클릭, 더블클릭, 타이머가 등록한 콜백을 실행한다. 
데이터 (self.schedules)와 표시 위젯 (self.tree)을 분리하고, 상태가 바뀔 때 화면을 다시 동기화한다.

2. 일정 데이터와 핵심 Logic
- 데이터 단위: 일정 하나는 아래 필드를 가진 딕셔너리이고, 
self.schedules는 이 딕셔너리의 리스트이다.
</> JSON
{"subject":"미적분학II","title":"WebWork 제출","kind":"과제","deadline":"2026-11-04 23:59:59","done":false}
1) __init__( ): load_schedules()로 JSON 로드 -> 화면 생성 -> 목록 렌더링 -> 1초 갱신 시작
2) _build_ui(): Entry, Combobox, Treeview, 버튼 및 상태 라벨 배치, 버튼에 command=self.메서드 연결
3) add_item( ): 입력값의 공백 제거 -> 필수값 검사 -> parse_deadline( ) 검증 -> save_schedules( ) -> 목록 갱신
4) refresh_list ( ): 완료 여부·마감일 기준 정렬 -> 필터 적용 -> Treeview 재구성 -> 전체/미완료/완료 개수 표시
5) toggle_done ( ): 선택 행 확인 -> 원본 일정 탐색 -> done 반전 -> JSON 저장 및 재출력
6) delete_item( ): 선택 행 확인 -> 삭제 승인(askyesno) -> 리스트에서 제거 -> JSON 저장 및 재출력
7) _tick_second( ): 입력 중인 마감일의 카운트다운 및 각 행의 상태 갱신 -> after(1000, ...)로 다음 실해 예약
- 화면 인덱스와 원본 인덱스를 구분하는 이유
</> Python
sorted_pairs = sorted(
    enumerate(self.schedules),
    key=lambda x: (x[1].get("done", False), x[1].get("deadline", ""))
)
# 화면에 추가할 때 self.display_order.append(orig_idx)
idx = self.display_order[int(sel[0]) - 1]
1) False < True이므로 미완료 일정이 먼저, 같은 완료 상태에서는 마감일 문자열순으로 표시된다. 날짜가 YYYY-MM-DD HH:MM:SS로 통일되어 있어 문자열 정렬이 시간순 정렬과 일치한다.
2) 정렬 및 필터 후에는 화면의 1번행 != 원본 리스트의 0번 원소일 수 있다. display_order가 두 순서를 연결하므로 완료 전환 및 삭제 시 다른 일정이 수정되지 않는다. 
3) refresh_list()는 표시만 갱신한다.
4) 실제 데이터 변경 후에는 save_schedules()를 호출하므로 프로그램을 다시 실행해도 변경 사항이 유지된다.
- 마감 시간 갱신과 이벤트 루프
format_countdown_label()은 현재 입력란의 날짜를, get_deadline_info(deadline, done)는 저장된 각 일정의 남은 시간과 표시 태그를 계산한다. _tick_second()는 Treeview의 전체 행을 다시 만들지 않고 urgency 열과 태그만 갱신한다.
</> Python
self.root.after(1000, self._tick_second)
1) after()는 대기하는 동안 GUI 실행을 막지 않는 콜백 예약이다.
2) 반복문에 time.sleep(1)을 사용하는 방식과 달리 버튼 입력과 화면 갱신이 계속 가능하다.
3) 달력 버튼은 CalendarPopup(self.root, self.entry_dt, parse_deadline)을 통해 기존 입력창·날짜 검증 함수를 재사용한다.

3. API 연동: 데이터 흐름과 비동기 처리
요청: GET https://nagerholidays.com/api/v4/Holidays/KR/{year} (year는 현재 연도)
</> Python
response = requests.get(url, timeout=10)
response.raise_for_status()
for holiday in response.json():
    if "Public" in holiday.get("holidayTypes", []):
        holidays.append({"date": holiday["date"], "name": holiday["name"]})
1) request.get( )은 서버 응답을 기다리는 네트워크 I/O 이다.
timeout = 10으로 응답 대기 시간을 제한하며, raise_for_status( )가 HTTP 실패 상태를 예외로 변환한다.
2) JSON 전체를 GUI에 넘기지 않고 holidayTypes의 Public 여부를 검사해 date, name만 추출한다. 
.get(..., [])는 분류 필드가 없을 때 빈 목록으로 취급하기 위한 방어적 접근이다.
3) fetch_public_holidays(year)는 결과 리스트만 반환한다.
API 호출/데이터 가공(api_client.py)과 화면 출력(gui_main.py)을 분리해 단독 실행·점검이 가능하다.