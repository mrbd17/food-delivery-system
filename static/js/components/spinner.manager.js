import { on } from "../core/events.js";

export default function initSpinner(){

    const spinner = document.createElement("div");
    spinner.className = "global-spinner";
    spinner.innerHTML = `<div class="spinner"></div>`;

    spinner.style.display = "none";

    document.body.appendChild(spinner);

    let startTime = 0;
    const MIN_DURATION = 2000;

    on("loading:start", () => {
        startTime = Date.now();
        spinner.style.display = "flex";
    });

    on("loading:end", () => {

        const elapsed = Date.now() - startTime;
        const remaining = MIN_DURATION - elapsed;

        setTimeout(() => {
            spinner.style.display = "none";
        }, Math.max(0, remaining));
    });
}