import { OTPHandler } from '../handlers/otp-handler.js';
import {getCSRFToken} from '../../accounts/base.js';
import { emit } from '../../core/events.js';

class OTPVerifyPage {
    constructor() {
        this.CSRFToken = getCSRFToken()
        this.emit = emit;
        this.otpHandler = new OTPHandler(this.CSRFToken);
        this.verificationToken = new URLSearchParams(window.location.search).get('token');
        
        if (!this.verificationToken) {
            this.showError("Invalid or expired session. Please register again.");
            return;
        }

        this.setupElements();
        this.attachEvents();
        this.handleOTPInput();
    }

    setupElements() {
        this.form = document.getElementById('otp-form');
        this.inputs = document.querySelectorAll('.otp-input');
        this.verifyBtn = document.getElementById('verify-btn');
        this.resendBtn = document.getElementById('resend-btn');
        this.resendTimer = document.getElementById('resend-timer');
        this.timerSeconds = document.getElementById('timer-seconds');
    }

    attachEvents() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.resendBtn.addEventListener('click', () => this.handleResend());
    }

    handleOTPInput() {
        this.inputs.forEach((input, index) => {

            input.addEventListener("input", () => {
                input.value = input.value.replace(/[^0-9]/g, "");
                
                if(input.value && index < this.inputs.length - 1) {
                    this.inputs[index + 1].focus();
                }      
            });

            input.addEventListener("paste", (e) => {
                e.preventDefault();

                const paste = e.clipboardData
                    .getData("text")
                    .replace(/\D/g,"")
                    .split("");
                
                paste.forEach((num, i) => {
                    if(i < this.inputs.length) {
                        this.inputs[i].value = num;
                    }
                });

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Backspace' && !input.value && index > 0) {
                    this.inputs[index - 1].focus();
                }
            });
        });

        });
    }

    async handleSubmit(e) {
        e.preventDefault();

        const otpCode = Array.from(this.inputs)
            .map(input => input.value)
            .join('');

        if (otpCode.length !== 6) {
            this.emit('toast:error', { message: 'Please enter all 6 digits' });
            return;
        }

        this.setLoading(this.verifyBtn, true);
        
        const data = await this.otpHandler.verifyOTP(otpCode, this.verificationToken);
        console.log(data)
        console.log(data.status)
        this.setLoading(this.verifyBtn, false);

        if (data) {
            setTimeout(() => {
                window.location.href = '/api/account/auth?mode=login';
            }, 1500);
        } else {
            this.emit("toast:error", {message:data.message})
        }
    }

    async handleResend() {
        this.setLoading(this.resendBtn, true);
        
        const success = await this.otpHandler.resendOTP(this.verificationToken);

        this.setLoading(this.resendBtn, false);

        if (success) {
            this.startResendTimer();
        }
    }

    startResendTimer() {
        this.resendBtn.disabled = true;
        this.resendTimer.style.display = 'inline';
        
        let seconds = 60;
        const interval = setInterval(() => {
            this.timerSeconds.textContent = seconds - 1;
            seconds--;

            if (seconds < 0) {
                clearInterval(interval);
                this.resendBtn.disabled = false;
                this.resendTimer.style.display = 'none';
            }
        }, 1000);
    }

    setLoading(button, isLoading) {
        button.disabled = isLoading;
        button.textContent = isLoading ? 'Verifying...' : 'Verify Code';
    }

    showError(message) {
        document.querySelector('.otp-card').innerHTML = `
            <h2>Error</h2>
            <p style="color: red;">${message}</p>
            <a href="/api/account/auth?mode=signup" class="back-link">Back to Login</a>
        `;
    }
}

new OTPVerifyPage();