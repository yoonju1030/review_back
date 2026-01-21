# 로깅 사용 가이드

## 📋 개요

이 프로젝트는 Django의 표준 로깅 시스템을 사용하여 애플리케이션의 동작을 추적하고 모니터링합니다.

## 🗂 로그 파일 구조

프로젝트 루트에 `logs/` 디렉토리가 자동으로 생성되며, 다음과 같은 로그 파일들이 생성됩니다:

```
logs/
├── django.log      # 전체 애플리케이션 로그 (INFO 레벨 이상)
├── error.log       # 에러 로그만 (ERROR 레벨)
└── api.log         # API 관련 로그 (animeapp, userapp, commentapp)
```

## 📝 로그 레벨

- **DEBUG**: 디버깅 정보 (개발 환경에서만)
- **INFO**: 일반적인 정보 메시지
- **WARNING**: 경고 메시지
- **ERROR**: 에러 메시지
- **CRITICAL**: 심각한 에러

## 🔧 설정

### settings.py에 로깅 설정이 포함되어 있습니다:

- **파일 로테이션**: 각 로그 파일은 10MB를 초과하면 자동으로 로테이션됩니다
- **백업 파일 수**: 최대 5-10개의 백업 파일 유지
- **인코딩**: UTF-8로 한글 로그 지원

## 💻 사용 방법

### 1. 기본 사용법

```python
import logging

# 앱별 로거 가져오기
logger = logging.getLogger('userapp')  # 또는 'animeapp', 'commentapp'

# 로그 레벨별 출력
logger.debug("디버그 메시지")
logger.info("정보 메시지")
logger.warning("경고 메시지")
logger.error("에러 메시지")
logger.critical("심각한 에러 메시지")
```

### 2. 실제 사용 예시

#### userapp/views.py
```python
import logging

logger = logging.getLogger('userapp')

@api_view(["POST"])
def sign_up_user(request):
    try:
        user_id = request.data.get("id", "unknown")
        logger.info(f"회원가입 요청: {user_id}")
        
        # ... 회원가입 로직 ...
        
        logger.info(f"회원가입 성공: {user.id}")
        return Response(...)
    except Exception as e:
        logger.error(f"회원가입 실패: {str(e)}", exc_info=True)
        return Response(...)
```

#### animeapp/views.py
```python
import logging

logger = logging.getLogger('animeapp')

@api_view(["POST"])
def insert_anime(request):
    try:
        anime_data = request.data["data"]
        logger.info(f"애니메이션 등록/수정 요청: {anime_data.get('name', 'unknown')}")
        
        # ... 애니메이션 등록 로직 ...
        
        logger.info(f"애니메이션 생성: {name} (ID: {obj.id})")
        return Response(...)
    except Exception as e:
        logger.error(f"애니메이션 등록 실패: {str(e)}", exc_info=True)
        return Response(...)
```

### 3. 예외 정보 포함하기

```python
try:
    # 코드 실행
    pass
except Exception as e:
    # exc_info=True를 사용하면 스택 트레이스도 함께 기록됩니다
    logger.error(f"에러 발생: {str(e)}", exc_info=True)
```

### 4. 추가 정보와 함께 로깅

```python
# 사용자 정보와 함께 로깅
user_id = request.user.id if hasattr(request.user, 'id') else "unknown"
logger.info(f"API 요청: 사용자={user_id}, 엔드포인트={request.path}")

# 데이터와 함께 로깅
logger.info(f"애니메이션 조회: ID={anime_id}, 결과={len(results)}개")
```

## 📊 로그 포맷

### 기본 포맷 (verbose)
```
[INFO] 2024-01-21 10:30:45 userapp.views 12345 67890 회원가입 요청: user123
```

포맷 구성:
- `[레벨]`: 로그 레벨
- `시간`: 타임스탬프
- `모듈`: 로그를 발생시킨 모듈
- `프로세스ID`: 프로세스 ID
- `스레드ID`: 스레드 ID
- `메시지`: 실제 로그 메시지

