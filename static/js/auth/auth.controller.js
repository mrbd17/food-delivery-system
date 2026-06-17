import { AuthAPI } from "./auth.service.js"
import { emit } from '../core/events.js';

class AuthController {
    constructor() {
        this.authService = new AuthAPI();
        this.emit = emit;

        this.container = null;
        this.loginForm = null;
        this.registerForm = null;
        this.loginBtn = null;
        this.signUpBtn = null;

        this.setupElements();
        this.attachEvents();
        this.initMode();
        this.setupGoogleAuth();
    }

    setupGoogleAuth() {
       window.initGoogleSignIn = () => {
        console.log("Google API loaded, initializing...");
        
        if (!window.google?.accounts?.id) {
            console.error("Google accounts ID not available");
            return;
        }
        
        const clientId = document.body.dataset.googleClientId;
        console.log("Client ID from HTML:", clientId); 
        if (!clientId) {
            console.error("Client ID not found");
            return;
        }

        try {
            google.accounts.id.initialize({
                client_id: clientId,
                callback: this.handleGoogleResponse.bind(this),
                auto_select: false,
            });
            
            this.renderGoogleButtons();
            console.log("Google Sign-In initialized & buttons rendered");
        } catch (error) {
            console.error("Error initializing Google Sign-In:", error);
        }
    };

    }

    renderGoogleButtons() {
        const signupContainer = document.getElementById('google-button-signup');
        if (signupContainer) {
            try {
                google.accounts.id.renderButton(signupContainer, {
                    theme: 'outline',
                    size: 'large',
                    text: 'signup_with',
                    width: '200'
                });
                console.log("Signup button rendered");
            } catch (error) {
                console.error("Error rendering signup button:", error);
            }
        }

        const signinContainer = document.getElementById('google-button-signin');
        if (signinContainer) {
            try {
                google.accounts.id.renderButton(signinContainer, {
                    theme: 'outline',
                    size: 'large',
                    text: 'signin_with',
                    width: '200'
                });
                console.log("Signin button rendered");
            } catch (error) {
                console.error("Error rendering signin button:", error);
            }
        }
    }

    setupElements() {
        this.container = document.getElementById("container");
        this.loginBtn = document.getElementById("signIn");
        this.signUpBtn = document.getElementById("signUp");
        this.loginForm = document.getElementById("loginForm");
        this.registerForm = document.getElementById("registerForm");

        if (!this.container) {
            console.error("Auth container not found");
            return;
        }
    }

    attachEvents() {
        this.loginBtn?.addEventListener("click", () => this.switchMode("login"));
        this.signUpBtn?.addEventListener("click", () => this.switchMode("signup"));

        this.loginForm?.addEventListener("submit", (e) => this.handleLoginSubmit(e));
        this.registerForm?.addEventListener("submit", (e) => this.handleRegisterSubmit(e));

        document.querySelectorAll(".toggle-password").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.preventDefault();
                this.togglePassword(e.currentTarget);
            });
        });

        document.querySelectorAll('.github-btn, .facebook-btn').forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.preventDefault();
                this.showComingSoonMessage();
            });
        });
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

    getCurrentMode() {
        return this.container?.classList.contains('right-panel-active') ? 'signup' : 'login';
    }

    switchMode(mode, updateUrl = true) {
        const isSignup = mode === 'signup';
        this.container?.classList.toggle('right-panel-active', isSignup);

        if (updateUrl) {
            window.history.replaceState(null, '', `?mode=${mode}`);
        }
    }

    initMode() {
        const mode = new URLSearchParams(window.location.search).get("mode") || "login";
        this.switchMode(mode, false);
    }

    async handleGoogleResponse(response) {
        console.log("Google response received");
        
        const mode = this.getCurrentMode();
        console.log("Current mode:", mode);

        const result = await this.authService.loginWithGoogle(response, mode);

        this.handleAuthResult(result, mode);
    }

    async handleLoginSubmit(e) {
        e.preventDefault();
        const button = e.target.querySelector('button[type=submit]');
        const formData = new FormData(this.loginForm);
        const data = Object.fromEntries(formData);

        this.setLoading(button, true);
        const result = await this.authService.loginWithEmail(data.email, data.password);
        this.setLoading(button, false);

        this.handleAuthResult(result, 'login');
    }

    async handleRegisterSubmit(e) {
        e.preventDefault();
        const button = e.target.querySelector('button[type=submit]');
        const formData = new FormData(this.registerForm);
        const data = Object.fromEntries(formData);

        if (data.password1 !== data.password2) {
            this.emit("toast:error", { message: "Passwords don't match" });
            return;
        }

        if (data.password1.length < 8) {
            this.emit("toast:error", { message: "Password must be at least 8 characters" });
            return;
        }

        this.setLoading(button, true);
        const result = await this.authService.register(data);
        this.setLoading(button, false);

        this.handleAuthResult(result, 'signup');
    }

    handleAuthResult(result, mode) {
        if (result.success) {
            const messageMap = {
                'signup': 'Account created successfully!',
                'login': 'Logged in successfully!'
            };

            this.emit("toast:success", {
                message: result.message || messageMap[mode]
            });

            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            this.emit("toast:error", { message: result.message });

            if (result.errors) {
                Object.values(result.errors).forEach(errorList => {
                    if (Array.isArray(errorList)) {
                        errorList.forEach(msg => {
                            this.emit("toast:error", { message: msg });
                        });
                    }
                });
            }
        }
    }

    showComingSoonMessage() {
        this.emit("toast:info", {
            message: "Coming soon! Currently only Google Sign-In is available."
        });
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

    getErrorMessage(errors) {
        if (!errors) return [];

        return Object.values(errors)
            .flat()
            .filter(Boolean);
    }
}

const authController = new AuthController();