# 🤖 Django GPT

Hugging Face `pipeline()`을 활용한 Django 기반 AI 웹 서비스입니다.
감정 분석 / 문서 요약 / 유해 표현 분석 세 가지 AI 기능과,
세 모델을 순서대로 연결한 복합 분석(Pipeline Chaining) 기능을 제공합니다.

---

## 🧭 기능 및 URL

| 탭                | URL           | 기능                              | 접근 권한     |
| ----------------- | ------------- | --------------------------------- | ------------- |
| 😊 감정 분석      | `/sentiment/` | 영어 문장의 감정 분석             | 비로그인 허용 |
| 📄 문서 요약      | `/summarize/` | 영어 문서 요약                    | 로그인 필요   |
| 🚨 유해 표현 분석 | `/moderate/`  | 영어 문장의 유해성 분석           | 로그인 필요   |
| 🔗 복합 분석      | `/combo/`     | 요약 → 감정 → 유해 표현 연결 분석 | 로그인 필요   |

---

## 🧠 사용 모델

### 1. 감정 분석

| 항목        | 내용                                               |
| ----------- | -------------------------------------------------- |
| Model ID    | `cardiffnlp/twitter-roberta-base-sentiment-latest` |
| Task        | `text-classification`                              |
| 라이선스    | MIT                                                |
| 입력 언어   | 영어                                               |
| 출력 레이블 | `positive`, `neutral`, `negative`                  |
| 출력 형태   | 레이블별 신뢰도 점수 (0~1)                         |
| 입력 길이   | 1자 ~ 1,000자                                      |

### 2. 문서 요약

| 항목      | 내용                                                          |
| --------- | ------------------------------------------------------------- |
| Model ID  | `sshleifer/distilbart-cnn-6-6`                                |
| Task      | `summarization`                                               |
| 라이선스  | Apache-2.0                                                    |
| 입력 언어 | 영어                                                          |
| 출력 형태 | 요약문 텍스트 (원문 길이 / 요약문 길이 / 요약 비율 함께 출력) |
| 입력 길이 | 100자 ~ 5,000자                                               |

### 3. 유해 표현 분석

| 항목        | 내용                                                                    |
| ----------- | ----------------------------------------------------------------------- |
| Model ID    | `unitary/toxic-bert`                                                    |
| Task        | `text-classification` (Multi-label)                                     |
| 라이선스    | Apache-2.0                                                              |
| 입력 언어   | 영어                                                                    |
| 출력 레이블 | `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate` |
| 출력 형태   | 전체 레이블 점수 (높은 순 정렬)                                         |
| 입력 길이   | 1자 ~ 1,000자                                                           |

> 세 모델 모두 공개(Public) 모델이며 Gated Model이 아닙니다.

---

## 🔗 복합 분석 (챌린지)

`/combo/` 에서 영어 고객 리뷰를 입력하면 세 모델을 순서대로 실행합니다.

```
사용자 입력 (영어 고객 피드백, 200자 ~ 5,000자)
  ↓
① sshleifer/distilbart-cnn-6-6        → 요약문 생성
  ↓ (요약문)
② cardiffnlp/twitter-roberta-...      → 감정 분석
  ↓ (요약문)
③ unitary/toxic-bert                  → 유해 표현 분석
  ↓
종합 판정 리포트 출력
```

- 감정 분석과 유해 표현 분석에는 **원문이 아닌 요약 모델의 출력(요약문)** 을 입력값으로 사용합니다.
- 종합 판정은 별도 LLM 호출 없이 감정 레이블과 유해 점수를 조합한 조건문으로 생성합니다.
- **재생성 버튼**은 원문을 다시 입력받지 않고 동일 원문으로 Pipeline을 다시 실행합니다.
  요약 단계에 `do_sample=True`, `top_p=0.9`, `temperature=0.8`을 적용해 매번 다른 요약문이 생성됩니다.
- 재생성 결과도 새로운 실행 기록으로 DB에 저장됩니다.

---

## 🧰 기술 스택

```
Django 5.2
Django Template / Django ORM
Django Authentication / Session
CSRF Protection
Hugging Face Transformers (pipeline)
python-dotenv
HTML / CSS / JavaScript (fetch)
SQLite
```

---

## ⚙️ 실행 방법

### 1. 저장소 클론 및 이동

```bash
git clone <repository-url>
cd Django_GPT
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv venv

# Windows (Git Bash)
source venv/Scripts/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

> GPU를 사용하지 않는 환경에서는 CPU 전용 torch 설치를 권장합니다.
>
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cpu
> ```

### 4. 환경변수 설정

`.env.example`을 복사해 `.env` 파일을 만들고 값을 채웁니다.

```bash
cp .env.example .env
```

### 5. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

### 6. 관리자 계정 생성

```bash
python manage.py createsuperuser
```

