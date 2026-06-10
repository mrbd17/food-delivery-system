const API_BASE = "http://127.0.0.1:8000/api/v1";

import {getCSRFToken} from '../accounts/base.js';

export const CartAPI = {
    async get() {
        const res =  await fetch(`${API_BASE}/cart/`, {
            method: "GET",
            credentials: "include",
        })

        return handleResponse(res);
    },

    async addItem(product_id) {
        const res = await fetch(`${API_BASE}/cart/add/`, {
            method: "POST",
            credentials: "include",
            headers:{
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                product_id:product_id,
            })
        })
        return handleResponse(res)
    },


    async updateItem(item_id, quantity) {
        const res = await fetch(`${API_BASE}/cart/update/`, {
            method: "PATCH",
            credentials: "include",
            headers:{
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },

            body: JSON.stringify({
               item_id:item_id, quantity
            })
        })

        return handleResponse(res)
    },

    async removeItem(item_id) {
        const res = await fetch(`${API_BASE}/cart/remove/`, {
            method: "DELETE",
            credentials: "include",
            headers: {
                "Content-Type":"application/json",
                "X-CSRFToken": getCSRFToken()
                
            },
            body:  JSON.stringify({
                item_id:item_id
            })
        })
        return handleResponse(res)
    },

}

async function handleResponse(res) {
    const text = await res.text().catch(() => '')
    let data 

    try {
        data = text ? JSON.parse(text) : {}
    } catch {data = {raw : text}}
    if(!res.ok){
        console.error("Fetch Failed", {url: res.url, status:res.status, statusText: res.statusText, body:data })
        throw new Error(data.detail || data.error || "Request Failed")
    }

    if(!res.length){
        console.log("empty Response")
    }

    return data
}