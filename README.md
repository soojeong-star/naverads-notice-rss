# 네이버애즈 공지사항 RSS

첫 페이지에서 발견한 공지의 제목·URL을 RSS로 제공합니다. 
최초 1페이지 이후에 발견한 공지는 이력에 계속 보관해, 다음 조회 전에 첫 페이지에서 밀려나도 RSS에는 남도록 합니다. 첫 페이지에 노출되기 전에 지나간 게시물이나 조회 사이에 게시·삭제된 글은 수집할 수 없습니다.

## GitHub 설정

1. 이 저장소의 기본 브랜치를 `main`으로 지정합니다.
2. Settings → Pages → Build and deployment → Source를 **GitHub Actions**로 지정합니다.
3. Actions → **Update notice RSS** → Run workflow → Run workflow를 선택합니다.
4. 실행 결과가 초록색인지 확인합니다.
5. RSS 주소: https://soojeong-star.github.io/naverads-notice-rss/rss.xml

Python 표준 라이브러리만 사용하므로 패키지 설치나 API 키는 필요 없습니다. GitHub Actions의 내장 토큰으로 이력을 저장하고 Pages에 게시합니다. Pages/Actions가 조직 정책으로 제한되거나 브랜치 보호 규칙이 적용되면 해당 권한을 조정해야 합니다.

## 실행 시간

수집은 한국 시간 월~금 08:47부터 17:47까지 매시간 예약합니다. 09:00부터 18:00 정각 알림 전에 RSS를 갱신하기 위한 시간입니다. 
