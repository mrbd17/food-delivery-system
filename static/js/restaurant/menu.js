import { addItem , initCartUI}  from '../cart/cartUI.js';
let menu = [];

initCartUI()

fetch('/api/menu/')
  .then(res =>res.json())
  .then(data => {
    menu = data;
    loadMenu(menu);
   
    });



const buttons = document.querySelectorAll(".category-btn")
buttons.forEach(btn =>{
  btn.addEventListener("click", () => {
    const category = btn.dataset.category;

    buttons.forEach(b => b.classList.remove("active"))
    btn.classList.add("active")

    if(category === "all") {
      loadMenu(menu)
    } else {
      loadMenu(menu.filter(item  => item.category === category))
    }
  });
});



function loadMenu(items){
 const menuDiv = document.getElementById("menu");
 let html = "";

 items.forEach(item=>{
   html += `
    <div class="food">
      <img src="${item.img}">
      <div>
       <h3>${item.name}</h3>
       <p>$${item.price}</p>
       <button class="add-btn" data-id="${item.id}">Add</button>
      </div>
    </div>
   `;
 });

 menuDiv.innerHTML = html; 
 
 document.querySelectorAll(".add-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const id = btn.dataset.id;
    addItem(id)

   }); 
 });
}



  


