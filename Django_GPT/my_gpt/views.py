import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .decorators import model_login_required
from .models import InferenceHistory
from .services.combo import MODEL_IDS as COMBO_MODEL_IDS
from .services.combo import analyze_combo
from .services.sentiment import MODEL_ID as SENTIMENT_MODEL_ID
from .services.sentiment import analyze_sentiment
from .services.moderator import MODEL_ID as MODERATE_MODEL_ID
from .services.moderator import moderate_text
from .services.summarizer import MODEL_ID as SUMMARIZE_MODEL_ID
from .services.summarizer import summarize_text

logger = logging.getLogger(__name__)

SENTIMENT_MIN_LEN = 1
SENTIMENT_MAX_LEN = 1000

SUMMARIZE_MIN_LEN = 100
SUMMARIZE_MAX_LEN = 5000

MODERATE_MIN_LEN = 1
MODERATE_MAX_LEN = 1000

COMBO_MIN_LEN = 200
COMBO_MAX_LEN = 5000


def sentiment_page(request):
    histories = []

    if request.user.is_authenticated:
        histories = InferenceHistory.objects.filter(
            user=request.user,
            task=InferenceHistory.Task.SENTIMENT,
        ).order_by("-created_at")[:5]

    context = {
        "model_id": SENTIMENT_MODEL_ID,
        "input_language": "영어",
        "active_tab": "sentiment",
        "min_len": SENTIMENT_MIN_LEN,
        "max_len": SENTIMENT_MAX_LEN,
        "histories": histories,
    }
    return render(request, "my_gpt/sentiment.html", context)

@require_POST
def sentiment_run(request):
    # 1. 요청 데이터 확인
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 요청 형식입니다."}, status=400)

    text = payload.get("text")

    # 2. 입력값 검증
    if not isinstance(text, str):
        return JsonResponse({"error": "분석할 문장을 입력해주세요."}, status=400)

    text = text.strip()

    if len(text) < SENTIMENT_MIN_LEN:
        return JsonResponse({"error": "분석할 문장을 입력해주세요."}, status=400)

    if len(text) > SENTIMENT_MAX_LEN:
        return JsonResponse(
            {"error": f"문장은 {SENTIMENT_MAX_LEN:,}자 이하로 입력해주세요."},
            status=400,
        )

    # 3. Service 호출
    try:
        result = analyze_sentiment(text)
    except Exception:
        logger.exception("Sentiment inference failed.")
        return JsonResponse(
            {"error": "모델 실행에 실패했습니다.\n잠시 후 다시 시도해주세요."},
            status=502,
        )
    
    # 4. 로그인 사용자만 실행 기록 저장
    if request.user.is_authenticated:
        InferenceHistory.objects.create(
            user=request.user,
            task=InferenceHistory.Task.SENTIMENT,
            input_text=text,
            output_text=result["output_text"],
            result_data={
                "label": result["label"],
                "score": result["score"],
                "all_scores": result["all_scores"],
            },
        )

    # 5. 응답
    histories = []

    if request.user.is_authenticated:
        rows = InferenceHistory.objects.filter(
            user=request.user,
            task=InferenceHistory.Task.SENTIMENT,
        ).order_by("-created_at")[:5]

        histories = [
            {
                "input_text": row.input_text,
                "label": row.result_data.get("label", ""),
            }
            for row in rows
        ]

    return JsonResponse(
        {
            "label": result["label"],
            "score": result["score"],
            "all_scores": result["all_scores"],
            "output_text": result["output_text"],
            "is_authenticated": request.user.is_authenticated,
            "histories": histories,
        }
    )

@model_login_required
def summarize_page(request):
    histories = InferenceHistory.objects.filter(
        user=request.user,
        task=InferenceHistory.Task.SUMMARIZE,
    ).order_by("-created_at")[:5]

    context = {
        "model_id": SUMMARIZE_MODEL_ID,
        "input_language": "영어",
        "active_tab": "summarize",
        "min_len": SUMMARIZE_MIN_LEN,
        "max_len": SUMMARIZE_MAX_LEN,
        "histories": histories,
    }
    return render(request, "my_gpt/summarize.html", context)


