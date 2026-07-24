document.addEventListener("DOMContentLoaded", () => {
  const inputEl = document.getElementById("input-text");
  const runBtn = document.getElementById("run-btn");
  const loadingEl = document.getElementById("loading");
  const errorBox = document.getElementById("error-box");
  const resultBox = document.getElementById("result-box");
  const labelEl = document.getElementById("result-label");
  const scoreEl = document.getElementById("result-score");
  const scoresEl = document.getElementById("result-scores");
  const historyList = document.getElementById("history-list");

  // 비로그인 사용자의 기록 (새로고침 시 초기화됨)
  const localHistory = [];

  function setBusy(isBusy) {
    runBtn.disabled = isBusy;
    inputEl.disabled = isBusy;
    loadingEl.classList.toggle("hidden", !isBusy);
  }

  function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
    resultBox.classList.add("hidden");
  }

  function showResult(data) {
    errorBox.classList.add("hidden");

    labelEl.textContent = capitalize(data.label);
    scoreEl.textContent = (data.score * 100).toFixed(2) + "%";

    scoresEl.innerHTML = "";
    data.all_scores.forEach((item) => {
      const li = document.createElement("li");
      li.textContent =
        capitalize(item.label) + ": " + (item.score * 100).toFixed(2) + "%";
      scoresEl.appendChild(li);
    });

    resultBox.classList.remove("hidden");
  }

  function capitalize(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  function addHistory(text, data) {
    // 로그인 사용자는 서버가 내려준 DB 기록을 그대로 표시
    if (data.is_authenticated) {
      renderServerHistory(data.histories);
      return;
    }

    localHistory.unshift({
      text: text,
      label: capitalize(data.label),
      score: (data.score * 100).toFixed(2),
    });

    if (localHistory.length > 5) {
      localHistory.pop();
    }

    renderHistory();
  }

  function renderHistory() {
    historyList.innerHTML = "";

    if (localHistory.length === 0) {
      const li = document.createElement("li");
      li.className = "history-empty";
      li.textContent = "아직 실행 기록이 없습니다.";
      historyList.appendChild(li);
      return;
    }

    localHistory.forEach((item) => {
      const preview =
        item.text.length > 40 ? item.text.slice(0, 40) + "..." : item.text;

      const li = document.createElement("li");
      li.textContent = preview + " → " + item.label + " (" + item.score + "%)";
      historyList.appendChild(li);
    });
  }

  function renderServerHistory(histories) {
    historyList.innerHTML = "";

    if (!histories || histories.length === 0) {
      const li = document.createElement("li");
      li.className = "history-empty";
      li.textContent = "아직 실행 기록이 없습니다.";
      historyList.appendChild(li);
      return;
    }

    histories.forEach((item) => {
      const preview =
        item.input_text.length > 40
          ? item.input_text.slice(0, 40) + "..."
          : item.input_text;

      const li = document.createElement("li");
      li.textContent = preview + " → " + capitalize(item.label);
      historyList.appendChild(li);
    });
  }

  runBtn.addEventListener("click", async () => {
    const text = inputEl.value.trim();

    setBusy(true);

    try {
      const data = await postJSON("/sentiment/run/", { text: text });
      showResult(data);
      addHistory(text, data);
    } catch (error) {
      showError(error.message);
    } finally {
      setBusy(false);
    }
  });
});