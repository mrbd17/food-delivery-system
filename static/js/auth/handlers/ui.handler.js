export class UIHandler {
    constructor(container) {
        this.container = container;
    }

    attachModeEvents(loginBtn, signUpBtn) {
        loginBtn?.addEventListener("click", () => this.switchMode("login"));
        signUpBtn?.addEventListener("click", () => this.switchMode("signup"));
    }

    attachPasswordToggle() {
        document.querySelectorAll(".toggle-password").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.preventDefault();
                this.togglePassword(e.currentTarget);
            });
        });
    }

    switchMode(mode, updateUrl = true) {
        const isSignup = mode === 'signup';
        this.container?.classList.toggle('right-panel-active', isSignup);

        if (updateUrl) {
            window.history.replaceState(null, '', `?mode=${mode}`);
        }
    }

    getCurrentMode() {
        return this.container?.classList.contains('right-panel-active') ? 'signup' : 'login';
    }

    togglePassword(button) {
        const input = document.getElementById(button.dataset.target);
        if (!input) return;

        const isHidden = input.type === 'password';
        input.type = isHidden ? 'text' : 'password';

        const eyeOn = button.querySelector('.eye-on');
        const eyeOff = button.querySelector('.eye-off');

        if (eyeOn && eyeOff) {
            eyeOn.style.display = isHidden ? 'none' : 'block';
            eyeOff.style.display = isHidden ? 'block' : 'none';
        }
    }

    initMode() {
        const mode = new URLSearchParams(window.location.search).get("mode") || "login";
        this.switchMode(mode, false);
    }
}