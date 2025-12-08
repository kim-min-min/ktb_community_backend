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
    
      ├── README.md
      ├── package-lock.json
      ├── package.json
      ├── app.js
      ├── .prettierrc
      ├── config
      │    └── mysql.cjs
      ├── controller
      │    ├── comment-controller.cjs
      │    ├── post-controller.cjs
      │    └── user-controller.cjs
      ├── images
      │    ├── post/
      │    └── profile/
      ├── middleware
      │    ├── authUser.cjs
      │    └── validation.cjs
      ├── model
      │    ├── comments.cjs
      │    ├── posts.cjs
      │    └── users.cjs
      ├── queries
      │    ├── comments.cjs
      │    ├── posts.cjs
      │    └── users.cjs
      ├── routes
      │    ├── comment.cjs
      │    ├── post.cjs
      │    ├── user.cjs
      │     postImage.cjs
      │    └── profileImage.cjs
      └── tools
           ├── queryUtils.cjs
           └── dataUtils.js
  </div>
</details> 

<br/>

## 서버 설계
### 서버 구조
||route|controller|model|
|:---|:---|:---|:---|
|유저|userRouter|userController|userModel|
|게시글|postRouter|postController|postModel|
|댓글|commentRouter|commentController|commentModal|
|게시글이미지|postImageRouter|-|-|
|프로필이미지|profileImageRouter|-|-|

### 구현 기능

#### Users
```
- 유저 CRUD 기능 구현
- 회원가입, 로그인, 비밀번호 변경 시 bcrypt로 비밀번호 암호화하여 처리
- 세션을 통해 유저 정보 저장, 로그아웃/회원탈퇴 시 세션 destroy
- 미들웨어를 통해 세션 정보가 있는 유저 요청만 처리
- 프로필 이미지는 서버에 저장하고, DB에는 이미지 url 저장
```

#### Posts
```
- 게시글 CRUD 기능 구현
- 미들웨어를 통해 세션 정보가 있는 유저 요청만 처리
```

#### Comments
```
- 댓글 CRUD 기능 구현
- 미들웨어를 통해 세션 정보가 있는 유저 요청만 처리
```
<br/>

## 데이터베이스 설계
### 요구사항 분석
`유저 관리`
- 사용자는 이메일, 프로필 이미지, 비밀번호, 닉네임 정보를 포함하는 유저 관리
- 각 유저는 고유한 식별자를 가지고 있으며, 이메일과 닉네임은 유니크하게 설정하여 중복 방지

`게시글 관리`
- 사용자가 제목, 내용, 이미지, 작성일시, 수정일시 등의 정보를 포함하는 게시글 관리
- 게시글은 작성자를 참조하여 관계를 설정

`댓글 관리`
- 사용자가 내용, 작성자, 작성일시 등의 정보를 포함하는 댓글 관리
- 댓글은 어떤 게시글에 속해 있는지 나타내는 참조 포함

`세션 관리`
- 사용자의 로그인 세션을 관리
- 세션 식별자, 만료 시간, 세션 데이터를 저장하여 사용자의 세션 추적

### 모델링
`E-R Diagram`  
요구사항을 기반으로 모델링한 E-R Diagram입니다.  
<br/>
<img src="https://github.com/100-hours-a-week/5-erica-express-be/assets/81230764/1546793d-fd03-47f3-8ed1-449edb764750" width="70%" />

<br/>

## 트러블 슈팅
추후 작성..

<br/>

## 프로젝트 후기
사실 상 백엔드를 구현하는 것이 처음이라서 많이 낯설었습니다.  
프론트엔드만 경험했던 저라서 어떻게 구조를 짜야하고 어떤 방식으로 코드를 짜야 효율적이고 클린한지 고민을 많이 했던 것 같습니다.  
express로 서버를 만들고, MySQL로 Database를 만들어 연결하는 방식 또한 새로운 지식이어서 힘들었지만 하나하나 해내가며 프로젝트 완성에 가까워지니 재밌어했던 것 같습니다.  
해당 프로젝트는 express로 구현을 했으니 추후 프로젝트에서는 SpringBoot를 사용해서 서버를 구현해보려고 합니다.  
백엔드 공부를 열심히 해서 더욱 완성도 있는 프로젝트를 하겠습니다! 


<br/>
<br/>
<br/>

<p align="center">
  <img src="https://github.com/100-hours-a-week/5-erica-react-fe/assets/81230764/d611b233-b596-4d1d-bbb9-dc2e4e41eb47" style="width:200px; margin: 0 auto"/>
</p>
