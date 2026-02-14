async function analyzeEmail() {

    const emailText = document.getElementById("emailInput").value;
    const resultDiv = document.getElementById("result");
    const spinner = document.getElementById("spinner");
    const button = document.getElementById("analyzeBtn");

    if (!emailText.trim()) {
        resultDiv.innerHTML = "Please enter email text.";
        resultDiv.style.backgroundColor = "#ffdddd";
        return;
    }

    // Show spinner
    spinner.classList.remove("hidden");
    button.disabled = true;
    resultDiv.innerHTML = "";
    resultDiv.style.backgroundColor = "transparent";

    try {

        const response = await fetch("http://localhost:8000/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: emailText
            })
        });

        const data = await response.json();

        resultDiv.innerHTML = `
            <strong>Prediction:</strong> ${data.prediction} <br>
            <strong>Confidence:</strong> ${(data.confidence_score * 100).toFixed(2)}% <br>
            <strong>Model:</strong> ${data.model_name} <br>
            <strong>Version:</strong> ${data.model_version}
        `;

        resultDiv.style.backgroundColor =
            data.is_phishing ? "#ffdddd" : "#ddffdd";

    } catch (error) {
        resultDiv.innerHTML = "Error connecting to API.";
        resultDiv.style.backgroundColor = "#ffdddd";
    }

    // Hide spinner
    spinner.classList.add("hidden");
    button.disabled = false;
}
