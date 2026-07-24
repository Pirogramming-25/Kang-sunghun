document.addEventListener("DOMContentLoaded", () => {
  const inputEl = document.getElementById("input-text");
  const runBtn = document.getElementById("run-btn");
  const regenBtn = document.getElementById("regen-btn");
  const loadingEl = document.getElementById("loading");
  const errorBox = document.getElementById("error-box");
  const resultBox = document.getElementById("result-box");

  const originalEl = document.getElementById("result-original");
  const summaryEl = document.getElementById("result-summary");
  const lengthsEl = document.getElementById("result-lengths");
  const sentLabelEl = document.getElementById("result-sentiment-label");
  const sentScoreEl = document.getElementById("result-sentiment-score");
  const toxLabelEl = document.getElementById("result-tox-label");
  const toxScoreEl = document.getElementById("result-tox-score");
  const toxScoresEl = document.getElementById("result-tox-scores");
  const verdictEl = document.getElementById("result-verdict");
  const historyList = document.getElementById("history-list");

  // 재생성 시 다시 사용할 원문
  let lastText = "";

  function setBusy(isBusy) {
    runBtn.disabled = isBusy;
    regenBtn.disabled = isBusy;
    inputEl.disabled = isBusy;
    loadingEl.classList.toggle("hidden", !isBusy);
  }

  function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
    resultBox.classList.add("hidden");
  }

  function capitalize(text) {
    return text ? text.charAt(0).toUpperCase() + text.slice(1) : "";
  }

  function truncate(text, limit) {
    return text.length > limit ? text.slice(0, limit) + "..." : text;
  }

  function showResult(text, data) {
    errorBox.classList.add("hidden");

    originalEl.textContent = text;
    summaryEl.textContent = data.summary;
    lengthsEl.textContent =
      "원문 " + data.original_length.toLocaleString() + "자 → 요약문 " +
      data.summary_length.toLocaleString() + "자 (비율 " +
      data.summary_ratio.toFixed(2) + "%)";

    sentLabelEl.textContent = capitalize(data.sentiment.label);
    sentScoreEl.textContent = (data.sentiment.score * 100).toFixed(2) + "%";

    toxLabelEl.textContent = data.toxicity.highest_label;
    toxScoreEl.textContent =
      (data.toxicity.highest_score * 100).toFixed(2) + "%";

    toxScoresEl.innerHTML = "";
    data.toxicity.all_scores.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item.label + ": " + (item.score * 100).toFixed(2) + "%";
      toxScoresEl.appendChild(li);
    });

    verdictEl.textContent = data.verdict;

    resultBox.classList.remove("hidden");
    regenBtn.classList.remove("hidden");
  }

  function renderHistory(histories) {
    historyList.innerHTML = "";

    if (!histories || histories.length === 0) {
      const li = document.createElement("li");
      li.className = "history-empty";
      li.textContent = "아직 실행 기록이 없습니다.";
      historyList.appendChild(li);
      return;
    }

    histories.forEach((item) => {
      const li = document.createElement("li");
      li.textContent =
        truncate(item.input_text, 40) +
        " → " + capitalize(item.sentiment_label) +
        " / " + item.toxicity_label +
        (item.regenerated ? " (재생성)" : "");
      historyList.appendChild(li);
    });
  }

  async function run(text, regenerate) {
    setBusy(true);

    try {
      const data = await postJSON("/combo/run/", {
        text: text,
        regenerate: regenerate,
      });

      lastText = text;
      showResult(text, data);
      renderHistory(data.histories);
    } catch (error) {
      showError(error.message);
    } finally {
      setBusy(false);
    }
  }

  runBtn.addEventListener("click", () => {
    run(inputEl.value.trim(), false);
  });

  // 재생성: 원문을 다시 입력받지 않고 모델 Pipeline을 다시 실행
  regenBtn.addEventListener("click", () => {
    if (!lastText) {
      return;
    }
    run(lastText, true);
  });
});