// static/main.js

document.addEventListener("DOMContentLoaded", () => {
  const imageInput = document.getElementById("imageInput");
  const preview = document.getElementById("preview");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const resultBox = document.getElementById("result");
  const tableBody = document.querySelector("#pipelineTable tbody");

  // Preview selected image
  imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];
    if (file) {
      preview.src = URL.createObjectURL(file);
      resultBox.innerHTML = "";
      resetTable();
    }
  });

  // Analyze button click
  analyzeBtn.addEventListener("click", async () => {
    const file = imageInput.files[0];
    if (!file) return;

    resultBox.innerHTML = "🔄 Processing...";
    updateTableStatus("running");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/analyze", { method: "POST", body: formData });
      const data = await res.json();

      if (data.error) {
        resultBox.innerHTML = `<span class="error">❌ Error: ${data.error}</span>`;
        updateTableStatus("error");
        return;
      }

      // Swap to annotated image if present
      if (data.annotated_url) {
        preview.src = data.annotated_url;
      }

      // Render results
      renderSummary(data);
      renderTable(data);

    } catch (err) {
      resultBox.innerHTML = `<span class="error">❌ ${err.message}</span>`;
    }
  });

  // Pre-fill table with all steps in gray
  function resetTable() {
    const steps = [
      ["Caption", "BLIP model", "-", "-"],
      ["Scene", "Places365", "-", "-"],
      ["Keywords", "Keyword matcher", "-", "-"],
      ["Pose", "Pose detection", "-", "-"],
      ["Skin", "YOLOv8 + HSV", "-", "-"]
    ];
    tableBody.innerHTML = steps.map(row =>
      `<tr class="pending"><td>${row[0]}</td><td>${row[1]}</td><td>${row[2]}</td><td>${row[3]}</td></tr>`
    ).join("");
  }

  // Replace placeholders with actual data
  function renderTable(data) {
    const timings = data.timings || {};
    const rows = [
      ["Caption", "BLIP model", data.caption?.[0] || "-", timings.caption],
      ["Scene", "Places365", data.scene || "-", timings.scene_classification],
      ["Keywords", "Keyword matcher", data.keywords?.join(", ") || "-", timings.keyword_matching],
      ["Pose", "Pose detection", data.pose || "-", timings.pose_detection],
      ["Skin", "YOLOv8 + HSV", (data.max_skin_ratio * 100).toFixed(0) + "%", timings.yolo_skin_detection]
    ];
    tableBody.innerHTML = rows.map(([step, method, result, time]) =>
      `<tr><td>${step}</td><td>${method}</td><td>${result}</td><td>${time ? time.toFixed(2) + "s" : "-"}</td></tr>`
    ).join("");
  }

  // Write summary text
  function renderSummary(data) {
    const label = data.label === "safe" ? "🟢 Safe" : "🔴 Flagged";
    const conf = Math.round(data.blip_confidence * 100) + "%";
    const skin = Math.round(data.max_skin_ratio * 100) + "%";

    resultBox.innerHTML = `
      <div class="summary ${data.label}">
        <strong>${label}</strong><br><br>
        <b>Caption:</b> ${data.caption?.[0] || "-"}<br>
        <b>Scene:</b> ${data.scene || "-"}<br>
        <b>BLIP Confidence:</b> ${conf}<br>
        <b>Contains Human:</b> ${data.contains_human ? "Yes" : "No"}<br>
        <b>Pose Detected:</b> ${data.pose || "-"}<br>
        <b>Skin Exposure (max):</b> ${skin}
      </div>
    `;
  }

  // Update pre-filled table with loading status
  function updateTableStatus(state) {
    if (state === "running") {
      tableBody.querySelectorAll("tr").forEach(tr => {
        tr.classList.remove("pending");
        tr.classList.add("processing");
      });
    }
    if (state === "error") {
      tableBody.querySelectorAll("tr").forEach(tr => {
        tr.classList.remove("processing");
        tr.classList.add("error");
      });
    }
  }

  // Init
  resetTable();
});
