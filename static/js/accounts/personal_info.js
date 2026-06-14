window.initPersonalInfo = function () {
    container = document.getElementById("accountContent");
    if(!container) return;

    function render() {
        const state = window.accountStore.getState();
        const user = state.user;

        const img = container.querySelector("#profilePhoto");
        const nameField = container.querySelector('[data-field="name"]');
        const emailField = container.querySelector('[data-field="email"]');
        const phoneField = container.querySelector('[data-field="phone"]');
        const passwordField = container.querySelector('[data-field="password"]');


        if (img && user.avatar) img.src = user.avatar;
        if (nameField) nameField.textContent = user.name ?? "-";
        if (emailField) emailField.textContent = user.email ?? "-";
        if (phoneField) phoneField.textContent = user.phone ?? "-";
        if (passwordField) passwordField.textContent = user.password ?? "-";
    }

    if (window._personalInfounsub){
        window._personalInfounsub();
    }

    const unsubscribe = window.accountStore.subscribe(render);
    window._personalInfounsub = unsubscribe;

    render();

        // ================= Helpers =================
    function openPhotoModal() {
        const modal = container.querySelector("#photoModal");
        const overlay = container.querySelector("#photoOverlay");
        if (!modal || !overlay) return;
        modal.classList.add("open");
        overlay.classList.add("open");
    }

    function closePhotoModal() {
        const modal = container.querySelector("#photoModal");
        const overlay = container.querySelector("#photoOverlay");
        if (!modal || !overlay) return;
        modal.classList.remove("open");
        overlay.classList.remove("open");
    }

    async function uploadPhoto(file) {
        const formData = new FormData();
        formData.append("photo", file);

        try {
            const res = await fetch("/account/upload-photo/", {
                method: "POST",
                body: formData,
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.error || "Upload failed");

            // حدّث الـ GS
            const prev = window.accountStore.getState().user;
            window.accountStore.setUser({ ...prev, avatar: data.url });

            closePhotoModal();

        } catch (err) {
            console.error(err);
        }
    }

    // ================= Event Delegation =================
    container.addEventListener("click", (e) => {

        // فتح المودال
        if (e.target.id === "profilePhoto" || e.target.classList.contains("photo-edit-icon")) {
            e.preventDefault();
            openPhotoModal();
        }

        // إغلاق المودال
        if (e.target.id === "photoOverlay" || e.target.id === "cancelPhotoBtn") {
            e.preventDefault();
            closePhotoModal();
        }

        // زر اختيار الصورة
        if (e.target.id === "updatePhotoBtn") {
            e.preventDefault();
            const input = container.querySelector("#profilePhotoInput");
            if (input) input.click();
        }

        // الضغط على field (name, email, phone, password)
        const field = e.target.closest(".profile-field.clickable");
        if (field) {
            const target = field.dataset.target;

            switch (target) {
                case "name":
                    window.location.href = "/account/personal/name/";
                    break;
                case "email":
                    window.location.href = "/account/personal/email/";
                    break;
                case "phone":
                    window.location.href = "/account/personal/phone/";
                    break;
                case "password":
                    window.location.href = "/account/personal/password/";
                    break;
                default:
                    console.warn("Unknown field target:", target);
            }
        }
    });

    // ================= File Change (Delegation برضه) =================
    container.addEventListener("change", (e) => {
        if (e.target.id === "profilePhotoInput") {
            const file = e.target.files[0];
            if (!file) return;
            uploadPhoto(file);
        }
    }); 
}