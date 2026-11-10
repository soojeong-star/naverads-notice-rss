# 네이버 광고 공지 RSS

첫 페이지에서 발견한 공지의 제목·URL을 RSS로 제공합니다. 기존 공지번호의 제목·본문 수정은 무시합니다. 최초 1페이지 이후에 발견한 공지는 이력에 계속 보관해, 다음 조회 전에 첫 페이지에서 밀려나도 RSS에는 남도록 합니다. 첫 페이지에 노출되기 전에 지나간 게시물이나 조회 사이에 게시·삭제된 글은 수집할 수 없습니다.

## GitHub 설정

1. 이 저장소의 기본 브랜치를 `main`으로 지정합니다.
2. Settings → Pages → Build and deployment → Source를 **GitHub Actions**로 지정합니다.
3. Actions → **Update notice RSS** → Run workflow → Run workflow를 선택합니다.
4. 실행 결과가 초록색인지 확인합니다.
5. RSS 주소: https://soojeong-star.github.io/naverads-notice-rss/rss.xml

Python 표준 라이브러리만 사용하므로 패키지 설치나 API 키는 필요 없습니다. GitHub Actions의 내장 토큰으로 이력을 저장하고 Pages에 게시합니다. Pages/Actions가 조직 정책으로 제한되거나 브랜치 보호 규칙이 적용되면 해당 권한을 조정해야 합니다.

## 실행 시간

수집은 한국 시간 월~금 08:47부터 17:47까지 매시간 예약합니다. Power Automate의 09:00부터 18:00 정각 알림 전에 RSS를 갱신하기 위한 시간입니다. GitHub Actions의 예약 실행은 지연되거나 누락될 수 있으므로 정각 전달은 보장하지 않습니다. 지연된 갱신 결과는 다음 Power Automate 실행에서 읽힐 수 있습니다. 공개 저장소에서 60일 동안 저장소 활동이 없으면 GitHub가 예약 워크플로를 비활성화할 수 있으므로 Actions 상태를 주기적으로 확인합니다.

## Power Automate

1. SharePoint 목록 `NaverAdsNoticeSent`를 만들고 기본 Title 열에 RSS 항목의 고유 ID(정규화된 공지 URL)를 저장합니다. 가능하면 Title 열의 고유값 적용을 켭니다.
2. 예약된 클라우드 흐름의 되풀이를 매주 / 월~금 / 시간 9,10,11,12,13,14,15,16,17,18 / 분 0 / 시간대 Seoul로 설정합니다. 흐름의 동시 실행은 1로 제한합니다.
3. `모든 RSS 피드 항목 나열`에 RSS 주소를 입력합니다. `since`는 비워두어 저장된 항목 전부를 비교합니다.
4. 각 항목의 `id`(고유 식별자)를 SharePoint Title 열과 비교합니다. RSS guid는 공지 URL이며 연결 옵션의 표시 이름은 언어에 따라 다를 수 있습니다. 실제 실행 출력에서 id와 primaryLink를 확인합니다.
5. 첫 실행은 **메시지 전송 없이** 모든 ID를 SharePoint에 저장하는 초기화 용도로 사용합니다. 초기화 성공 후 기존에 없는 ID에만 Teams 전송이 실행되도록 바꿉니다. 초기화 중 새로 발견된 공지도 초기 기준에 포함됩니다.
6. 다음 실행부터 신규 ID이면 기존에 시험한 Teams 그룹채팅 액션으로 제목과 primaryLink만 전송합니다.
7. Teams 전송이 성공한 경우에만 SharePoint에 ID를 저장합니다. 저장 실패 시 다음 실행에서 중복 전송될 수 있으므로 실패 실행 이력을 확인합니다.
8. 조회 실패는 실패로 처리합니다. 신규 없음과 오류를 구분합니다.

GitHub에는 Teams 인증정보를 넣지 않습니다. 로컬 실행: `python generate_rss.py`. 출력은 `site/rss.xml`이며 이력은 `data/notices.json`에 저장됩니다. 이력 파일을 지우면 기존 공지를 다시 신규로 판단하므로 유지합니다.
