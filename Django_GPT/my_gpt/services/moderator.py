from functools import lru_cache

from transformers import pipeline

from .common import get_pipeline_device

MODEL_ID = "unitary/toxic-bert"


@lru_cache(maxsize=1)
def get_moderator_pipeline():
    """
    유해 표현 분석 파이프라인을 최초 1회만 생성하고 이후에는 재사용한다.
    """
    return pipeline(
        task="text-classification",
        model=MODEL_ID,
        top_k=None,
        device=get_pipeline_device(),
    )


def moderate_text(text: str) -> dict:
    """
    영어 문장의 유해성을 분석한다.
    Multi-label 모델이므로 전체 레이블 점수를 함께 반환한다.
    """
    moderator = get_moderator_pipeline()

    raw = moderator(text, truncation=True, max_length=512)

    if raw and isinstance(raw[0], list):
        raw = raw[0]

    scores = sorted(raw, key=lambda item: item["score"], reverse=True)
    top = scores[0]

    all_scores = [
        {"label": item["label"], "score": round(item["score"], 4)}
        for item in scores
    ]

    lines = [
        f"{item['label']}: {item['score'] * 100:.2f}%" for item in scores
    ]
    output_text = (
        f"최고 위험 레이블: {top['label']}\n"
        f"위험 점수: {top['score'] * 100:.2f}%\n\n"
        + "\n".join(lines)
    )

    return {
        "model_id": MODEL_ID,
        "highest_label": top["label"],
        "highest_score": round(top["score"], 4),
        "all_scores": all_scores,
        "output_text": output_text,
    }