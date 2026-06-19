import { AuthAPI } from "./auth.service.js";
import { emit } from '../core/events.js';
import { GoogleAuthHandler } from './handlers/google.auth.handler.js';
import { FormAuthHandler } from './handlers/form.auth.handler.js';
import { UIHandler } from './handlers/ui.handler.js';

class AuthController {
    constructor() {
        this.authService = new AuthAPI();
        this.emit = emit;

        this.setupElements();
        
        this.ui = new UIHandler(this.container);
        this.googleAuth = new GoogleAuthHandler(this.authService, this.emit);
        this.formAuth = new FormAuthHandler(this.authService, this.emit);

        this.attachAllEvents();
        this.initialize();
    }

    setupElements() {
        this.container = document.getElementById("container");
        this.loginBtn = document.getElementById("signIn");
        this.signUpBtn = document.getElementById("signUp");
        this.loginForm = document.getElementById("loginForm");
        this.registerForm = document.getElementById("registerForm");

        if (!this.container) {
            console.error("Auth container not found");
        }
    }

    attachAllEvents() {
        this.ui.attachModeEvents(this.loginBtn, this.signUpBtn);
        this.ui.attachPasswordToggle();

        this.formAuth.attachFormEvents(this.loginForm, this.registerForm, {
            onSuccess: (result, mode) => this.handleAuthResult(result, mode)
        });

        document.querySelectorAll('.github-btn, .facebook-btn').forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.preventDefault();
                this.emit("toast:info", {
                    message: "Coming soon!"
                });
            });
        });
    }

    initialize() {
        this.ui.initMode();
        
        const clientId = document.body.dataset.googleClientId;
        this.googleAuth.setupGoogleAuth(
            clientId, 
            this.handleGoogleResponse.bind(this)
        );
       
    }

    async handleGoogleResponse(response) {
        const result = await this.googleAuth.handleGoogleResponse(
            response, 
            () => this.ui.getCurrentMode()
        );
        this.handleAuthResult(result, this.ui.getCurrentMode());
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
        }
    }
}

const authController = new AuthController();