import { PasswordResetHandler } from '../handlers/password-reset-handler.js';
import { emit } from '/static/js/core/events.js';

class ForgotPasswordPage {
    constructor() {
        this.resetHandler = new PasswordResetHandler(emit);
        this.form = document.getElementById('forgot-password-form');
        this.sendBtn = document.getElementById('send-btn');

        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    async handleSubmit(e) {
        e.preventDefault();

        const email = document.getElementById('email').value;
        this.setLoading(this.sendBtn, true);

        const token = await this.resetHandler.requestPasswordReset(email);

        this.setLoading(this.sendBtn, false);

        if (token) {
            window.location.href = `/auth/reset-password?token=${token}`;
        }
    }

    setLoading(button, isLoading) {
        button.disabled = isLoading;
        button.textContent = isLoading ? 'Sending...' : 'Send Verification Code';
    }
}

new ForgotPasswordPage();