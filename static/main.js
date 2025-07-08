// static/main.js

document.getElementById("imageInput").addEventListener("change", e => {
  const file = e.target.files[0];
  const preview = document.getElementById("preview");
  if (file) preview.src = URL.createObjectURL(file);
});

document.getElementById("analyzeBtn").addEventListener("click", async () => {
  const input = document.getElementById("imageInput");
  const file = input.files[0];
  const resultEl = document.getElementById("result");

  if (!file) {
    resultEl.textContent = "⚠️ No image selected!";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  resultEl.textContent = "⏳ Analyzing...";

  try {
    const res = await fetch("/analyze", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    if (res.ok) {
      resultEl.textContent = [
        `📌 Label: ${data.label}`,
        `📝 Caption: ${data.caption?.[0] || "-"}`,
        `🏷️ Scene: ${data.scene || "-"}`,
        `💯 Skin %: ${data.skin_percent || 0}`,
        `🕺 Pose: ${data.pose || "-"}`,
        `🧍‍♂️ Human: ${data.contains_human ? "Yes" : "No"}`,
      ].join("\n");
    } else {
      resultEl.textContent = `❌ Error: ${data.error || "Unknown error"}`;
    }

  } catch (err) {
    resultEl.textContent = `❌ Exception: ${err.message}`;
  }
});
