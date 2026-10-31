Academic Schedule Manager
Python과 Tkinter로 만든 대학생 과제·시험 일정 관리 프로그램입니다. 과제, 시험, 발표 등의 마감일을 등록하고 남은 시간을 실시간으로 확인할 수 있습니다. 9주차 업데이트에서는 외부 API를 연동하여 대한민국 공휴일 조회 기능을 추가했습니다.

1. 주요 기능
일정 등록·삭제: 과목명, 일정 내용, 종류(과제·시험·발표·팀플·기타), 마감일시를 입력합니다.
달력 선택: 달력 팝업에서 날짜와 시·분·초를 선택합니다.
실시간 마감 표시: 마감까지 남은 일·시·분·초와 긴급도(여유·긴급·마감 지남)를 표시합니다.
완료 관리: 일정의 완료 여부를 변경하고 미완료 일정만 필터링합니다.
자동 저장: 등록한 일정은 schedules.json에 저장되어 다음 실행 시 다시 불러옵니다.
공휴일 조회(9주차 추가): 「공휴일 조회」 버튼을 누르면 현재 연도의 대한민국 공휴일 날짜와 이름을 별도 창에 표시합니다.
2. 실행 환경 및 설치 방법
언어: Python 3.10 이상 (.python-version에는 3.13 지정)
GUI: Tkinter (Python 표준 라이브러리; 실행 환경에 설치되어 있어야 함)
외부 라이브러리: requests
환경 관리: uv / pyproject.toml / uv.lock
인터넷 연결: 공휴일 API 조회 시 필요
저장소를 내려받은 뒤 프로젝트 폴더에서 아래 명령을 실행합니다.

git clone https://github.com/woojung016/academic-schedule-manager.git
cd academic-schedule-manager
uv sync
uv run python gui_main.py
GUI 창이 열리면 프로그램을 사용할 수 있습니다. API 통신만 단독으로 시험하려면 uv run python api_client.py를 실행합니다.

3. 프로그램 사용 방법
일정 등록: 과목명, 과제·시험 내용, 종류, 마감일시를 입력한 뒤 「일정 추가」를 누릅니다.
마감 확인: 메인 목록에서 각 일정의 남은 시간과 상태를 확인합니다. 남은 시간은 주기적으로 갱신됩니다.
완료·삭제: 목록에서 일정을 선택한 뒤 완료 상태를 전환하거나 삭제할 수 있습니다. 더블클릭으로도 완료 상태를 전환할 수 있습니다.
공휴일 조회: 화면 하단의 「공휴일 조회」 버튼을 클릭하면 별도 창에서 공휴일 목록을 볼 수 있습니다. 공휴일은 기존 일정에 자동 등록되지 않습니다.
4. 공휴일 API 연동 방식
제공 API: Nager.Holidays
요청 형식: GET https://nagerholidays.com/api/v4/Holidays/KR/{year}
인증: API Key 불필요
처리 과정: api_client.py에서 requests.get()으로 JSON 응답을 받고, holidayTypes에 Public이 포함된 항목의 date, name을 추출합니다. gui_main.py는 이를 별도 창에 출력합니다.
오류 처리: 요청 시간 제한 10초, HTTP 오류 검사(raise_for_status()), 예외 발생 시 오류 대화상자 표시
화면 응답성: API 요청은 별도 스레드에서 수행하고, 결과 표시 작업은 Tkinter의 after()를 통해 메인 이벤트 루프에 전달합니다.
5. 주요 파일 구성
파일	역할
gui_main.py	메인 GUI, 일정 조작, 공휴일 조회 버튼 및 결과 표시
api_client.py	공휴일 API 호출 및 응답 데이터 가공
schedule_model.py	일정 데이터 저장·불러오기, 마감 시간 및 상태 계산
calendar_picker.py	날짜·시간 선택 달력 팝업
schedules.json	사용자가 등록한 일정 데이터
pyproject.toml, uv.lock	프로젝트 환경 및 의존성 관리
api_plan.md	9주차 API 연동 기획안
장우정_9주차_AI대화_원문.md	AI 활용 및 오류 해결 대화 기록
6. 참고 및 주의사항
일정은 로컬 JSON 파일에 저장되므로 여러 기기 간 자동 동기화되지 않습니다.
공휴일 조회 기능은 외부 서비스와 인터넷 연결 상태에 영향을 받습니다.
실제 API 응답에 따라 표시되는 공휴일 정보가 달라질 수 있습니다.
이번 프로젝트는 API Key가 필요하지 않습니다. 이후 인증키를 사용할 경우 .env 파일에 보관하고 GitHub에는 올리지 않아야 합니다.
9주차 업데이트 과정: 별도 Git 브랜치에서 개발 → Commit/Push → Pull Request 생성 → main 병합. 자세한 기획은 api_plan.md, AI 활용 내역은 장우정_9주차_AI대화_원문.md를 참고하세요.

⋮⋮⋮⋮