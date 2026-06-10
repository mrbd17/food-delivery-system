import store from "../../accounts/store.js";
import * as service from "../../accounts/accountService.js";

import renderPersonal from "./personal.view.js";
import { matchPersonalRoute} from "./personal.routes.js";

export default function personalEntry(content){

    let unsubscribe = null;

    function render(){
        const state = store.state;
        const route =  matchPersonalRoute();
        renderPersonal(content, state, route);
    }

    async function init(){

        if(!store.state.personal){
            await service.loadPersonal();
        }

        render();
        
    }

    unsubscribe  = store.subscribe(render);

    window.addEventListener("popstate", render);

    init();
    
    return function cleanup(){
        unsubscribe();
        window.removeEventListener("popstate", render);
        content.innerHTML = "";
    };

}