document.addEventListener("DOMContentLoaded", () => {
  const imageInput = document.getElementById("imageInput");
  const uploadBox = document.getElementById("uploadBox");
  const preview = document.getElementById("preview");
  const annotated = document.getElementById("annotated");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const resultBox = document.getElementById("result");
  const summary = document.getElementById("summary");
  const pipelineBody = document.getElementById("pipelineBody");

  const steps = [
    ["caption", "BLIP Captioning"],
    ["scene_classification", "Places365 Scene"],
    ["pose_detection", "Human Pose Estimation"],
    ["yolo_skin_detection", "YOLOv8 + Skin Filter"],
    ["keyword_matching", "Keyword Filter"]
  ];

  // Initiera pipeline-tabellen med grått "pending"-utseende
  function initPipelineTable() {
    pipelineBody.innerHTML = "";
    for (const [key, label] of steps) {
      const row = document.createElement("tr");
      row.id = `step-${key}`;
      row.classList.add("pending");
      row.innerHTML = `
        <td>${label}</td>
        <td class="method gray">${key}</td>
        <td class="result gray">...</td>
        <td class="time gray">...</td>
      `;
      pipelineBody.appendChild(row);
    }
  }

  // Uppdatera ett steg med resultat och tid, ta bort grå ton
  function updateStep(key, result, time) {
    const row = document.getElementById(`step-${key}`);
    if (row) {
      row.querySelector(".result").textContent = result ?? "-";
      row.querySelector(".time").textContent = (time !== undefined && time !== null) ? time.toFixed(2) : "-";
      row.querySelectorAll("td").forEach(td => td.classList.remove("gray"));
      row.classList.remove("pending");
    }
  }

  uploadBox.addEventListener("click", () => {
    imageInput.click();
  });

  imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];
    if (file) {
      preview.src = URL.createObjectURL(file);
      preview.style.display = "block";
      annotated.style.display = "none";
      uploadBox.style.display = "none";
      summary.textContent = "";
      resultBox.style.display = "none";
      initPipelineTable();
      analyzeBtn.disabled = false; // Enable button when file chosen
    } else {
      preview.style.display = "none";
      annotated.style.display = "none";
      uploadBox.style.display = "flex";
      summary.textContent = "";
      resultBox.style.display = "none";
      initPipelineTable();
      analyzeBtn.disabled = true;
    }
  });

  analyzeBtn.addEventListener("click", async () => {
    const file = imageInput.files[0];
    if (!file) {
      alert("Please select an image first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    analyzeBtn.disabled = true;
    summary.textContent = "Analyzing...";
    resultBox.style.display = "none";
    annotated.style.display = "none";

    try {
      const res = await fetch("/analyze", {
        method: "POST",
        body: formData
      });

      const data = await res.json();

      if (res.ok) {
        const timings = data.timings || {};
        updateStep("caption", data.caption?.[0] || "–", timings.caption);
        updateStep("scene_classification", data.scene || "–", timings.scene_classification);
        updateStep("pose_detection", data.pose || "–", timings.pose_detection);
        updateStep("yolo_skin_detection", data.max_skin_ratio ? `${(data.max_skin_ratio * 100).toFixed(1)}% skin` : "–", timings.yolo_skin_detection);
        updateStep("keyword_matching", (data.keywords || []).join(", ") || "–", timings.keyword_matching);

        summary.innerHTML = `Label: <b>${data.label}</b>`;

        if (data.annotated_path) {
          annotated.src = data.annotated_path + "?t=" + Date.now();
          annotated.style.display = "block";
          preview.style.display = "none";
          uploadBox.style.display = "none";
        }

        resultBox.style.display = "none";
      } else {
        resultBox.textContent = "❌ " + (data.error || "Unknown error");
        resultBox.style.display = "block";
        summary.textContent = "";
      }
    } catch (err) {
      resultBox.textContent = "❌ " + err.message;
      resultBox.style.display = "block";
      summary.textContent = "";
    } finally {
      analyzeBtn.disabled = false;
    }
  });

  // Start state
  preview.style.display = "none";
  annotated.style.display = "none";
  uploadBox.style.display = "flex";
  resultBox.style.display = "none";
  summary.textContent = "";
  analyzeBtn.disabled = true;

  initPipelineTable();
});
