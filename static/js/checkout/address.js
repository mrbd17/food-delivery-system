import {getCSRFToken} from "../accounts/base.js"

export const addressAPI = {

    async listAddresses(){
        const res = await fetch("/api/v1/orders/addresses/", {
            credentials: "include"
        })

        return handleResponse(res)
    },

    async createAddress(data){
        const res = await fetch("/api/v1/orders/addresses/", {
            method: 'POST',
            credentials: "include",
            headers: {
                "Content-Type":"application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify((data))
        })

        return handleResponse(res)
    },

    async addressDetail(data, id){
        const res = await fetch(`/api/v1/orders/address/${id}/`, {
            method: 'PATCH',
            credentials: "include",
            headers: {
                "Content-Type":"application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify((data))
        })
        return handleResponse(res)
    },

    async deleteAddress(id){
        const res = await fetch(`/api/v1/orders/address/${id}/`, {
            method: 'DELETE',
            credentials: "include",
            headers:{
                "X-CSRFToken": getCSRFToken()
            }
        })
        return handleResponse(res)
    },
}


async function handleResponse(res){
    const text = await res.text().catch(() => '');

    let data;

    try {
        data = text ? JSON.parse(text): {}
    } catch{
        data = {raw : text}
    }

    if(!res.ok){
        console.error("Fetch Failed", 
            { url: res.url,
            status: res.status,
            statusText: res.statusText,
            body:data
        });

        throw new Error(
            data.detail || 
            data.error || 
            `Request Failed${res.status}`
        );
    }

    return data
}