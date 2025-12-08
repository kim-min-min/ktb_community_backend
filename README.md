## 🎉 심야톡방 – 익명 기반 실시간 커뮤니티 서비스

<p align="center">
  <img width="700" height="500" alt="다운로드" src="https://github.com/user-attachments/assets/f924c869-7824-4d3d-9277-800b2e6a6d97" />
</p>



📌 프로젝트 소개

“심야톡방”은 2030 사용자를 대상으로 한 익명 커뮤니티 서비스로,

심야 시간대에 자유롭게 글을 작성하고, 이미지를 공유하며 소통할 수 있도록 설계된 웹 서비스입니다.

FastAPI 기반의 RESTful 백엔드와 MySQL 데이터베이스를 구축하고,

JWT 인증, 이미지 업로드, 게시글/댓글 CRUD 등 커뮤니티 서비스의 핵심 기능을 직접 설계·구현했습니다.

전체 서비스는 Docker 기반으로 컨테이너화하여 Nginx + React(Frontend) + FastAPI(Backend) + MySQL 구조로 AWS EC2에 배포했습니다.

<br><br>

👨‍💻 개발 정보

개발 인원: 1명 (단독 개발)

개발 기간: 2025.11 ~ 2025.12

<br><br>

🛠 Tech Stack

Frontend : React, Vite

Backend : FastAPI, SQLAlchemy ORM, MySQL 8.0

Infra : Docker, Nginx Reverse Proxy, AWS EC2

<br><br>

🚀 주요 기능

🔐 1. JWT 기반 인증/인가

로그인 시 Access Token 발급, LocalStorage 저장

/posts, /profile 등 주요 페이지 접근 보호

토큰 만료 시 자동 로그아웃 및 로그인 페이지로 이동

Refresh Token 없이 Access Token만 사용하는 심플한 구조
<br><br>

📝 2. 게시글/댓글 CRUD + 이미지 업로드

FastAPI UploadFile 기반 이미지 업로드 처리

게시글 이미지 / 프로필 이미지 저장

좋아요, 조회수 증가 로직 구현

SQLAlchemy ORM 기반의 데이터 정합성 유지
<br><br>

⚙️ 3. Nginx + Docker 기반 배포 구조

모든 요청을 Nginx가 우선 수신하고 프론트엔드·백엔드 컨테이너로 라우팅하는 구조로 설계

Backend는 내부 Docker 네트워크에서만 접근 가능

CORS, 정적 파일 라우팅, HTTPS 대응 가능

<br><br>

🧠 프로젝트 회고
### What.

익명 커뮤니티 서비스의 전체 기능을 백엔드부터 프론트, 배포까지 단독으로 구현한 프로젝트입니다.

### How.

FastAPI 기반 백엔드 설계 및 REST API 구현

JWT 인증/인가 + RequireAuth 라우팅 가드

이미지 업로드/정적 파일 문제를 Nginx + FastAPI StaticFiles 조합으로 해결

Docker 기반 배포 + AWS EC2 서버 환경 구성

### Then.

서비스 기획 → API 개발 → DB 모델링 → 배포/운영까지

웹 서비스의 전체 생애주기를 실질적으로 경험하며, 프로덕션 환경에서 서비스가 어떻게 동작하는지 명확히 이해하게 되었습니다.