@require_POST
@model_login_required
def summarize_run(request):
    # 1. 요청 데이터 확인
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 요청 형식입니다."}, status=400)

    text = payload.get("text")

    # 2. 입력값 검증
    if not isinstance(text, str):
        return JsonResponse(
            {"error": f"요약할 문서는 {SUMMARIZE_MIN_LEN}자 이상 입력해주세요."},
            status=400,
        )

    text = text.strip()

    if len(text) < SUMMARIZE_MIN_LEN:
        return JsonResponse(
            {"error": f"요약할 문서는 {SUMMARIZE_MIN_LEN}자 이상 입력해주세요."},
            status=400,
        )

    if len(text) > SUMMARIZE_MAX_LEN:
        return JsonResponse(
            {"error": f"문서는 {SUMMARIZE_MAX_LEN:,}자 이하로 입력해주세요."},
            status=400,
        )

    # 3. Service 호출
    try:
        result = summarize_text(text)
    except Exception:
        logger.exception("Summarize inference failed.")
        return JsonResponse(
            {"error": "모델 실행에 실패했습니다.\n잠시 후 다시 시도해주세요."},
            status=502,
        )

    # 4. 실행 기록 저장
    InferenceHistory.objects.create(
        user=request.user,
        task=InferenceHistory.Task.SUMMARIZE,
        input_text=text,
        output_text=result["output_text"],
        result_data={
            "summary": result["summary"],
            "original_length": result["original_length"],
            "summary_length": result["summary_length"],
            "summary_ratio": result["summary_ratio"],
        },
    )

    # 5. 응답
    rows = InferenceHistory.objects.filter(
        user=request.user,
        task=InferenceHistory.Task.SUMMARIZE,
    ).order_by("-created_at")[:5]

    histories = [
        {
            "input_text": row.input_text,
            "summary": row.result_data.get("summary", ""),
        }
        for row in rows
    ]

    return JsonResponse(
        {
            "summary": result["summary"],
            "original_length": result["original_length"],
            "summary_length": result["summary_length"],
            "summary_ratio": result["summary_ratio"],
            "output_text": result["output_text"],
            "histories": histories,
        }
    )

@model_login_required
def moderate_page(request):
    histories = InferenceHistory.objects.filter(
        user=request.user,
        task=InferenceHistory.Task.MODERATE,
    ).order_by("-created_at")[:5]

    context = {
        "model_id": MODERATE_MODEL_ID,
        "input_language": "영어",
        "active_tab": "moderate",
        "min_len": MODERATE_MIN_LEN,
        "max_len": MODERATE_MAX_LEN,
        "histories": histories,
    }
    return render(request, "my_gpt/moderate.html", context)


@require_POST
@model_login_required
def moderate_run(request):
    # 1. 요청 데이터 확인
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 요청 형식입니다."}, status=400)

    text = payload.get("text")

    # 2. 입력값 검증
    if not isinstance(text, str):
        return JsonResponse({"error": "분석할 문장을 입력해주세요."}, status=400)

    text = text.strip()

    if len(text) < MODERATE_MIN_LEN:
        return JsonResponse({"error": "분석할 문장을 입력해주세요."}, status=400)

    if len(text) > MODERATE_MAX_LEN:
        return JsonResponse(
            {"error": f"문장은 {MODERATE_MAX_LEN:,}자 이하로 입력해주세요."},
            status=400,
        )

    # 3. Service 호출
    try:
        result = moderate_text(text)
    except Exception:
        logger.exception("Moderate inference failed.")
        return JsonResponse(
            {"error": "모델 실행에 실패했습니다.\n잠시 후 다시 시도해주세요."},
            status=502,
        )

    # 4. 실행 기록 저장
    InferenceHistory.objects.create(
        user=request.user,
        task=InferenceHistory.Task.MODERATE,
        input_text=text,
        output_text=result["output_text"],
        result_data={
            "highest_label": result["highest_label"],
            "highest_score": result["highest_score"],
            "all_scores": result["all_scores"],
        },
    )

    # 5. 응답
    rows = InferenceHistory.objects.filter(
        user=request.user,
        task=InferenceHistory.Task.MODERATE,
    ).order_by("-created_at")[:5]

    histories = [
        {
            "input_text": row.input_text,
            "highest_label": row.result_data.get("highest_label", ""),
            "highest_score": row.result_data.get("highest_score", 0),
        }
        for row in rows
    ]

    return JsonResponse(
        {
            "highest_label": result["highest_label"],
            "highest_score": result["highest_score"],
            "all_scores": result["all_scores"],
            "output_text": result["output_text"],
            "histories": histories,
        }
    )

