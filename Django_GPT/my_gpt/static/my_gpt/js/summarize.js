document.addEventListener("DOMContentLoaded", () => {
  const inputEl = document.getElementById("input-text");
  const runBtn = document.getElementById("run-btn");
  const loadingEl = document.getElementById("loading");
  const errorBox = document.getElementById("error-box");
  const resultBox = document.getElementById("result-box");
  const originalEl = document.getElementById("result-original");
  const lengthEl = document.getElementById("result-length");
  const ratioEl = document.getElementById("result-ratio");
  const summaryEl = document.getElementById("result-summary");
  const historyList = document.getElementById("history-list");

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

    originalEl.textContent = data.original_length.toLocaleString() + "자";
    lengthEl.textContent = data.summary_length.toLocaleString() + "자";
    ratioEl.textContent = data.summary_ratio.toFixed(2) + "%";
    summaryEl.textContent = data.summary;

    resultBox.classList.remove("hidden");
  }

  function truncate(text, limit) {
    return text.length > limit ? text.slice(0, limit) + "..." : text;
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
        truncate(item.input_text, 40) + " → " + truncate(item.summary, 50);
      historyList.appendChild(li);
    });
  }

  runBtn.addEventListener("click", async () => {
    const text = inputEl.value.trim();

    setBusy(true);

    try {
      const data = await postJSON("/summarize/run/", { text: text });
      showResult(data);
      renderHistory(data.histories);
    } catch (error) {
      showError(error.message);
    } finally {
      setBusy(false);
    }
  });
});