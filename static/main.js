// static/main.js

// Run when DOM is loaded
window.addEventListener("DOMContentLoaded", () => {
  const imageInput = document.getElementById("imageInput");
  const preview = document.getElementById("preview");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const resultBox = document.getElementById("result");

  // Show image preview
  imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];
    if (file) {
      preview.src = URL.createObjectURL(file);
      resultBox.innerHTML = renderPipelineSkeleton();
    }
  });

  // Trigger analysis
  analyzeBtn.addEventListener("click", async () => {
    const file = imageInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      resultBox.innerHTML = renderPipelineSkeleton(); // Reset with placeholders

      const res = await fetch("/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.error) throw new Error(data.error);

      resultBox.innerHTML = renderResult(data);

    } catch (err) {
      resultBox.innerHTML = `<div class="error">❌ Error: ${err.message}</div>`;
    }
  });
});

// Render empty pipeline with placeholders
function renderPipelineSkeleton() {
  const steps = [
    ["Caption", "BLIP model", "…"],
    ["Scene", "Places365", "…"],
    ["Keywords", "Keyword matcher", "…"],
    ["Pose", "Pose detection", "…"],
    ["Skin", "YOLOv8 + HSV", "…"]
  ];
  return renderTable(steps, true);
}

// Render final results
function renderResult(data) {
  const steps = [
    ["Caption", "BLIP model", data.caption?.[0] || "-"],
    ["Scene", "Places365", data.scene || "-"],
    ["Keywords", "Keyword matcher", (data.keywords || []).join(", ") || "-"],
    ["Pose", "Pose detection", data.pose || "-"],
    ["Skin", "YOLOv8 + HSV", `${Math.round(data.max_skin_ratio * 100)}%`]
  ];

  const timings = data.timings || {};
  const timingLookup = {
    "caption": "Caption",
    "scene_classification": "Scene",
    "keyword_matching": "Keywords",
    "pose_detection": "Pose",
    "yolo_skin_detection": "Skin"
  };

  const finalTable = steps.map(([step, method, output]) => {
    const timing = Object.entries(timingLookup).find(([key, val]) => val === step);
    const time = timing && timings[timing[0]] ? `${timings[timing[0]].toFixed(2)}s` : "–";
    return [step, method, output, time];
  });

  const label = data.label === "safe"
    ? `<div class="badge safe">🟢 Safe</div>`
    : `<div class="badge unsafe">🔴 Unsafe</div>`;

  return `
    ${label}
    <div class="section">
      <b>Caption:</b> ${data.caption?.[0] || "-"}<br>
      <b>Scene:</b> ${data.scene || "-"}<br>
      <b>BLIP Confidence:</b> ${(data.blip_confidence * 100).toFixed(1)}%<br>
      <b>Contains Human:</b> ${data.contains_human ? "Yes" : "No"}<br>
      <b>Pose Detected:</b> ${data.pose || "-"}<br>
      <b>Skin Exposure (max):</b> ${Math.round(data.max_skin_ratio * 100)}%<br>
    </div>
    <details class="timing-section" open>
      <summary>⏱️ Timing per step</summary>
      ${renderTable(finalTable)}
    </details>
  `;
}

// Render compact results table
function renderTable(rows, placeholder = false) {
  const header = `
    <div class="table-row header">
      <div>Step</div><div>Method</div><div>Result</div><div>Time</div>
    </div>`;
  const body = rows.map(row => `
    <div class="table-row ${placeholder ? "placeholder" : ""}">
      <div>${row[0]}</div><div>${row[1]}</div><div>${row[2]}</div><div>${row[3] || "–"}</div>
    </div>`).join("");
  return `<div class="table">${header}${body}</div>`;
}