@model_login_required
def combo_page(request):
    histories = InferenceHistory.objects.filter(
        user=request.user,
        task=InferenceHistory.Task.COMBO,
    ).order_by("-created_at")[:5]

    context = {
        "model_ids": COMBO_MODEL_IDS,
        "input_language": "영어",
        "active_tab": "combo",
        "min_len": COMBO_MIN_LEN,
        "max_len": COMBO_MAX_LEN,
        "histories": histories,
    }
    return render(request, "my_gpt/combo.html", context)


@require_POST
@model_login_required
def combo_run(request):
    # 1. 요청 데이터 확인
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 요청 형식입니다."}, status=400)

    text = payload.get("text")
    regenerate = bool(payload.get("regenerate", False))

    # 2. 입력값 검증
    if not isinstance(text, str):
        return JsonResponse(
            {"error": f"분석할 피드백은 {COMBO_MIN_LEN}자 이상 입력해주세요."},
            status=400,
        )

    text = text.strip()

    if len(text) < COMBO_MIN_LEN:
        return JsonResponse(
            {"error": f"분석할 피드백은 {COMBO_MIN_LEN}자 이상 입력해주세요."},
            status=400,
        )

    if len(text) > COMBO_MAX_LEN:
        return JsonResponse(
            {"error": f"피드백은 {COMBO_MAX_LEN:,}자 이하로 입력해주세요."},
            status=400,
        )

    # 3. Service 호출 (요약 -> 감정 -> 유해)
    try:
        result = analyze_combo(text, regenerate=regenerate)
    except Exception:
        logger.exception("Combo inference failed.")
        return JsonResponse(
            {"error": "모델 실행에 실패했습니다.\n잠시 후 다시 시도해주세요."},
            status=502,
        )

    # 4. 실행 기록 저장 (재생성도 새 기록으로 저장)
    InferenceHistory.objects.create(
        user=request.user,
        task=InferenceHistory.Task.COMBO,
        input_text=text,
        output_text=result["output_text"],
        result_data={
            "summary": result["summary"],
            "sentiment": result["sentiment"],
            "toxicity": result["toxicity"],
            "verdict": result["verdict"],
            "regenerated": regenerate,
        },
    )

    # 5. 응답
    rows = InferenceHistory.objects.filter(
        user=request.user,
        task=InferenceHistory.Task.COMBO,
    ).order_by("-created_at")[:5]

    histories = [
        {
            "input_text": row.input_text,
            "sentiment_label": row.result_data.get("sentiment", {}).get("label", ""),
            "toxicity_label": row.result_data.get("toxicity", {}).get("highest_label", ""),
            "regenerated": row.result_data.get("regenerated", False),
        }
        for row in rows
    ]

    return JsonResponse(
        {
            "summary": result["summary"],
            "original_length": result["original_length"],
            "summary_length": result["summary_length"],
            "summary_ratio": result["summary_ratio"],
            "sentiment": result["sentiment"],
            "toxicity": result["toxicity"],
            "verdict": result["verdict"],
            "output_text": result["output_text"],
            "histories": histories,
        }
    )