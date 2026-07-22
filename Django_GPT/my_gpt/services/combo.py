from .moderator import MODEL_ID as MODERATE_MODEL_ID
from .moderator import moderate_text
from .sentiment import MODEL_ID as SENTIMENT_MODEL_ID
from .sentiment import analyze_sentiment
from .summarizer import MODEL_ID as SUMMARIZE_MODEL_ID
from .summarizer import summarize_text

MODEL_IDS = [SUMMARIZE_MODEL_ID, SENTIMENT_MODEL_ID, MODERATE_MODEL_ID]


def build_verdict(sentiment_label: str, toxicity_score: float) -> str:
    """
    감정/유해성 결과를 조합해 종합 판정 문장을 만든다.
    """
    if sentiment_label == "negative":
        sentiment_description = "이 피드백은 부정적인 평가를 포함합니다."
    elif sentiment_label == "positive":
        sentiment_description = "이 피드백은 긍정적인 평가를 포함합니다."
    else:
        sentiment_description = "이 피드백은 중립적인 평가에 가깝습니다."

    if toxicity_score >= 0.5:
        toxicity_description = "유해 표현이 포함되었을 가능성이 높습니다."
    elif toxicity_score >= 0.1:
        toxicity_description = "일부 공격적인 표현이 포함되었을 수 있습니다."
    else:
        toxicity_description = "심각한 유해 표현은 포함하지 않습니다."

    return f"{sentiment_description} {toxicity_description}"


def analyze_combo(text: str, regenerate: bool = False) -> dict:
    """
    Pipeline Chaining:
      원문 -> 요약 -> (요약문) -> 감정 분석 / 유해 표현 분석 -> 통합 리포트
    """
    # 1단계: 원문 요약
    summary_result = summarize_text(text, do_sample=regenerate)
    summary = summary_result["summary"]

    # 2단계: 요약문으로 감정 분석
    sentiment_result = analyze_sentiment(summary)

    # 3단계: 요약문으로 유해 표현 분석
    toxicity_result = moderate_text(summary)

    # 4단계: 종합 판정
    verdict = build_verdict(
        sentiment_result["label"],
        toxicity_result["highest_score"],
    )

    output_text = (
        f"[요약]\n{summary}\n\n"
        f"[감정 분석]\n"
        f"{sentiment_result['label'].capitalize()} "
        f"{sentiment_result['score'] * 100:.2f}%\n\n"
        f"[유해 표현 분석]\n"
        f"Highest Risk: {toxicity_result['highest_label']} "
        f"{toxicity_result['highest_score'] * 100:.2f}%\n\n"
        f"[종합 판정]\n{verdict}"
    )

    return {
        "model_ids": MODEL_IDS,
        "summary": summary,
        "original_length": summary_result["original_length"],
        "summary_length": summary_result["summary_length"],
        "summary_ratio": summary_result["summary_ratio"],
        "sentiment": {
            "label": sentiment_result["label"],
            "score": sentiment_result["score"],
        },
        "toxicity": {
            "highest_label": toxicity_result["highest_label"],
            "highest_score": toxicity_result["highest_score"],
            "all_scores": toxicity_result["all_scores"],
        },
        "verdict": verdict,
        "output_text": output_text,
    }