// views/personal/components/avatarOverlay.js

export default function openAvatarOverlay(onUpdate){

    const overlay = document.createElement("div");
    overlay.className = "avatar-overlay";

    overlay.innerHTML = `
        <div class="avatar-card">

            <h3>Update profile photo</h3>

            <p class="avatar-subtitle">
                This is the photo you would like others to see.
            </p>

            <div class="avatar-preview">
                <img />
            </div>

            <input type="file" accept="image/*" hidden />

            <div class="avatar-actions">
                <button class="upload-btn">Upload photo</button>
                <button class="cancel-btn">Cancel</button>
            </div>

        </div>
    `;

    document.body.appendChild(overlay);

    const fileInput  = overlay.querySelector("input");
    const uploadBtn  = overlay.querySelector(".upload-btn");
    const cancelBtn  = overlay.querySelector(".cancel-btn");
    const previewImg = overlay.querySelector(".avatar-preview img");

    /* ======================
       CLOSE
    ====================== */

    function close(){
        overlay.remove();
        document.removeEventListener("keydown", escHandler);
    }

    function escHandler(e){
        if(e.key === "Escape") close();
    }

    /* ======================
       EVENTS
    ====================== */

    uploadBtn.addEventListener("click", ()=>{
        fileInput.click();
    });

    fileInput.addEventListener("change", async ()=>{

        const file = fileInput.files[0];

        if(file){
            previewImg.src = URL.createObjectURL(file);

            if(onUpdate){
                await onUpdate(file);
            }
        }

        close();
    });

    cancelBtn.addEventListener("click", close);

    overlay.addEventListener("click",(e)=>{
        if(e.target === overlay){
            close();
        }
    });

    document.addEventListener("keydown", escHandler);

    return close;
}