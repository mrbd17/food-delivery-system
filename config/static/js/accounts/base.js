export function getCSRFToken() {
    
    const meta =  document.querySelector('meta[name="csrf-token"]')
    if(meta) {
       return meta.getAttribute("content");
    }
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.startsWith('csrftoken=')) {
                cookieValue = cookie.substring('csrftoken='.length);
                break;
            }
        }
    }

    return cookieValue;
}

window.getCSRFToken = getCSRFToken;
