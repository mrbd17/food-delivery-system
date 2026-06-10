import {on} from "../core/events.js";

export default function initToastManager(){

    const container = document.createElement("div");
    container.className = "toast-container";

    document.body.appendChild(container);

    function createToast( message, type="success"){

        const toast = document.createElement("div");
        toast.className =  `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        requestAnimationFrame(()=>{
            toast.classList.add("show")
        })

        setTimeout(()=>{
            toast.classList.remove("show");
            setTimeout(()=> toast.remove(),300);
        }, 2500);
    }

    on("toast:success", e=>{
        createToast(e.detail.message, "success")
    })

    on("toast:error", e=>{
        createToast(e.detail.message, "error")
    })
}