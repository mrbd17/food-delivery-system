export class FormAuthHandler {
    constructor(authService, emit) {
        this.authService = authService;
        this.emit = emit;
    }

    attachFormEvents(loginForm, registerForm, handlers) {
        loginForm?.addEventListener("submit", (e) => 
            this.handleLoginSubmit(e, handlers.onSuccess)
        );
        
        registerForm?.addEventListener("submit", (e) => 
            this.handleRegisterSubmit(e, handlers.onSuccess)
        );
    }

    async handleLoginSubmit(e, onSuccess) {
        e.preventDefault();
        const button = e.target.querySelector('button[type=submit]');
        const formData = Object.fromEntries(new FormData(e.target));

        this.setLoading(button, true);
        const result = await this.authService.login(formData);
        this.setLoading(button, false);

        onSuccess(result, 'login');
    }

    async handleRegisterSubmit(e, onSuccess) {
        e.preventDefault();
        const button = e.target.querySelector('button[type=submit]');
        const formData = Object.fromEntries(new FormData(e.target));

        if (!this.validatePasswords(formData.password1, formData.password2)) {
            return;
        }

        this.setLoading(button, true);
        const result = await this.authService.register(formData);
        this.setLoading(button, false);

        onSuccess(result, 'signup');
    }

    validatePasswords(password1, password2) {
        if (password1 !== password2) {
            this.emit("toast:error", { message: "Passwords don't match" });
            return false;
        }
        if (password1.length < 8) {
            this.emit("toast:error", { message: "Password must be at least 8 characters" });
            return false;
        }
        return true;
    }

    setLoading(button, isLoading) {
        if (!button) return;

        if (isLoading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.textContent = 'Loading...';
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || button.textContent;
        }
    }
}