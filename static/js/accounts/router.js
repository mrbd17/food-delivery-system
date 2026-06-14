// router.js

document.addEventListener("DOMContentLoaded", () => {

    let currentCleanup = null;
    const content = document.getElementById("accountContent");

    if (!content) {
        console.error("accountContent not found");
        return;
    }



    const routes = {
        overview: () => import("../views/overview.js"),
        personal: () => import("../views/personal/personal.controller.js"),
        security: () => import("../views/security.js"),
        settings: () => import("../views/settings.js"),
        addresses: () => import("../views/addresses.js"),
        orders: () => import("../views/orders.js"),
    };

    

    function setActive(section) {

        const links = document.querySelectorAll(".menu-link");
        const indicator = document.querySelector(".active-indicator");

        console.log("Active section:", section);
        console.log("Links found:", links.length);

        let activeLink = null;

        links.forEach(link => {

            link.classList.remove("active");

            if (link.dataset.section === section) {
                link.classList.add("active");
                activeLink = link;
            }
        });

        if (!activeLink || !indicator) return;

        // حساب مكان العنصر
        const menuTop = activeLink.offsetTop;
        const height = activeLink.offsetHeight;

        // تحريك الخط
        indicator.style.top = menuTop + "px";
        indicator.style.height = height + "px";
    }

    const focusRoutes = [
        "personal/name",   
        "personal/email",
        "personal/phone",
    ]

    function setLayout(path){
        const isFocus = focusRoutes.some(r => path.startsWith(r));

        document.body.classList.toggle("focus-layout", isFocus)
    }

    async function navigateTo(){

        if(currentCleanup){
            currentCleanup();
            currentCleanup = null;
        }

        const path = location.hash.replace("#/", "") || "overview";
        setLayout(path);

        const mainSection = path.split("/")[0];
        

        if(!routes[mainSection]){
            content.innerHTML =   "<h2>404 - Page Not Found</h2>";
            return;
        }

        content.innerHTML = `<div class="loading">Loading...</div>`

        try {
            const module = await routes[mainSection]();


            if(!module.default){
                throw new Error("No default export in module")
            }
            
            currentCleanup =  module.default(content)

            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    setActive(mainSection);
            });
        });

        } catch(err){
            console.log("Router Error:", err);
            content.innerHTML = "<p>Something went wrong</p>";
        }
    }

    document.addEventListener("click", (e) => {

        const link = e.target.closest(".menu-link");
        
        if (!link) return;


        e.preventDefault();

        const section = link.dataset.section;

        location.hash = `/${section}`;;

        navigateTo();
    });


    // Back / Forward
    window.addEventListener("popstate", navigateTo);


    navigateTo();

});
