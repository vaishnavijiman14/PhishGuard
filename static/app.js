
document.addEventListener("DOMContentLoaded", function () {

    // SCANNER TAB SWITCHING

    const tabs = document.querySelectorAll(".scanner-tab");
    const scanType = document.getElementById("scanType");

    const messageGroup = document.getElementById("messageGroup");
    const urlGroup = document.getElementById("urlGroup");
    const mobileGroup = document.getElementById("mobileGroup");

    if (tabs.length > 0) {
        tabs.forEach(function (tab) {
            tab.addEventListener("click", function () {

                tabs.forEach(t => t.classList.remove("active"));
                tab.classList.add("active");

                const type = tab.dataset.type;
                scanType.value = type;

                messageGroup.hidden = type !== "message";
                urlGroup.hidden = type !== "url";
                mobileGroup.hidden = type !== "mobile";
            });
        });
    }

    // SECURITY SCANNER

    const scanForm = document.getElementById("scanForm");

    if (scanForm) {
        scanForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const type = scanType.value;
            let value = "";

            if (type === "message") {
                value = document.getElementById("scanInput").value.trim();
            } else if (type === "url") {
                value = document.getElementById("urlInput").value.trim();
            } else {
                value = document.getElementById("mobileInput").value.trim();
            }

            const resultBox = document.getElementById("scanResult");
            const resultTitle = document.getElementById("resultTitle");
            const resultMessage = document.getElementById("resultMessage");
            const resultDetails = document.getElementById("resultDetails");

            resultBox.hidden = false;
            resultTitle.textContent = "Checking...";
            resultMessage.textContent = "Please wait while we analyze your input.";
            resultDetails.textContent = "";

            if (!value) {
                resultTitle.textContent = "Invalid Input";
                resultMessage.textContent = "Please enter a value before scanning.";
                return;
            }

            try {
                const response = await fetch("/api/check", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        type: type,
                        value: value
                    })
                });

                const data = await response.json();

                resultTitle.textContent = data.title || data.risk || "Scan Result";
resultBox.classList.remove("high-risk");

if (data.level === "high") {
    resultBox.classList.add("high-risk");
}
}
                
                resultMessage.textContent = data.message || "Analysis completed.";

                if (data.details) {
                 resultDetails.textContent = [
    ...(data.details || []),
    ...(data.tips || []).map(tip => "Tip: " + tip)
].join("\n");
                }

            } catch (error) {
                resultTitle.textContent = "Connection Error";
                resultMessage.textContent =
                    "Unable to connect to the scanner. Make sure the Flask server is running.";
            }
        });
    }

    // CONTACT FORM

    const contactForm = document.getElementById("contactForm");

    if (contactForm) {
        contactForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const name = document.getElementById("contactName").value.trim();
            const result = document.getElementById("contactResult");

            if (!name) {
                result.textContent = "Please enter your name.";
                return;
            }

            result.textContent =
                "Thank you, " + name + "! This is a demo form. Your message has not been emailed.";

            contactForm.reset();
        });
    }

});
