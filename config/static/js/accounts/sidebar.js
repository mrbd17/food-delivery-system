// ====== sidebar.js ======
(() => {

    if(window.sidebarInitialized) return;
    window.sidebarInitialized = true;

    document.addEventListener("DOMContentLoaded", () => {

        const menuLinks = document.querySelectorAll(".menu-link");
        const content = document.getElementById("accountContent");

        if (!menuLinks.length || !content) return;

    async function reInit() {

        const page = content.querySelector("[data-js]");
        if(!page) return;

        const css  = page.dataset.css;
        const js   = page.dataset.js;
        const init = page.dataset.init;

        /* ===== CSS ===== */

        document
            .querySelectorAll("link[data-dynamic-css]")
            .forEach(l => l.remove());

        if(css){

            const link = document.createElement("link");

            link.rel = "stylesheet";
            link.href = `/static/css/accounts/${css}.css`;
            link.dataset.dynamicCss = "true";

            document.head.appendChild(link);
        }

        /* ===== JS ===== */

        if(js){

            const exists = document.querySelector(
                `script[data-dynamic-js="${js}"]`
            );

            if(!exists){
                 await new Promise((resolve, reject) => {
                    const script = document.createElement("script");
                    script.src = `/static/js/accounts/${js}`;
                    script.dataset.dynamicJs = js;

                    script.onload = resolve;
                    script.onerror = reject;

                    document.body.appendChild(script);
                 })
            }
        }

        /* ===== INIT ===== */

            if(init && window[init]){
                 window[init]();
            }
    }



        // ====== Helper: تحميل المحتوى بدون Reload ======\
        let isLoading = false;
        async function loadSection(section) {

            if(isLoading) return;
            isLoading  = true;

            try {
                const res = await fetch(`/account/${section}/partial/`);

                if(!res.ok){
                    throw new Error(`HTTP ${res.status}`);
    
                }

                const html = await res.text();

                if(!html.trim()){
                    throw new Error("Empty response");
                }

                content.innerHTML = html;
                    await reInit();
                     
                    

            } catch(err){
                content.innerHTML =
                    `<p style="color:red;">Failed to load ${section}</p>`;

                console.error(err);
            } finally {
                isLoading = false;
            }
        }

        function loadSectionCSS() {

            document
                .querySelectorAll("link[data-dynamic-css]")
                .forEach(l => l.remove());
            
            const el = content.querySelector("[data-css]");
            if(!el) return;

            const cssName = el.dataset.css;
            if(!cssName) return;

            const link = document.createElement("link");
            link.rel = "stylesheet";
            link.href =  `/static/css/accounts/${cssName}.css`;
            link.dataset.dynamicCss = "true";

            document.head.appendChild(link);
        }

        // ====== تحديد أول Section ======
        let initialSection = document.body.dataset.section;

        // لو overview محذوف
        if (!initialSection) {
            initialSection = menuLinks[0].dataset.section;
        }

        history.replaceState(
            { section: initialSection },
            "",
            window.location.pathname
        );

        loadSection(initialSection);

        // ====== تفعيل الـ active ======
        menuLinks.forEach(link => {
            if (link.dataset.section === initialSection) {
                link.classList.add("active");
            }
        });

        // ====== Click على Sidebar ======
        menuLinks.forEach(link => {
            if(link.dataset.listenerAttached) return;
            link.dataset.listenerAttached = "true";


            link.addEventListener("click", e => {
                e.preventDefault();

                const section = link.dataset.section;
                const url = link.getAttribute("href");

                history.pushState(
                    { section },
                    "",
                    url
                );

                loadSection(section);

                menuLinks.forEach(l => l.classList.remove("active"));
                link.classList.add("active");
            });
        });

        // ====== Back / Forward ======
        window.addEventListener("popstate", e => {
            if (e.state?.section) {
                const section = e.state.section;

                menuLinks.forEach(l => l.classList.remove("active"));
                menuLinks.forEach(link => {
                    if (link.dataset.section === section) {
                        link.classList.add("active");
                    }
                });

                loadSection(section);
            }
        });

    });

})();
