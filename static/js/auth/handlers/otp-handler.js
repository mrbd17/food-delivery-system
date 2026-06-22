export class OTPHandler {
    constructor(getCSRFToken) {
        this.verificationToken = null;
        this.CSRFToken = getCSRFToken
    }

    async sendOTP(email) {
        try {
            console.log(this.CSRFToken);
            console.log(typeof this.CSRFToken);
            const response = await fetch('/api/account/email/otp/send/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', "X-CSRFToken": this.CSRFToken },
                body: JSON.stringify({ email })
            });

            const data = await response.json();

            if (data.success) {
                console.log(data.verification_token)
                return {
                    success:true,  message:data.message, token:data.verification_token 
                }
            } else {
                return {
                    success:false,
                    message:data.message
                };
            }
        } catch (error) {
            console.error("Send OTP failed:", error);
            return false;
        }
    }

    async verifyOTP(otpCode, token) {

        try {
            const response = await fetch('/api/account/email/otp/verify/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json',"X-CSRFToken": this.CSRFToken  },
                body: JSON.stringify({
                    otp_code: otpCode,
                    verification_token: token
                })
            });

            const data = await response.json();

            if (data.success) {
                return true ;
            } else{
                
                return {
                    success:false,
                    message:data.message
                };
            } 
                
        } catch (error) {
            console.error("OTP verification failed:", error);
            return false;
        }
    }

    async resendOTP(token) {

        try {
            const response = await fetch('/api/account/email/otp/resend/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', "X-CSRFToken": this.CSRFToken },
                body: JSON.stringify({
                    verification_token: token
                })
            });

            const data = await response.json();

            if (data.success) {
                return true;
            } else {
                return false;
            }
        } catch (error) {
            console.error("Resend OTP failed:", error);
            return false;
        }
    }

}