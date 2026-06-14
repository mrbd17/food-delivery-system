export function matchPersonalRoute(){

    const path = location.hash.replace("#/personal", "");

    const section = path.replace("/", "");

    return {
        section: section || "main"
    };

}
