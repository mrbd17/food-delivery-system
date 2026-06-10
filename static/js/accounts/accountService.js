import api from "./api.js";
import store from './store.js';

export async function loadOverview() {

    const current = store.get("overview");

    if (current?.data){
        return current.data;
    }

    store.set("overview", {
        data:null,
        loading:true,
        error:null
    });

    try {
        const res = await api.get("/account/overview/");
        await new Promise(resolve => setTimeout(resolve, 1200));
        store.set("overview", {
        data:res.data,
        loading:false,
        error:null
        });
        console.log("store after set:", store.get("overview"));
        return res.data;

    } catch (err) {
        store.set("overview", {
            data: null,
            loading: false,
            error: err.message
        });

        throw err;
    }
}

// ==========================
// 2️⃣ Load Personal Info
// ==========================
export async function loadPersonal() {
    const current = store.get("personal");

    if (current?.data){
        return current.data;
    }

    store.set("personal", {
        data:null,
        loading:true,
        error:null
    });

    try {
        const res = await api.get("/account/personal/");
        await new Promise(resolve => setTimeout(resolve, 1200));
        
        store.set("personal", {
        data:res.data,
        loading:false,
        error:null
        });
        console.log("store after set:", store.get("personal"));
        return res.data;

    } catch (err) {
        store.set("personal", {
            data: null,
            loading: false,
            error: err.message
        });

        throw err;
    }
}

export async function changeName(first_name, last_name){
    
    const res = await api.patch("/account/personal/change-name/",{
        first_name,
        last_name,
    });

    const overview = store.get("overview");

    if(overview?.data?.user){
        store.set("overview", {
            ...overview,
                data: {
                ...overview.data,
                    user: { 
                        ...overview.data.user,
                        first_name,
                        last_name,
                    }
                }
        });

    }

    const personal = store.get("personal");

    if (personal?.data) {
        store.set("personal", {
            ...personal,
            data:{
                ...personal.data,
                data: {
                    ...personal.data.data,
                    first_name,
                    last_name,
                }  
            }
        })
    }

    return res.data;
}

export async function changePhone(phone){

    const res = await api.patch("/account/personal/change-phone/",{
        phone
    });

    const overview = store.get("overview");

    if (overview?.data?.user){
        store.set("overview", {
            ...overview,
            data: {
                ...overview.data,
                user: {
                    ...overview.data.user,
                    phone
                }
            }
        });
    }

    const personal = store.get("personal")

    if(personal?.data){
        store.set("personal", {
            ...personal,
            data: {
                ...personal.data,
                phone
            }
        });
    }

    return res.data;
}

export async function changeEmail(email) {

    const res = await api.patch("/account/personal/change-email/", {
        email
    });

    const overview = store.get("overview");

    if (overview?.data?.user) {
        store.set("overview", {
            ...overview,
            data: {
                ...overview.data,
                user: {
                    ...overview.data.user,
                    email
                }
            }
        })
    }

    const personal = store.get("personal");

    if (personal?.data) {
        store.set("personal", {
            ...personal,
            data: {
                ...personal.data,
                    email
            }
        });
    }

    return res.data;
}

export async function changeAvatar(file){

    const formData = new FormData();
    formData.append("avatar", file);

    const res = await api.post(
        "/account/personal/change-avatar/",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data"
            }
        }
    );

    const avatarUrl = res.data.data.avatar + "?t=" + Date.now();

    // Update overview
    const overview = store.get("overview");

    if (overview?.data?.user) {

        store.set("overview", {
            ...overview,
            data: {
                ...overview.data,
                user: {
                    ...overview.data.user,
                    avatar: avatarUrl
                }
            }
        });
    }

    // Update personal
    const personal = store.get("personal");

    if (personal?.data?.data) {

        const newPersonal = {
            ...personal,
            data: {
                ...personal.data,
                data: {
                    ...personal.data.data,
                    avatar: avatarUrl
                }
            }
        };

        store.set("personal", newPersonal);
    }

} // ✅ دي اللي كانت ناقصة



export async function changePasswrod(current_password, new_password){

    const res = await api.post(
        "/account/personal/change-password/",
        {
            current_password,
            new_password
        }
    );

    return res.data;
}