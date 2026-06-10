import {CartAPI} from "./cartAPI.js"

export let cart = { items: [] }

function renderCart(){
    const container = document.getElementById("cartItems")
    const checkoutBtn = document.getElementById("checkoutBtn")

    if(!container) return

    if(!cart || !Array.isArray(cart.items) || cart.items.length === 0){
        container.innerHTML = "<p>Your cart is empty</p>"
        if(checkoutBtn){
            checkoutBtn.classList.add("disabled")
        }
        
        renderCartSummary()
        return
    } else {
        checkoutBtn.classList.remove("disabled")
    }
    
    container.innerHTML = cart.items.map(getItemHtml).join('')
    renderCartSummary()
    checkoutBtn.classList.remove("disabled")
}

function getElement(id) {
    return document.getElementById(id)
}

function getItemHtml(item) {
    const menuItem = item.menu_item || {}
    const name = menuItem.name || 'Product'
    const price = Number(menuItem.price || 0)
    const quantity = Number(item.quantity || 0)
    const subtotal = Number(item.subtotal ?? price * quantity)

    return `
    <div class="cart-item" data-item-id="${item.id}">
      <div class="cart-item-details">
        <span class="cart-item-name">${name}</span>
        <span class="cart-item-price">$${price.toFixed(2)} each</span>
      </div>
      <div class="cart-item-controls">
        <button type="button" class="cart-action-btn" data-action="decrease" data-item-id="${item.id}">-</button>
        <span class="cart-item-qty">${quantity}</span>
        <button type="button" class="cart-action-btn" data-action="increase" data-item-id="${item.id}">+</button>
        <button type="button" class="cart-action-btn remove-item" data-action="remove" data-item-id="${item.id}">Remove</button>
      </div>
      <div class="cart-item-subtotal">$${subtotal.toFixed(2)}</div>
    </div>`
}

const CART_TOTAL_ID = 'cartTotal'
const CART_COUNT_ID = 'cartCount'
const CART_SUMMARY_ID = 'cartSummary'

function renderCartSummary() {
    const count = cart.item_count ?? cart.items.reduce((sum, item) => sum + Number(item.quantity || 0), 0)
    const total = cart.subtotal ?? cart.items.reduce(
        (sum, item) => sum + Number((item.subtotal ?? ((item.menu_item?.price || 0) * item.quantity)) || 0),
        0
    )

    const summaryEl = getElement(CART_SUMMARY_ID)
    if (summaryEl) {
        summaryEl.innerHTML = `
        <div class="cart-summary">
          <span>Total items: ${count}</span>
          <span>Total: $${total.toFixed(2)}</span>
        </div>`
    }

    const totalEl = getElement(CART_TOTAL_ID)
    if (totalEl) {
        totalEl.innerText = `$${total.toFixed(2)}`
    }

    const countEl = getElement(CART_COUNT_ID)
    if (countEl) {
        countEl.innerText = count
    }
}

async function loadCart() {
    console.group('🛒 loadCart');

    try {
        const res = await CartAPI.get();

        console.log('📡 Raw Response:', res);

        // لو عندك access للـ status
        if (res?.status && res.status >= 400) {
            console.error('❌ Bad status:', res.status, res.statusText);
        }

        cart = res.data ?? res;

        console.log('✅ Cart loaded:', cart);

    } catch (error) {
        console.error('❌ Failed to load cart');

        // 🔍 أهم جزء: تحليل الـ error
        console.error('Message:', error.message);
        console.error('Stack:', error.stack);

        // لو Axios أو fetch wrapper
        if (error.response) {
            console.error('📡 Response Error:', {
                status: error.response.status,
                data: error.response.data,
                headers: error.response.headers
            });
        } else if (error.request) {
            console.error('📭 No response received:', error.request);
        } else {
            console.error('⚙️ Setup Error:', error);
        }

        cart = { items: [] };
    }

    console.log('🎯 Final cart state:', cart);
    console.groupEnd();

    renderCart();
}

async function changeQuantity(itemId, change) {
    const item = cart.items.find(i => String(i.id) === String(itemId))
    if (!item) return

    const quantity = item.quantity + change
    if (quantity < 1) {
        await removeItem(itemId)
        return
    }

    try {
        await CartAPI.updateItem(itemId, quantity)
        await loadCart()
    } catch (error) {
        console.error('Failed to update cart item', error)
    }
}

async function removeItem(itemId) {
    try {
        await CartAPI.removeItem(itemId)
        await loadCart()
    } catch (error) {
        console.error('Failed to remove cart item', error)
    }
}

export async function addItem(product_id){
    try {
        await CartAPI.addItem(product_id)
        await loadCart()
    } catch(error){
        console.error("failed to add product to cart", error)
        console.log(typeof error)
    }
}

function handleCartClick(event) {
    const button = event.target.closest('button[data-action]')
    if (!button) return

    const action = button.dataset.action
    const itemId = button.dataset.itemId
    if (!itemId) return

    if (action === 'increase') {
        changeQuantity(itemId, 1)
        return
    }

    if (action === 'decrease') {
        changeQuantity(itemId, -1)
        return
    }

    if (action === 'remove') {
        removeItem(itemId)
    }
}

export function initCartUI() {
    const container = getElement('cartItems')
    if (container) {
        container.addEventListener('click', handleCartClick)
    }
    loadCart()
}

export function toggleCart(){
    const cartEl = document.getElementById('cart');
    const cartBtn = document.querySelector('.cart-btn');
    
    if(!cartEl || !cartBtn) return;

    const isOpen = cartEl.classList.toggle('open');

    if(isOpen){
        document.addEventListener('click', closeOnOutside)
    } else {
        document.removeEventListener('click', closeOnOutside)
    };

    function closeOnOutside(e){
        if(!cartEl.contains(e.target) && !cartBtn.contains(e.target)){
            console.log(cartBtn)
            cartEl.classList.remove('open');
            document.removeEventListener('click', closeOnOutside)
        }
    }
}