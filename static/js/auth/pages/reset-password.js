import { PasswordResetHandler } from '../handlers/password-reset-handler.js';
import { emit } from '.../core/events.js';

class ResetPasswordPage {
    constructor() {
        this.resetHandler = new PasswordResetHandler(emit);
        this.token = new URLSearchParams(window.location.search).get('token');

        if (!this.token) {
            this.showError("Invalid or expired reset link");
            return;
        }

        this.setupElements();
        this.attachEvents();
    }

    setupElements() {
        this.form = document.getElementById('reset-form');
        this.passwordInput = document.getElementById('password');
        this.confirmInput = document.getElementById('confirm');
        this.submitBtn = document.getElementById('submit-btn');
        this.toggleBtns = document.querySelectorAll('.toggle-visibility');
        
        this.strengthFill = document.getElementById('strength-fill');
        this.strengthText = document.getElementById('strength-text');
        this.passwordRules = document.getElementById('password-rules');
        this.passwordMatch = document.getElementById('password-match');
    }

    attachEvents() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        this.toggleBtns.forEach(btn => {
            btn.addEventListener('click', (e) => this.togglePassword(e));
        });

        this.passwordInput.addEventListener('input', (e) => {
            this.checkPasswordStrength(e.target.value);
            this.checkPasswordMatch();
        });

        this.confirmInput.addEventListener('input', () => {
            this.checkPasswordMatch();
        });
    }

    checkPasswordStrength(password) {
        const rules = [
            { id: 'rule-length', regex: /.{8,}/, text: 'At least 8 characters' },
            { id: 'rule-number', regex: /\d/, text: 'Contains a number' },
            { id: 'rule-upper', regex: /[A-Z]/, text: 'Contains uppercase letter' },
            { id: 'rule-special', regex: /[!@#$%^&*]/, text: 'Contains special character' }
        ];

        let strength = 0;
        rules.forEach(rule => {
            const element = document.getElementById(rule.id);
            if (rule.regex.test(password)) {
                element.classList.add('valid');
                element.textContent = '✓ ' + rule.text;
                strength++;
            } else {
                element.classList.remove('valid');
                element.textContent = '✗ ' + rule.text;
            }
        });

        const strengthLevels = ['Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];
        this.strengthText.textContent = strengthLevels[strength];
        this.strengthFill.style.width = ((strength / 4) * 100) + '%';
        this.strengthFill.style.backgroundColor = this.getStrengthColor(strength);

        this.submitBtn.disabled = strength < 3;
    }

    checkPasswordMatch() {
        if (this.confirmInput.value === '') return;

        const match = this.passwordInput.value === this.confirmInput.value;
        this.passwordMatch.textContent = match ? '✓ Passwords match' : '✗ Passwords don\'t match';
        this.passwordMatch.style.color = match ? 'green' : 'red';
        
        this.submitBtn.disabled = !match;
    }

    getStrengthColor(strength) {
        const colors = ['#ef4444', '#f97316', '#eab308', '#84cc16', '#22c55e'];
        return colors[strength] || '#ef4444';
    }

    togglePassword(e) {
        const targetId = e.currentTarget.dataset.target;
        const input = document.getElementById(targetId);
        const isPassword = input.type === 'password';

        input.type = isPassword ? 'text' : 'password';
        e.currentTarget.classList.toggle('fa-eye');
        e.currentTarget.classList.toggle('fa-eye-slash');
    }

    async handleSubmit(e) {
        e.preventDefault();

        const password = this.passwordInput.value;
        const confirm = this.confirmInput.value;

        if (password !== confirm) {
            emit('toast:error', { message: 'Passwords don\'t match' });
            return;
        }

        this.setLoading(this.submitBtn, true);

        const success = await this.resetHandler.resetPassword(password, this.token);

        this.setLoading(this.submitBtn, false);

        if (success) {
            setTimeout(() => {
                window.location.href = '/auth?mode=login';
            }, 1500);
        }
    }

    setLoading(button, isLoading) {
        button.disabled = isLoading;
        button.textContent = isLoading ? 'Resetting...' : 'Reset Password';
    }

    showError(message) {
        document.querySelector('.auth-card').innerHTML = `
            <h2>Error</h2>
            <p style="color: red; margin: 20px 0;">${message}</p>
            <a href="/auth?mode=login" class="back-link">Back to Login</a>
        `;
    }
}

new ResetPasswordPage();