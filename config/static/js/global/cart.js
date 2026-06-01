/* =======================
   Cart Model (Data)
======================= */

let cart = JSON.parse(localStorage.getItem("cart")) || {};


/* =======================
   Storage
======================= */

function saveCart() {
  localStorage.setItem("cart", JSON.stringify(cart));
}


/* =======================
   Cart Logic (Controller)
======================= */

export function addToCart(item) {
  const id = item.id

  cart[id] = cart[id]
    ? { ...cart[id], qty:cart[id].qty + 1}
    : { ...item, qty:1};
    
  updateUI();
}

export function changeQty(id, change) {
  if (!cart[id]) return;

  cart[id].qty += change

  if (cart[id].qty <= 0) {
    delete cart[id];
  }

  updateUI()
}

/* =======================
   Calculations
======================= */

function getCartCount() {
  let count = 0;
  for (let id in cart) {
    count += cart[id].qty
  }
  return count;
}

function getCartTotal() {
  let total = 0;
  for (let id in cart) {
    total += cart[id].price * cart[id].qty
  }
  return total;
}


/* =======================
   UI (View)
======================= */

function renderCartItems() {
  const cartItemEl = document.getElementById("cartItems");
  if(!cartItemEl) return;

  let html = "";

  for (let id in cart) {
    const item = cart[id];
    html += `
    <div class="cart-item">
      <span class="item-name">${item.name}</span>
      <span class="item-total">$${(item.price * item.qty).toFixed(2)}</span>
      <div class="qty-buttons">
        <button class="minus-btn" data-id="${id}">-</button>
        <span class="item-qty">${item.qty}</span>
        <button class="plus-btn" data-id="${id}">+</button>
      </div>
    </div>
   `;

  }
  cartItemEl.innerHTML = html;
}

function renderCartCount() {
  const cartCountEl = document.getElementById("cartCount");
  if (cartCountEl) {
    cartCountEl.innerText = getCartCount();
  }
}

function renderCartTotal() {
  const totalEl = document.getElementById("total");
  if (totalEl) {
    totalEl.innerText = getCartTotal().toFixed(2);
  }
}


/* =======================
   UI Update Handler
======================= */

function updateUI() {
  saveCart();
  renderCartItems();
  renderCartCount();
  renderCartTotal();
}


/* =======================
   Events
======================= */

export function initCartEvents() {
  const cartItemsEl = document.getElementById("cartItems");
  if (!cartItemsEl) return;

  cartItemsEl.addEventListener("click", (e) => {
    if (e.target.classList.contains("plus-btn")) {
      changeQty(e.target.dataset.id, 1);
    }

    if (e.target.classList.contains("minus-btn")) {
      changeQty(e.target.dataset.id, -1);
    }
  });
}


/* =======================
   Cart Toggle
======================= */

export function toggleCart() {
  const cartEl = document.getElementById("cart");
  const cartBtn = document.querySelector(".cart-btn")
  if (!cartEl || !cartBtn) return; 

  const isOpen = cartEl.classList.toggle("open");

  if (isOpen) {
    document.addEventListener("click", closeOnOutside);
  } else {
    document.removeEventListener("click", closeOnOutside);
  }

  function closeOnOutside(e) {
    if(!cartEl.contains(e.target) && !cartBtn.contains(e.target)) {
      cartEl.classList.remove("open");
      document.removeEventListener("click" , closeOnOutside);

    }
  }
}

const cartEl = document.getElementById("cart");
if(cartEl) {
  cartEl.addEventListener("click", e => e.stopPropagation());
}


/* =======================
   Init On Load
======================= */

export function initCart() {
  renderCartItems();
  renderCartCount();
  renderCartTotal();
}
