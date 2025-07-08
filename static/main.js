// static/main.js

document.addEventListener("DOMContentLoaded", () => {
  const imageInput = document.getElementById("imageInput");
  const preview = document.getElementById("preview");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const resultDiv = document.getElementById("result");

  let currentImage;

  imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      preview.src = reader.result;
    };
    reader.readAsDataURL(file);
    currentImage = file;
    resultDiv.innerHTML = "...";
  });

  analyzeBtn.addEventListener("click", async () => {
    if (!currentImage) return;
    const formData = new FormData();
    formData.append("file", currentImage);

    resultDiv.innerHTML = "⏳ Analyzing...";

    try {
      const res = await fetch("/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.error) {
        resultDiv.innerHTML = `<div class="error">❌ Error: ${data.error}</div>`;
        return;
      }

      renderResult(data);
    } catch (err) {
      resultDiv.innerHTML = `<div class="error">❌ ${err}</div>`;
    }
  });

  function renderResult(data) {
    const label = data.label || "unknown";
    const safe = label.toLowerCase() === "safe";
    const scene = data.scene?.split(" ")[0] || "";
    const confidence = data.blip_confidence || 0;
    const caption = data.caption?.[0] || "";
    const containsHuman = !!data.contains_human;
    const pose = data.pose || "Unknown";
    const maxSkin = data.max_skin_ratio || 0;
    const timings = data.timings || {};

    const timingRows = Object.entries(timings)
      .map(([k, v]) => `<tr><td>${k}</td><td>${v.toFixed(2)}s</td></tr>`)
      .join("");

    resultDiv.innerHTML = `
      <div class="results">
        <div class="label ${safe ? "safe" : "nsfw"}">
          ${safe ? "✅ Safe" : "⚠️ NSFW"}
        </div>
        <p><strong>Caption:</strong> ${caption}</p>
        <p><strong>Scene:</strong> ${scene}</p>
        <p><strong>BLIP Confidence:</strong> ${(confidence * 100).toFixed(1)}%</p>
        <p><strong>Contains Human:</strong> ${containsHuman ? "✅" : "❌"}</p>
        <p><strong>Pose Detected:</strong> ${pose}</p>
        <p><strong>Skin Exposure (max):</strong> ${(maxSkin * 100).toFixed(1)}%</p>
        <details>
          <summary>⏱ Timing per step</summary>
          <table class="timings">
            ${timingRows}
          </table>
        </details>
      </div>
    `;
  }
});
