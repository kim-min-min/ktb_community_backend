# 🌙 심야톡방

## Back-end 소개

- 2030 사용자가 밤에 편하게 아무 말이든 털어놓을 수 있는 익명 커뮤니티 서비스입니다.
- FastAPI로 REST API 서버를 구현하고, MySQL을 RDBMS로 사용했습니다.
- JWT 기반 인증, 게시글/댓글 CRUD, 이미지 업로드, 실제 서비스에 필요한 기능들을 처음부터 끝까지 직접 구현했습니다.
- Router–Controller–CRUD–Model 패턴으로 구조를 나누고, Docker + Nginx로 컨테이너화하여 AWS EC2에 배포했습니다.

### 개발 인원 및 기간

- 개발기간 :  2025-11-03 ~ 2025-12-07
- 개발 인원 : 프론트엔드/백엔드 1명 (본인)

### 사용 기술 및 tools
- MySQL
- FastAPI
- Docker
- Nginx
- AWS


### Front-end
- <a href="https://github.com/kim-min-min/ktb_community_frontend">Front-end Github</a>

### 서비스 시연 영상
- <a href="https://youtu.be/q1ynQzCd8ew?si=9sB9tTtQmSvPlvr6">유튜브</a>

### 폴더 구조
<details>
  <summary>폴더 구조 보기/숨기기</summary>
  <div markdown="1">
    
      ktb_community_backend
      │
      ├── app
      │   ├── core                # 보안 / 설정
      │   │    └── security.py
      │   │
      │   ├── database.py         # DB 연결
      │   │
      │   ├── models              # SQLAlchemy 모델
      │   │    ├── user_model.py
      │   │    └── post_model.py
      │   │
      │   ├── crud                # DB CRUD 로직
      │   │    ├── user_crud.py
      │   │    └── post_crud.py
      │   │
      │   ├── controllers         # 비즈니스 로직
      │   │    ├── auth_controller.py
      │   │    └── post_controller.py
      │   │
      │   ├── dependencies        # Depends() 인증/인가
      │   │    └── auth.py
      │   │
      │   └── routes              # FastAPI 라우터
      │        ├── auth_router.py
      │        └── post_router.py
      │
      ├── uploads                 # 프로필 이미지
      └── post_uploads            # 게시글 이미지

  </div>
</details> 

<br/>

## 서버 설계
### 서버 구조
||route|controller|model|CRUD|
|:---|:---|:---|:---|:---|
|유저|user_router|user_controller|user_model|user_crud|
|게시글,댓글|post_router|post_controller|post_model|post_crud|


### 구현 기능

#### Users
```
- 회원가입, 로그인, 프로필 수정, 비밀번호 변경, 회원탈퇴
- 비밀번호는 passlib(pbkdf2_sha256)으로 해싱하여 저장
- FastAPI 의존성 주입(Depends)을 이용해 JWT에서 현재 유저 정보 추출
- 회원가입 시 이메일/닉네임 중복 체크 및 기본 검증 로직 구현
- 프로필 이미지는 서버 폴더에 저장하고, DB에는 이미지 경로만 저장
```

#### Posts
```
- 게시글 생성, 조회(단건/목록), 수정, 삭제 기능 구현
- 이미지 첨부 시 UploadFile로 서버에 저장 후 image_path 컬럼에 경로 저장
- 작성자(user_id)와의 FK 관계를 통해 유저-게시글 연관 관리
- 좋아요(likes), 조회수(views) 컬럼으로 간단한 피드백 기능 제공
```

<br/>

## 데이터베이스 설계
### 요구사항 분석
`유저 관리`
- 이메일, 비밀번호, 닉네임, 프로필 이미지 경로 등을 포함
- 이메일/닉네임은 유니크 제약 조건으로 중복 방지

`게시글 관리`
- 제목, 내용, 이미지 경로, 좋아요 수, 조회수, 작성일시 등의 정보 포함
- 작성자는 User 테이블의 FK로 참조

`댓글 관리`
- 댓글 내용, 작성자, 작성일시 정보 포함
- 어떤 게시글에 달린 댓글인지 Post를 참조

`JWT 기반 인증 관리`
- 서버 세션을 사용하지 않고, Stateless 인증 방식인 JWT(Json Web Token)를 사용하여 로그인 상태를 유지
- 인증이 필요한 모든 요청은 Authorization: Bearer <token> 헤더를 통해 토큰을 전달하며, 서버에서는 해당 토큰을 검증하여 유저 정보를 확인
- 토큰 검증은 get_current_user 의존성(FastAPI Depends)을 통해 자동화되며, 만료되었거나 위조된 토큰의 경우 401 Unauthorized를 반환하여 보안을 유지

<br/>

## 트러블 슈팅
..

<br/>

## 프로젝트 후기
단순히 API 몇 개를 만드는 수준이 아니라, 인증·데이터 모델링·이미지 처리·Docker 기반 배포·Nginx 프록시 설정까지 

실제 서비스가 갖춰야 할 전 과정을 직접 설계하고 구현했습니다.

JWT 기반 인증 시스템을 직접 설계하면서, 토큰 생성·만료·검증 흐름, get_current_user 의존성을 통한 자동 인증 처리 등

서버가 상태를 저장하지 않는 Stateless 아키텍처에 대한 이해가 깊어졌습니다.

마지막으로, Docker + EC2 배포를 통해 로컬에서 만들던 코드가 서비스가 되는 순간 큰 성취감을 느꼈고, 서버 운영에 대한 자신감도 생겼습니다.


<br/>
<br/>
<br/>
