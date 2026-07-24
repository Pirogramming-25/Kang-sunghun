from functools import lru_cache

from transformers import pipeline

from .common import get_pipeline_device

MODEL_ID = "cardiffnlp/twitter-roberta-base-sentiment-latest"


@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    """
    감정 분석 파이프라인을 최초 1회만 생성하고 이후에는 재사용한다.
    """
    return pipeline(
        task="text-classification",
        model=MODEL_ID,
        top_k=None,
        device=get_pipeline_device(),
    )


def analyze_sentiment(text: str) -> dict:
    """
    영어 문장의 감정을 분석한다.
    입력값 검증은 View에서 끝난 상태라고 가정한다.
    """
    classifier = get_sentiment_pipeline()

    raw = classifier(text, truncation=True, max_length=512)

    # transformers 버전에 따라 [[...]] 형태로 감싸져 나올 수 있어 평탄화
    if raw and isinstance(raw[0], list):
        raw = raw[0]

    scores = sorted(raw, key=lambda item: item["score"], reverse=True)
    top = scores[0]

    all_scores = [
        {"label": item["label"], "score": round(item["score"], 4)}
        for item in scores
    ]

    lines = [
        f"{item['label'].capitalize()}: {item['score'] * 100:.2f}%"
        for item in scores
    ]
    output_text = "\n".join(lines)

    return {
        "model_id": MODEL_ID,
        "label": top["label"],
        "score": round(top["score"], 4),
        "all_scores": all_scores,
        "output_text": output_text,
    }