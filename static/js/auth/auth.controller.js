import {AuthAPI} from "./auth.service.js"
import {emit} from '../core/events.js';
class AuthController {
    constructor(){
        this.AuthAPI = new AuthAPI();
        this.emit = emit;

        this.container = null;
        this.loginForm = null;
        this.registerForm = null;
        this.loginBtn = null;
        this.signUpBtn = null;
        this.googleBtn = null;

        this.setupElement();
        this.attachEvents();
        this.initMode();
    };

    setloading(button, isLoading){
        if(!button) return;
        if(isLoading){
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            setTimeout(() => {
               button.textContent = 'Loading... ' 
            },5000)
            
        } else{
            button.disabled = false;
            button.textContent = button.dataset.originalText || 'Submit'
        }
    }
    

    setupElement(){
        this.container = document.getElementById("container");
        this.googleBtn = document.getElementById("googleSignUp");

        this.loginBtn = document.getElementById("signIn");
        this.signUpBtn = document.getElementById("signUp");

        this.loginForm = document.getElementById("loginForm");
        this.registerForm = document.getElementById("registerForm")

        if (!this.container){
            console.log("no container");
            return
        }
    };

    attachEvents(){
        this.loginBtn?.addEventListener("click", () => this.switchMode("login"));
        this.signUpBtn?.addEventListener("click", () => this.switchMode("signup"))
        
        this.loginForm?.addEventListener("submit", (e) => this.handleLogin(e))
        this.registerForm?.addEventListener("submit", (e) => this.handleRegister(e));

        document.querySelectorAll(".toggle-password").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.preventDefault();
                this.togglePassword(e.currentTarget);
            });
        });
    }

    initMode(){
        const mode = new URLSearchParams(window.location.search).get("mode") || "login";
        this.switchMode(mode, false)
    }

    switchMode(mode, updateUrl=true){
        const isSignup = mode === 'signup';

        this.container?.classList.toggle('right-panel-active', isSignup);
        this.googleBtn.style.display = isSignup ? 'block':'none';

        if (updateUrl){
            window.history.replaceState(null, '', `?mode=${mode}`)
        }
    }

    getErrorMessage(errors){
        if(!errors) return [];

        return Object.values(errors)
            .flat()
            .filter(Boolean)
    }

    async handleRegister(e){
        e.preventDefault();

        const button = e.target.querySelector('button[type=submit]');
        const data = Object.fromEntries(new FormData(this.registerForm));

        if (data.password1 !== data.password2){
            this.emit("toast:error", {message: "Passwords dosn't match"});
            return;
        }

        if (data.password1.length < 8){
            this.emit("toast:error", {message: "Password must be at least 8 characters"})
            return;
        }

        this.setloading(button, true);

        const result = await this.AuthAPI.register(data);

        this.setloading(button, false);
        if(result.success){
            
            this.emit("toast:success", {message:result.errors[0]});
            this.registerForm.reset();

            setTimeout(() => {
                window.location.href = '/api/account/email/send-otp/'
            },1500);

        }else {
            this.getErrorMessage(result.errors)
                .forEach(messages => {
                    this.emit("toast:error", {message:messages})
                })
        }
    }
    async handleLogin(e){
        e.preventDefault();

        const button = e.target.querySelector('button[type=submit]');
        const data = Object.fromEntries(new FormData(this.loginForm));

        
        this.setloading(button, true);

        const result = await this.AuthAPI.login(data);

        this.setloading(button, false);
        if(result.success){

            setTimeout(() => {
                this.emit("toast:success", {message:"Logged in successfully"});
                window.location.href = '/'
            },4000);

        }else {
            console.log(result.message)
            this.emit("toast:error", {message:result.message})
        }
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
    
}

const authConstroller = new AuthController()