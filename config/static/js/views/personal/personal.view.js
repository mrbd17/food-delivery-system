import renderMain from "./personal-main.js";
import renderChangeName from "./change-name.js"
import renderChangeEmail from "./change-email.js";
import renderChangePhone from "./change-phone.js";



export default function renderPersnoal(container, state, route){

    if (state.personal.loading){
            container.innerHTML = `
                <div class="personal-loading">
                    <div class="spinner"></div>
                </div>
            `;
            return;
    }

    if (state.personal.error){
        container.innerHTML = `<div class="error"> Something went wrong</div>`
        return;
    }
    console.log(route)
    switch(route.section){
        case "name":
            renderChangeName(container, state);
            console.log(route)
            break;
        case "email":
            renderChangeEmail(container, state);
            console.log(route)
            break;
        case "phone":
            renderChangePhone(container, state);
            break;

        default:
             renderMain(container, state)  
             console.log(route)


    }
}
