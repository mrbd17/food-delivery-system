import {getCSRFToken} from "../accounts/base.js";

export class AuthAPI {
    constructor(){
        this.CSRFToken = getCSRFToken();
        this.API_BASE = "/api/account/";
    }

    async loginWithGoogle(credentialResponse, mode){
        try {
            const res = await fetch(`${this.API_BASE}google/`,{
                method:"POST",
                headers:{
                    "Content-Type":"application/json",
                    "X-CSRFToken":this.getCSRFToken,
                },
                credentials:"include", 
                body: JSON.stringify({
                    token:credentialResponse.credential,
                    mode:mode
                })              
            })

            const data  = await res.json();

            if (!res.ok){
                throw new Error(data.message || "Authentication failed")
            }

            return {
                success:true,
                data:data,
                message: data.message
            }
        } catch (error){
            console.log("Google login error", error);
            return {
                success:false,
                message: error.message || 'Network error',
                data: null
            }
        } 
    }

    async request(path, data){
        try {
            const res = await fetch(path, {
                method: "POST",
                headers: {
                    "Content-Type":"application/json",
                    "X-CSRFToken": this.CSRFToken
                },

                credentials:'same-origin',
                body: JSON.stringify(data)
            });

            const result =  await res.json()
            console.log(result)
            console.log(res.status)

            if(!res.ok){
                return {
                    success:false,
                    errors:result.errors || {message:result.message} ||"Unknown error",
                    message:result.massage
                }
            }

            return result
        } catch(error){
            return {
                success:false,
                errors:{network: "Network error. Check your connection"}
            }
        }
    } 

    async google_auth(data){
        return this.request(`${this.API_BASE}google/`, data)
    }

    async login(data){
        return this.request(`${this.API_BASE}login/`, data)
    }
    
    async register(data){
        return this.request(`${this.API_BASE}register/`, data)
    }

    async logout(){
        return this.request(`${this.API_BASE}logout/`,{})
    }
}