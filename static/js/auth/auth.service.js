import {getCSRFToken} from "../accounts/base.js";

export class AuthAPI {
    constructor(){
        this.CSRFToken = getCSRFToken();
        this.API_BASE = "/api/account/";
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
                console.log("line 28 res faild")
                return {
                    success:false,
                    errors:result.errors || {message:result.message} ||"Unknown error"
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