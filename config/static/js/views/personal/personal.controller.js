import store from "../../accounts/store.js";
import * as service from "../../accounts/accountService.js";

import renderPersonal from "../personal/personal.view.js";
import {matchPersonalRoute} from "../personal/personal.routes.js";

export default function personalEntry(content){

    let  unsubscribe = null

    function render(){

        const state = {
            personal: store.get("personal")
        }

        const route = matchPersonalRoute();

        renderPersonal(content, state, route);
    }


    async function init() {

        const personal = store.get("personal")

        if(!personal.data && !personal.loading){
            await service.loadPersonal();

        }

        render();
    }

    unsubscribe = store.subscribe(render);

    window.addEventListener("popstate", render);

    init()

    return function cleanup(){
        unsubscribe();
        window.removeEventListener("popstate", render);
        content.innerHTML = "";
    }
}
