
let allCountries = []

export async function loadCountries(){
    try {
       const res = await fetch("/api/v1/orders/countries/"); 
       if(!res.ok){
            throw new Error("Failed to fetch countries")   
       }

       allCountries = await res.json()
       renderCountries(allCountries);
       await autoDetectCountry()
    } catch(error){
        console.error("Error loading Countries", error)
    }
    
    
    
}

function renderCountries(list){
    const select = document.getElementById("country");
    if(!select) return;

    select.innerHTML = "<option>Loading....</option>";

    list.forEach(c => {
        const option = document.createElement("option");

        option.value = c.code;
        option.textContent = `${c.code} ${c.name}`;
        
        select.appendChild(option)

    });

}

async function autoDetectCountry(){
    try {
        const res = await fetch("/api/v1/orders/detect_country/");
        if(!res.ok) return;

        const data = await res.json();

        const select = document.getElementById("country");

        if (select && data.country_code) {
            select.value = data.country_code.toUpperCase();
        }

    } catch(err){
        console.error(err);
    }
}