> 회원가입 기능은 제공하지 않으며, Django Admin에서 계정을 생성해 사용합니다.

### 7. 서버 실행

```bash
python manage.py runserver
```

브라우저에서 `http://127.0.0.1:8000/sentiment/` 로 접속합니다.

> 각 모델은 해당 기능을 **처음 실행할 때** 다운로드됩니다.
> 최초 실행 시 모델당 400~500MB가 다운로드되며 시간이 걸릴 수 있습니다.
> CPU 환경에서는 문서 요약 실행에 10~30초가 소요될 수 있습니다.

---

## 🔐 환경변수 설정 방법

프로젝트 최상단의 `.env` 파일에 아래 값을 작성합니다.

```
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
HUGGINGFACE_TOKEN=
HF_HUB_DISABLE_SYMLINKS_WARNING=1
```

| 변수                              | 설명                                                               |
| --------------------------------- | ------------------------------------------------------------------ |
| `DJANGO_SECRET_KEY`               | Django Secret Key (필수)                                           |
| `DJANGO_DEBUG`                    | 디버그 모드 여부 (`True` / `False`)                                |
| `HUGGINGFACE_TOKEN`               | Hugging Face Access Token (공개 모델만 사용하므로 비워두어도 동작) |
| `HF_HUB_DISABLE_SYMLINKS_WARNING` | Windows symlink 경고 비활성화                                      |

- `.env` 파일은 `.gitignore`에 포함되어 GitHub에 업로드되지 않습니다.
- Token은 코드에 직접 작성하지 않고 환경변수로만 관리합니다.
- 형식 참고용으로 `.env.example` 파일을 저장소에 포함했습니다.

---

## 🗃️ 실행 기록 관리

- 로그인 사용자의 모델 실행 결과는 `InferenceHistory` 모델에 저장됩니다.
- 각 탭에서는 해당 기능(`task`)의 최근 기록 5개만 최신순으로 출력합니다.
- 조회 시 `filter(user=request.user)` 로 본인의 기록만 조회하며, 다른 사용자의 기록에는 접근할 수 없습니다.
- 비로그인 사용자의 감정 분석 기록은 DB에 저장하지 않고 JavaScript 배열로만 유지하므로,
  새로고침 시 초기화됩니다. (`localStorage` / `Django Session` 미사용)

---

## 🛡️ 보안 및 예외 처리

- `@csrf_exempt`를 사용하지 않으며, `fetch()` 요청 시 `X-CSRFToken` 헤더를 전송합니다.
- 모든 입력값은 모델 실행 전에 Django View에서 검증합니다.
  (타입 / 빈 문자열 / 공백 / 최소 길이 / 최대 길이)
- 모델 실행 실패 시 Traceback을 노출하지 않고 `logger.exception()`으로 서버에 기록한 뒤,
  사용자에게는 안내 메시지만 반환합니다.
- 로그인 제한은 서버에서 검사하므로 주소창에 URL을 직접 입력해도 접근할 수 없습니다.

---

## 💤 Lazy Loading 및 모델 캐시

- 모델 실행 코드는 View가 아닌 `my_gpt/services/` 계층으로 분리했습니다.
- 각 파이프라인은 `@lru_cache(maxsize=1)`로 감싸 **최초 요청 시에만 로드**되고 이후 재사용됩니다.
- 서버 시작 시 모든 모델을 로드하지 않습니다.
- CPU / CUDA / MPS 환경 판별은 `services/common.py`의 `get_pipeline_device()`에서 공통 처리합니다.

---

## 📁 프로젝트 구조

```
Django_GPT/
├─ config/
│  ├─ settings.py
│  └─ urls.py
├─ my_gpt/
│  ├─ migrations/
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ common.py        # device 판별 공통 함수
│  │  ├─ sentiment.py     # 감정 분석
│  │  ├─ summarizer.py    # 문서 요약
│  │  ├─ moderator.py     # 유해 표현 분석
│  │  └─ combo.py         # 복합 분석 (Pipeline Chaining)
│  ├─ static/my_gpt/js/
│  │  ├─ common.js        # CSRF 포함 fetch 유틸
│  │  ├─ sentiment.js
│  │  ├─ summarize.js
│  │  ├─ moderate.js
│  │  └─ combo.js
│  ├─ templates/
│  │  ├─ registration/
│  │  │  └─ login.html
│  │  └─ my_gpt/
│  │     ├─ base.html
│  │     ├─ sentiment.html
│  │     ├─ summarize.html
│  │     ├─ moderate.html
│  │     └─ combo.html
│  ├─ decorators.py       # model_login_required
│  ├─ models.py           # InferenceHistory
│  ├─ urls.py
│  └─ views.py
├─ .env
├─ .env.example
├─ .gitignore
├─ manage.py
├─ README.md
└─ requirements.txt
```
