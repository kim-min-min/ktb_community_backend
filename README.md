⭐ 📌 심야톡방 – 익명 기반 실시간 커뮤니티 서비스 (Backend)
🎯 프로젝트 소개

**“심야톡방”**은 2030 사용자를 타깃으로 한 익명 커뮤니티 서비스로,
심야 시간대에 자유롭게 글을 작성하고, 이미지를 공유하며 소통할 수 있도록 설계된 웹 서비스입니다.

FastAPI 기반의 RESTful API 서버와 MySQL 기반의 데이터베이스를 구축하였으며,
JWT 인증, 이미지 업로드, 게시글/댓글 CRUD 등 커뮤니티 서비스 핵심 기능을 직접 설계·구현했습니다.

전체 서비스는 Docker 기반으로 컨테이너화하여
Nginx Reverse Proxy + FastAPI + MySQL 구조로 AWS EC2에 배포했습니다.

🧑‍💻 개발 인원 및 기간

개발 인원: 1명 (단독 개발)

개발 기간: 2025.11 ~ 2025.12

🔧 사용 기술 (Tech Stack)
Backend

FastAPI

SQLAlchemy ORM

MySQL 8.0

Pydantic

JWT Authentication

Passlib (pbkdf2_sha256)

Infra / DevOps

Docker, Docker Compose

Nginx Reverse Proxy

AWS EC2 (Ubuntu)

Linux 서버 운영

.env 환경변수 관리

🚀 주요 기능 구현
🔐 1. JWT 기반 인증/인가

로그인 성공 시 Access Token 발급, LocalStorage에 저장

/posts, /profile 등 주요 페이지는 RequireAuth로 보호

토큰 만료 시 자동 로그아웃 + 로그인 페이지로 리다이렉트

Refresh Token 없이 Access Token 기반의 심플한 구조로 설계

📝 2. 게시글 & 댓글 CRUD + 이미지 업로드

FastAPI UploadFile 기반 이미지 업로드 처리

게시글 이미지, 프로필 이미지 관리

좋아요, 조회수 증가 로직 구현

ORM 기반으로 DB 정합성 유지

🖼 3. 정적 파일 접근 문제 해결 (Nginx + StaticFiles)

개발 중 업로드된 이미지가 FastAPI에서 정상적으로 반환되지 않는 문제가 발생
→ 정적 파일 서빙을 Nginx로 이관하여 해결
