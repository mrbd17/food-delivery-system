import {getCSRFToken} from "../accounts/base.js"

export const OrderAPI = {
    async list(){
        const res = await fetch('/api/v1/orders/list/',{
            credentials:"include"
        })

        return handleResponse(res)
    },

    async detail(id){  
        const res = await fetch(`/api/v1/orders/${id}/`,{
            method: "GET",
            credentials:"include",
        })

        return handleResponse(res)

    },

    async cancel(order_id){
        const res = await fetch(`/api/v1/orders/cancel-order/${order_id}/`,{
            method: "PATCH",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            }
        });

        return handleResponse(res);
    },

    async create(address_id, payment_method){
        const res = await fetch("/api/v1/orders/create/",{
            method:"POST",
            credentials:"include",
            headers: {
                "Content-Type":"application/json",
                "X-CSRFToken": getCSRFToken()   
            },
            body: JSON.stringify({delivery_address_id:address_id, payment_method})

        })

        return handleResponse(res)
    }
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