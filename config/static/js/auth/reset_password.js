const passwordInput = document.getElementById("password");
const confirmInput = document.getElementById("confirm");
const submitBtn = document.getElementById("submit-btn");

const strengthFill = document.getElementById("strength-fill");
const strengthText = document.getElementById("strength-text");

const ruleLength = document.getElementById("rule-length");
const ruleNumber = document.getElementById("rule-number");
const ruleUpper  = document.getElementById("rule-upper");

// Show / Hide password
document.querySelectorAll(".toggle-visibility").forEach(icon => {
    icon.addEventListener("click", () => {
        const target = document.getElementById(icon.dataset.target);
        const isPassword = target.type === "password";
        target.type = isPassword ? "text" : "password";
        icon.classList.toggle("fa-eye");
        icon.classList.toggle("fa-eye-slash");
    });
});

function updateStrength() {
    const val = passwordInput.value;

    let passed = 0;

    if (val.length >= 8) {
        ruleLength.classList.add("valid");
        passed++;
    } else ruleLength.classList.remove("valid");

    if (/[0-9]/.test(val)) {
        ruleNumber.classList.add("valid");
        passed++;
    } else ruleNumber.classList.remove("valid");

    if (/[A-Z]/.test(val)) {
        ruleUpper.classList.add("valid");
        passed++;
    } else ruleUpper.classList.remove("valid");

    const percent = (passed / 3) * 100;
    strengthFill.style.width = percent + "%";

    if (passed === 1) {
        strengthFill.style.background = "#ef4444";
        strengthText.textContent = "Weak";
    } else if (passed === 2) {
        strengthFill.style.background = "#f59e0b";
        strengthText.textContent = "Medium";
    } else if (passed === 3) {
        strengthFill.style.background = "#16a34a";
        strengthText.textContent = "Strong";
    } else {
        strengthFill.style.background = "#ef4444";
        strengthText.textContent = "Weak";
    }

    // Enable submit only if strong + confirm matches
    if (passed === 3 && val && val === confirmInput.value) {
        submitBtn.disabled = false;
    } else {
        submitBtn.disabled = true;
    }
}

passwordInput.addEventListener("input", updateStrength);
confirmInput.addEventListener("input", updateStrength);

// Loader on submit
document.getElementById("reset-form").addEventListener("submit", () => {
    submitBtn.classList.add("loading");
    submitBtn.disabled = true;
});
