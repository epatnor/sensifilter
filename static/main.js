// static/main.js

document.getElementById("imageInput").addEventListener("change", function (e) {
    const file = e.target.files[0];
    if (file) {
        const preview = document.getElementById("preview");
        preview.src = URL.createObjectURL(file);
    }
});

document.getElementById("analyzeBtn").addEventListener("click", async function () {
    const fileInput = document.getElementById("imageInput");
    const resultBox = document.getElementById("result");

    if (!fileInput.files.length) {
        resultBox.textContent = "Please select an image first.";
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    resultBox.textContent = "Analyzing...";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (result.error) {
            resultBox.textContent = "❌ Error: " + result.error;
        } else {
            const { annotated_base64, ...rest } = result;

            if (annotated_base64) {
                const preview = document.getElementById("preview");
                preview.src = "data:image/png;base64," + annotated_base64;
            }

            resultBox.textContent = JSON.stringify(rest, null, 2);
        }
    } catch (err) {
        resultBox.textContent = "⚠️ Failed to analyze image: " + err.message;
    }
});
