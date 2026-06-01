import "../accounts/api.js";
import "../accounts/store.js";
import "../accounts/router.js";

import initToastManager from "../components/toast.manager.js";
import initSpinner from "../components/spinner.manager.js";

function bootstrapApp(){
    initToastManager();
    initSpinner();
}

document.addEventListener("DOMContentLoaded", bootstrapApp);