document.addEventListener("DOMContentLoaded", () => {
    const signUpButton = document.getElementById("signUp");
    const signInButton = document.getElementById("signIn");
    const container = document.getElementById("container");
    const googleButton = document.getElementById("googleSignUp");

    const alerts = document.querySelectorAll(".alert");
    const params = new URLSearchParams(window.location.search);
    const mode = params.get("mode");

    if(mode === "signup") {
        container.classList.add("right-panel-active");
        googleButton.style.display = "block";
    }

    if(mode === "login") {
        container.classList.remove("right-panel-active");
        googleButton.style.display = "none";
    }
    if(alerts.length) {
        container.classList.add("right-panel-active");
        googleButton.style.display = "block";
    }

    signUpButton.addEventListener("click", () => {
        container.classList.add("right-panel-active");
        googleButton.style.display = "block";
    });

    signInButton.addEventListener("click", () => {
        container.classList.remove("right-panel-active");
        googleButton.style.display = "none";
    });
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500);
        }, 20000);
    });

    document.querySelectorAll(".toggle-password").forEach(btn => {
        btn.addEventListener("click", () => {
            const input = document.getElementById(btn.dataset.target);
            const eyeOn = btn.querySelector(".eye-on");
            const eyeOff = btn.querySelector(".eye-off");

            if(input.type === "password") {
                input.type = "text";
                eyeOn.style.display = "none";
                eyeOff.style.display = "block";
            } else {
                input.type = "password";
                eyeOn.style.display = "block";
                eyeOff.style.display = "none";
            }
        });
    });
});
