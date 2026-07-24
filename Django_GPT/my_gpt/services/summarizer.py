from functools import lru_cache

from transformers import pipeline

from .common import get_pipeline_device

MODEL_ID = "sshleifer/distilbart-cnn-6-6"


@lru_cache(maxsize=1)
def get_summarizer_pipeline():
    """
    문서 요약 파이프라인을 최초 1회만 생성하고 이후에는 재사용한다.
    """
    return pipeline(
        task="summarization",
        model=MODEL_ID,
        device=get_pipeline_device(),
    )


def summarize_text(text: str, do_sample: bool = False) -> dict:
    """
    영어 문서를 요약한다.
    입력값 검증은 View에서 끝난 상태라고 가정한다.
    """
    summarizer = get_summarizer_pipeline()

    options = {
        "max_length": 180,
        "min_length": 40,
        "truncation": True,
    }

    if do_sample:
        options.update(
            {
                "do_sample": True,
                "top_p": 0.9,
                "temperature": 0.8,
            }
        )

    raw = summarizer(text, **options)
    summary = raw[0]["summary_text"].strip()

    original_length = len(text)
    summary_length = len(summary)
    summary_ratio = (
        round(summary_length / original_length * 100, 2)
        if original_length
        else 0.0
    )

    output_text = (
        f"원문 길이: {original_length:,}자\n"
        f"요약문 길이: {summary_length:,}자\n"
        f"요약 비율: {summary_ratio:.2f}%\n\n"
        f"요약 결과:\n{summary}"
    )

    return {
        "model_id": MODEL_ID,
        "summary": summary,
        "original_length": original_length,
        "summary_length": summary_length,
        "summary_ratio": summary_ratio,
        "output_text": output_text,
    }