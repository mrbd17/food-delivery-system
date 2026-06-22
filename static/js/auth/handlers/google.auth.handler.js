export class GoogleAuthHandler {
    constructor(authService, emit) {
        this.authService = authService;
        this.emit = emit;
        this.initialize = false;
    }

    setupGoogleAuth(clientId, callback) {
        this.loadGoogleAPI()
            .then(() => this.initializeGoogleSignIn(clientId, callback))
            .catch(error => console.error("Google setup failed:", error));
    }

    loadGoogleAPI() {
        return new Promise((resolve, reject) => {
            if (window.google?.accounts?.id) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://accounts.google.com/gsi/client';
            script.async = true;
            script.defer = true;

            script.referrerPolicy = "strict-origin-when-cross-origin"; 

            script.onload = () => {
                if (window.google?.accounts?.id) {
                    resolve();
                } else {
                    reject(new Error("Google API not available after load"));
                }
            };

            script.onerror = () => {
                reject(new Error("Failed to load Google API script"));
            };

            document.head.appendChild(script);
        });
    }

    initializeGoogleSignIn(clientId, callback) {

        if (this.initialized) {
            console.log("SKIPPED: already initialized");
            return;
        }

        this.initialized = true; 
        if (!clientId) {
            console.error("Client ID not found");
            return;
        }

        try {
            google.accounts.id.initialize({
                client_id: clientId,
                callback: callback,
                auto_select: false,
                
            });

            this.renderGoogleButtons();
        } catch (error) {
            console.error("Google initialization failed:", error);
        }
    }

    renderGoogleButtons() {
        this.renderButton('google-button-signup', 'signup_with');
        this.renderButton('google-button-signin', 'signin_with');
    }

    renderButton(containerId, text) {
        const container = document.getElementById(containerId);
        if (!container) return;

        try {
            google.accounts.id.renderButton(container, {
                theme: 'outline',
                size: 'large',
                text: text,
                width: '200'
            });
        } catch (error) {
            console.error(`Error rendering ${containerId}:`, error);
        }
    }

}