### 간단한 포맷 (simple)
```
[INFO] 2024-01-21 10:30:45 회원가입 요청: user123
```

## 🎯 로그 활용 시나리오

### 1. API 요청 추적
```python
logger.info(f"API 요청: {request.method} {request.path} - 사용자: {user_id}")
```

### 2. 성능 모니터링
```python
import time

start_time = time.time()
# ... 작업 수행 ...
elapsed_time = time.time() - start_time
logger.info(f"작업 완료: {elapsed_time:.2f}초 소요")
```

### 3. 데이터 변경 추적
```python
logger.info(f"애니메이션 생성: {name} (ID: {obj.id}, 장르: {genre_names})")
logger.info(f"댓글 생성: 사용자={user.id}, 애니메이션={anime.id}")
```

### 4. 에러 디버깅
```python
try:
    # 코드 실행
    pass
except Exception as e:
    logger.error(f"에러 발생: {type(e).__name__} - {str(e)}", exc_info=True)
    # exc_info=True는 전체 스택 트레이스를 포함합니다
```

## 🔍 로그 확인 방법

### 1. 실시간 로그 확인 (Linux/Mac)
```bash
# 전체 로그 실시간 확인
tail -f logs/django.log

# 에러 로그만 확인
tail -f logs/error.log

# API 로그만 확인
tail -f logs/api.log
```

### 2. 특정 키워드 검색
```bash
# "회원가입" 관련 로그만 검색
grep "회원가입" logs/django.log

# 에러 로그에서 특정 사용자 검색
grep "user123" logs/error.log
```

### 3. 최근 로그 확인
```bash
# 마지막 100줄 확인
tail -n 100 logs/django.log

# 특정 시간대 로그 확인
grep "2024-01-21 10:" logs/django.log
```

## ⚙️ 로깅 설정 커스터마이징

### 로그 레벨 변경

`settings.py`에서 로그 레벨을 변경할 수 있습니다:

```python
LOGGING = {
    'loggers': {
        'userapp': {
            'handlers': ['console', 'api_file'],
            'level': 'DEBUG',  # DEBUG로 변경하면 더 상세한 로그 출력
            'propagate': False,
        },
    },
}
```

### 새로운 로그 핸들러 추가

```python
'handlers': {
    'custom_file': {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': LOGGING_DIR / 'custom.log',
        'maxBytes': 1024 * 1024 * 10,  # 10MB
        'backupCount': 5,
        'formatter': 'verbose',
        'encoding': 'utf-8',
    },
}
```

## 📌 주의사항

1. **민감한 정보 로깅 금지**
   - 비밀번호, 토큰, 개인정보 등은 로그에 남기지 않도록 주의
   ```python
   # ❌ 나쁜 예
   logger.info(f"로그인: {user_id}, 비밀번호: {password}")
   
   # ✅ 좋은 예
   logger.info(f"로그인 시도: {user_id}")
   ```

2. **과도한 로깅 방지**
   - 너무 많은 로그는 성능에 영향을 줄 수 있습니다
   - 중요한 이벤트만 로깅하세요

3. **로그 파일 크기 관리**
   - 로그 파일이 너무 커지지 않도록 로테이션 설정 확인
   - 주기적으로 오래된 로그 파일 정리

## 🚀 프로덕션 환경

프로덕션 환경에서는:
- `DEBUG = False`로 설정
- 로그 레벨을 `INFO` 이상으로 설정
- 에러 로그는 별도 모니터링 시스템과 연동 고려
- 로그 파일은 보안이 유지되는 위치에 저장

## 📚 참고 자료

- [Django 공식 로깅 문서](https://docs.djangoproject.com/en/5.0/topics/logging/)
- [Python logging 모듈 문서](https://docs.python.org/3/library/logging.html)

