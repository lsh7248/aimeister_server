CREATE TABLE alembic_version
(
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

CREATE TABLE sys_api
(
    id           INTEGER      NOT NULL AUTO_INCREMENT,
    name         VARCHAR(50)  NOT NULL COMMENT 'api이름',
    method       VARCHAR(16)  NOT NULL COMMENT '요청 방법',
    path         VARCHAR(500) NOT NULL COMMENT 'api 경로',
    remark       LONGTEXT COMMENT '비고',
    created_time DATETIME     NOT NULL COMMENT '생성 시간',
    updated_time DATETIME COMMENT '수정 시간',
    PRIMARY KEY (id),
    UNIQUE (name)
);

CREATE INDEX ix_sys_api_id ON sys_api (id);

CREATE TABLE sys_casbin_rule
(
    id    INTEGER      NOT NULL COMMENT '주 키 ID' AUTO_INCREMENT,
    ptype VARCHAR(255) NOT NULL COMMENT '정책 유형: p 또는 g',
    v0    VARCHAR(255) NOT NULL COMMENT '역할 / 사용자 uuid',
    v1    LONGTEXT     NOT NULL COMMENT 'api 경로 / 역할 이름',
    v2    VARCHAR(255) COMMENT '요청 방법',
    v3    VARCHAR(255),
    v4    VARCHAR(255),
    v5    VARCHAR(255),
    PRIMARY KEY (id)
);

CREATE INDEX ix_sys_casbin_rule_id ON sys_casbin_rule (id);

CREATE TABLE sys_dept
(
    id           INTEGER     NOT NULL AUTO_INCREMENT,
    name         VARCHAR(50) NOT NULL COMMENT '부서 이름',
    level        INTEGER     NOT NULL COMMENT '부서 계층',
    sort         INTEGER     NOT NULL COMMENT '정렬',
    leader       VARCHAR(20) COMMENT '담당자',
    phone        VARCHAR(11) COMMENT '휴대폰',
    email        VARCHAR(50) COMMENT '이메일',
    status       INTEGER     NOT NULL COMMENT '부서 상태(0사용 중지 1정상)',
    del_flag     BOOL        NOT NULL COMMENT '삭제 표시(0삭제 1존재)',
    parent_id    INTEGER COMMENT '상위 부서 ID',
    created_time DATETIME    NOT NULL COMMENT '생성 시간',
    updated_time DATETIME COMMENT '수정 시간',
    PRIMARY KEY (id),
    FOREIGN KEY (parent_id) REFERENCES sys_dept (id) ON DELETE SET NULL
);

CREATE INDEX ix_sys_dept_id ON sys_dept (id);

CREATE INDEX ix_sys_dept_parent_id ON sys_dept (parent_id);

CREATE TABLE sys_dict_type
(
    id           INTEGER     NOT NULL AUTO_INCREMENT,
    name         VARCHAR(32) NOT NULL COMMENT '사전 유형 이름',
    code         VARCHAR(32) NOT NULL COMMENT '사전 유형 코드',
    status       INTEGER     NOT NULL COMMENT '상태(0사용 중지 1정상)',
    remark       LONGTEXT COMMENT '비고',
    created_time DATETIME    NOT NULL COMMENT '생성 시간',
    updated_time DATETIME COMMENT '수정 시간',
    PRIMARY KEY (id),
    UNIQUE (code),
    UNIQUE (name)
);

CREATE INDEX ix_sys_dict_type_id ON sys_dict_type (id);

CREATE TABLE sys_login_log
(
    id           INTEGER      NOT NULL AUTO_INCREMENT,
    user_uuid    VARCHAR(50)  NOT NULL COMMENT '사용자 UUID',
    username     VARCHAR(20)  NOT NULL COMMENT '사용자 이름',
    status       INTEGER      NOT NULL COMMENT '로그인 상태(0실패 1성공)',
    ip           VARCHAR(50)  NOT NULL COMMENT '로그인 IP 주소',
    country      VARCHAR(50) COMMENT '국가',
    region       VARCHAR(50) COMMENT '지역',
    city         VARCHAR(50) COMMENT '도시',
    user_agent   VARCHAR(255) NOT NULL COMMENT '요청 헤더',
    os           VARCHAR(50) COMMENT '운영 체제',
    browser      VARCHAR(50) COMMENT '브라우저',
    device       VARCHAR(50) COMMENT '장치',
    msg          LONGTEXT     NOT NULL COMMENT '알림 메시지',
    login_time   DATETIME     NOT NULL COMMENT '로그인 시간',
    created_time DATETIME     NOT NULL COMMENT '생성 시간',
    PRIMARY KEY (id)
);

CREATE INDEX ix_sys_login_log_id ON sys_login_log (id);

CREATE TABLE sys_menu
(
    id           INTEGER     NOT NULL AUTO_INCREMENT,
    title        VARCHAR(50) NOT NULL COMMENT '메뉴 제목',
    name         VARCHAR(50) NOT NULL COMMENT '메뉴 이름',
    level        INTEGER     NOT NULL COMMENT '메뉴 계층',
    sort         INTEGER     NOT NULL COMMENT '정렬',
    icon         VARCHAR(100) COMMENT '메뉴 아이콘',
    path         VARCHAR(200) COMMENT '라우팅 주소',
    menu_type    INTEGER     NOT NULL COMMENT '메뉴 유형 (0디렉토리 1메뉴 2버튼)',
    component    VARCHAR(255) COMMENT '컴포넌트 경로',
    perms        VARCHAR(100) COMMENT '권한 식별자',
    status       INTEGER     NOT NULL COMMENT '메뉴 상태(0사용 중지 1정상)',
    `show`       INTEGER     NOT NULL COMMENT '표시 여부(0아니오 1예)',
    cache        INTEGER     NOT NULL COMMENT '캐시 여부(0아니오 1예)',
    remark       LONGTEXT COMMENT '비고',
    parent_id    INTEGER COMMENT '상위 메뉴 ID',
    created_time DATETIME    NOT NULL COMMENT '생성 시간',
    updated_time DATETIME COMMENT '수정 시간',
    PRIMARY KEY (id),
    FOREIGN KEY (parent_id) REFERENCES sys_menu (id) ON DELETE SET NULL
);

CREATE INDEX ix_sys_menu_id ON sys_menu (id);

CREATE INDEX ix_sys_menu_parent_id ON sys_menu (parent_id);

CREATE TABLE sys_opera_log
(
    id           INTEGER      NOT NULL AUTO_INCREMENT,
    username     VARCHAR(20) COMMENT '사용자 이름',
    method       VARCHAR(20)  NOT NULL COMMENT '요청 유형',
    title        VARCHAR(255) NOT NULL COMMENT '조작 모듈',
    path         VARCHAR(500) NOT NULL COMMENT '요청 경로',
    ip           VARCHAR(50)  NOT NULL COMMENT 'IP 주소',
    country      VARCHAR(50) COMMENT '국가',
    region       VARCHAR(50) COMMENT '지역',
    city         VARCHAR(50) COMMENT '도시',
    user_agent   VARCHAR(255) NOT NULL COMMENT '요청 헤더',
    os           VARCHAR(50) COMMENT '운영 체제',
    browser      VARCHAR(50) COMMENT '브라우저',
    device       VARCHAR(50) COMMENT '장치',
    args         JSON COMMENT '요청 매개 변수',
    status       INTEGER      NOT NULL COMMENT '조작 상태(0이상 1정상)',
    code         VARCHAR(20)  NOT NULL COMMENT '조작 상태 코드',
    msg          LONGTEXT COMMENT '알림 메시지',
    cost_time    FLOAT        NOT NULL COMMENT '요청 시간(ms)',
    opera_time   DATETIME     NOT NULL COMMENT '조작 시간',
    created_time DATETIME     NOT NULL COMMENT '생성 시간',
    PRIMARY KEY (id)
);

CREATE INDEX ix_sys_opera_log_id ON sys_opera_log (id);

CREATE TABLE sys_role
(
    id           INTEGER     NOT NULL AUTO_INCREMENT,
    name         VARCHAR(20) NOT NULL COMMENT '역할 이름',
    data_scope   INTEGER COMMENT '권한 범위(1:전체 데이터 권한 2:사용자 정의 데이터 권한)',
    status       INTEGER     NOT NULL COMMENT '역할 상태(0사용 중지 1정상)',
    remark       LONGTEXT COMMENT '비고',
    created_time DATETIME    NOT NULL COMMENT '생성 시간',
    updated_time DATETIME COMMENT '수정 시간',
    PRIMARY KEY (id),
    UNIQUE (name)
);

CREATE INDEX ix_sys_role_id ON sys_role (id);

CREATE TABLE sys_dict_data
(
    id           INTEGER     NOT NULL AUTO_INCREMENT,
    label        VARCHAR(32) NOT NULL COMMENT '사전 레이블',
    value        VARCHAR(32) NOT NULL COMMENT '사전 값',
    sort         INTEGER     NOT NULL COMMENT '정렬',
    status       INTEGER     NOT NULL COMMENT '상태(0사용 중지 1정상)',
    remark       LONGTEXT COMMENT '비고',
    type_id      INTEGER     NOT NULL COMMENT '사전 유형 연결 ID',
    created_time DATETIME    NOT NULL COMMENT '생성 시간',
    updated_time DATETIME COMMENT '수정 시간',
    PRIMARY KEY (id),
    FOREIGN KEY (type_id) REFERENCES sys_dict_type (id),
    UNIQUE (label),
    UNIQUE (value)
);

CREATE INDEX ix_sys_dict_data_id ON sys_dict_data (id);

CREATE TABLE sys_role_menu
(
    id      INTEGER NOT NULL COMMENT '주 키 ID' AUTO_INCREMENT,
    role_id INTEGER NOT NULL COMMENT '역할 ID',
    menu_id INTEGER NOT NULL COMMENT '메뉴 ID',
    PRIMARY KEY (id, role_id, menu_id),
    FOREIGN KEY (menu_id) REFERENCES sys_menu (id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES sys_role (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_sys_role_menu_id ON sys_role_menu (id);

CREATE TABLE sys_user
(
    id              INTEGER      NOT NULL AUTO_INCREMENT,
    uuid            VARCHAR(50)  NOT NULL,
    username        VARCHAR(20)  NOT NULL COMMENT '사용자 이름',
    nickname        VARCHAR(20)  NOT NULL COMMENT '닉네임',
    password        VARCHAR(255) NOT NULL COMMENT '비밀번호',
    salt            VARCHAR(5)   NOT NULL COMMENT '암호화 소금',
    email           VARCHAR(50)  NOT NULL COMMENT '이메일',
    is_superuser    BOOL         NOT NULL COMMENT '슈퍼 권한(0 아니오, 1 예)',
    is_staff        BOOL         NOT NULL COMMENT '백엔드 관리 로그인 (0 아니오, 1 예)',
    status          INTEGER      NOT NULL COMMENT '사용자 계정 상태 (0 비활성화, 1 정상)',
    is_multi_login  BOOL         NOT NULL COMMENT '다중 로그인 (0 아니오, 1 예)',
    avatar          VARCHAR(255) COMMENT '아바타',
    phone           VARCHAR(11) COMMENT '휴대폰 번호',
    join_time       DATETIME     NOT NULL COMMENT '가입일',
    last_login_time DATETIME COMMENT '마지막 로그인',
    dept_id         INTEGER COMMENT '부서 관련 ID',
    created_time    DATETIME     NOT NULL COMMENT '생성일',
    updated_time    DATETIME COMMENT '수정일',
    PRIMARY KEY (id),
    FOREIGN KEY (dept_id) REFERENCES sys_dept (id) ON DELETE SET NULL,
    UNIQUE (nickname),
    UNIQUE (uuid)
);

CREATE UNIQUE INDEX ix_sys_user_email ON sys_user (email);

CREATE INDEX ix_sys_user_id ON sys_user (id);

CREATE UNIQUE INDEX ix_sys_user_username ON sys_user (username);

CREATE TABLE sys_user_role
(
    id      INTEGER NOT NULL COMMENT '주 키 ID' AUTO_INCREMENT,
    user_id INTEGER NOT NULL COMMENT '사용자 ID',
    role_id INTEGER NOT NULL COMMENT '역할 ID',
    PRIMARY KEY (id, user_id, role_id),
    FOREIGN KEY (role_id) REFERENCES sys_role (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES sys_user (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_sys_user_role_id ON sys_user_role (id);
