import store from "../../accounts/store.js";
import { changeName } from "../../accounts/accountService.js";
import { emit } from "../../core/events.js";

export default function renderChangeName(container){

    const personal = store.get("personal");
    const user = personal?.data?.data;

    let original = {
        first_name: user.first_name,
        last_name: user.last_name
    };

    container.innerHTML = `
        <div class="name-page">

            <h1 class="page-title">Name</h1>

            <p class="page-desc">
                This is the name you would like other people to use when referring to you.
            </p>

            <form id="nameForm" class="name-form">

                <!-- First Name -->
                <div class="field">

                    <label>First name</label>

                    <div class="input-box">

                        <input
                            id="first"
                            type="text"
                            value="${user.first_name}"
                            autocomplete="given-name"
                        />

                        <span class="clear" id="clearFirst">
                            <svg viewBox="0 0 24 24" class="clear-icon">
                                <path d="M12 1C5.9 1 1 5.9 1 12s4.9 11 11 11 11-4.9 11-11S18.1 1 12 1Zm6 15-2 2-4-4-4 4-2-2 4-4-4-4 2-2 4 4 4-4 2 2-4 4 4 4Z"/>
                            </svg>
                        </span>

                    </div>

                </div>


                <!-- Last Name -->
                <div class="field">

                    <label>Last name</label>

                    <div class="input-box">

                        <input
                            id="last"
                            type="text"
                            value="${user.last_name}"
                            autocomplete="family-name"
                        />

                        <span class="clear" id="clearLast">
                            <svg viewBox="0 0 24 24" class="clear-icon">
                                <path d="M12 1C5.9 1 1 5.9 1 12s4.9 11 11 11 11-4.9 11-11S18.1 1 12 1Zm6 15-2 2-4-4-4 4-2-2 4-4-4-4 2-2 4 4 4-4 2 2-4 4 4 4Z"/>
                            </svg>
                        </span>

                    </div>

                </div>


                <!-- Button -->
                <button id="updateBtn" class="update-btn" disabled>
                    Update
                </button>

            </form>

        </div>
    `;



    const firstInput = container.querySelector("#first");
    const lastInput = container.querySelector("#last");

    const clearFirst = container.querySelector("#clearFirst");
    const clearLast = container.querySelector("#clearLast");

    const btn = container.querySelector("#updateBtn");
    const form = container.querySelector("#nameForm");


    function toggleClear(){

        clearFirst.style.display =
            firstInput.value ? "flex" : "none";

        clearLast.style.display =
            lastInput.value ? "flex" : "none";
    }


    function checkValid(){

        const first = firstInput.value.trim();
        const last = lastInput.value.trim();

        const invalid = first === "" || last === "";

        btn.disabled = invalid;

        toggleClear();
    }

    firstInput.addEventListener("input", checkValid);
    lastInput.addEventListener("input", checkValid);


    clearFirst.addEventListener("click", () => {
        firstInput.value = "";
        checkValid();
        firstInput.focus();
    });


    clearLast.addEventListener("click", () => {
        lastInput.value = "";
        checkValid();
        lastInput.focus();
    });


    async function submit(e){

        e.preventDefault();

        const first = firstInput.value.trim();
        const last = lastInput.value.trim();

        const prev = store.get("personal").data;


        // Optimistic Update
        store.set("personal", {
            ...store.get("personal"),
            data: {
                ...prev,
                first_name: first,
                last_name: last
            }
        });


        emit("loading:start");


        try{

            await changeName(first, last);

            original = {
                first_name: first,
                last_name: last
            };

            emit("toast:success", {
                message: "Name updated successfully"
            });

        }catch{

            
            store.set("personal", {
                ...store.get("personal"),
                data: prev
            });

            emit("toast:error", {
                message: "Update failed"
            });

        }finally{

            emit("loading:end");

            checkValid();
        }
    }


    form.addEventListener("submit", submit);

    checkValid();


    return () => {
        form.removeEventListener("submit", submit);
    };
}