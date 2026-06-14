
import { CartAPI }    from "../cart/cartAPI.js";
import { OrderAPI }   from "../orders/orderAPI.js";
import { addressAPI } from "./address.js";
import { loadCountries } from "./country.js";
import { emit }       from "../core/events.js";

const cartItemsEl   = document.getElementById("cart-items");
const addressListEl = document.getElementById("list-addresses");
const placeOrderBtn = document.getElementById("place-order");
const addressModal  = document.getElementById("address-modal");
const modalForm     = document.getElementById("modal-form");
const modalError    = document.getElementById("modal-error");
const closeModalBtn = document.getElementById("close-modal");
const cancelBtn     = document.getElementById("cancel");
const addAddressBtn = document.getElementById("add-address-btn");

const state = {
  cart:            null,  
  addresses:       [],     
  selectedAddress: null,   
  paymentMethod:   "cash", 
  loading:         false,
};

function escapeHTML(value = "") {
  return String(value)
    .replaceAll("&",  "&amp;")
    .replaceAll("<",  "&lt;")
    .replaceAll(">",  "&gt;")
    .replaceAll('"',  "&quot;")
    .replaceAll("'",  "&#039;");
}

function fmt(price) {
  return new Intl.NumberFormat("en-US", {
    style:    "currency",
    currency: "USD",
  }).format(Number(price) || 0);
}

async function safeLoad(fn, errorMessage = "Something went wrong") {
  if (state.loading) return false;
  state.loading = true;
  try {
    emit("spinner:show");
    await fn();
    return true;
  } catch (err) {
    console.error("[checkout]", err);
    emit("toast:error", { message: errorMessage });
    return false;
  } finally {
    state.loading = false;
    emit("spinner:hide");
  }
}

function openModal() {
  addressModal.classList.remove("hidden");
  addressModal.setAttribute("aria-hidden", "false");
  document.body.classList.add("modal-open");
  const firstInput = modalForm.querySelector("input, select");
  firstInput?.focus();
}

function closeModal() {
  addressModal.classList.add("hidden");
  addressModal.setAttribute("aria-hidden", "true");
  document.body.classList.remove("modal-open");
  modalForm.reset();
  clearModalError();
}

function setModalError(msg) {
  modalError.textContent = msg; // textContent — XSS safe
  modalError.hidden = false;
}

function clearModalError() {
  modalError.textContent = "";
  modalError.hidden = true;
}

/** Lock / unlock the Place Order button based on state. */
function syncPlaceOrderBtn() {
  const canOrder = !!state.selectedAddress && !!state.cart?.items?.length;
  placeOrderBtn.disabled = !canOrder;
  placeOrderBtn.classList.toggle("btn--disabled", !canOrder);
}

/* ─────────────────────────────────────────────
   RENDERERS — pure DOM, no business logic
───────────────────────────────────────────── */

function renderCart() {
  const items = state.cart?.items ?? [];

  if (!items.length) {
    cartItemsEl.innerHTML = ""; // clear first (safe; no user data)
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.innerHTML = `
      <span class="empty-icon">🛒</span>
      <p>Your cart is empty</p>
      <a href="/" class="link-back">Continue shopping</a>
    `;
    cartItemsEl.appendChild(empty);
    syncPlaceOrderBtn();
    return;
  }

  // Build DOM nodes — never innerHTML with user data
  const fragment = document.createDocumentFragment();

  items.forEach(item => {
    const name     = escapeHTML(item.menu_item?.name  || "Item");
    const imgSrc   = item.menu_item?.img;
    const price    = fmt(item.price_snapshot ?? item.price ?? 0);
    const quantity = Number(item.quantity) || 1;

    const card = document.createElement("div");
    card.className = "cart-item-card";

    const thumb = document.createElement("div");
    thumb.className = "cart-item-thumb";
    if (imgSrc) {
      const img = document.createElement("img");
      img.src = imgSrc;          
      img.alt = name;
      img.loading = "lazy";
      thumb.appendChild(img);
    } else {
      thumb.textContent = "📦";
    }

    const details = document.createElement("div");
    details.className = "cart-item-details";
    details.innerHTML = `
      <span class="cart-item-name">${name}</span>
      <span class="cart-item-qty">Qty: ${quantity}</span>
    `;

    // Price
    const priceEl = document.createElement("div");
    priceEl.className = "cart-item-price";
    priceEl.textContent = price;

    card.append(thumb, details, priceEl);
    fragment.appendChild(card);
  });

  // Summary row
  const total = state.cart?.total ?? items.reduce(
    (sum, i) => sum + Number(i.price_snapshot ?? i.price ?? 0), 0
  );
  const summary = document.createElement("div");
  summary.className = "cart-summary";
  summary.innerHTML = `
    <span>Order Total:</span>
    <strong class="cart-total">${fmt(total)}</strong>
  `;
  fragment.appendChild(summary);

  cartItemsEl.innerHTML = "";
  cartItemsEl.appendChild(fragment);
  syncPlaceOrderBtn();
}

function renderAddresses() {
  if (!state.addresses.length) {
    addressListEl.innerHTML = "";
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.innerHTML = `
      <span class="empty-icon">📍</span>
      <p>No saved addresses yet</p>
    `;
    addressListEl.appendChild(empty);
    syncPlaceOrderBtn();
    return;
  }

  const fragment = document.createDocumentFragment();

  state.addresses.forEach(addr => {
    const isSelected = state.selectedAddress?.id === addr.id;

    const card = document.createElement("div");
    card.className = `address-card${isSelected ? " address-card--selected" : ""}`;

    const label = document.createElement("label");
    label.className = "address-label";

    const radio = document.createElement("input");
    radio.type    = "radio";
    radio.name    = "address";
    radio.value   = String(addr.id);
    radio.checked = isSelected;
    radio.className = "address-radio";

    const info = document.createElement("div");
    info.className = "address-info";

    const actions = document.createElement("div");
    actions.className = "address-actions";

    const deleteBtn = document.createElement("button");
    deleteBtn.type = "button";
    deleteBtn.className = 'delete-address-btn';
    deleteBtn.dataset.addressId = addr.id

    const icon = document.createElement("i");
    icon.className = "fa-solid fa-trash"


    const nameEl = document.createElement("strong");
    nameEl.className = "address-name";
    nameEl.textContent = addr.full_name || "";

    const badgeEl = document.createElement("span");
    badgeEl.className = `address-badge address-badge--${(addr.label || "other").toLowerCase()}`;
    badgeEl.textContent = addr.label || "";

    const lineEl = document.createElement("p");
    lineEl.className = "address-line";
    lineEl.textContent = [addr.street, addr.city, addr.state, addr.country]
      .filter(Boolean)
      .join(", ");

    const phoneEl = document.createElement("p");
    phoneEl.className = "address-phone";
    phoneEl.textContent = addr.phone ? `📞 ${addr.phone}` : "";


    if (isSelected) {
      const tick = document.createElement("span");
      tick.className = "address-selected-badge";
      tick.textContent = "✔ Delivering here";
      info.appendChild(tick);
    }

    info.append(nameEl, badgeEl, lineEl, phoneEl);
    deleteBtn.appendChild(icon)
    actions.appendChild(deleteBtn)
    label.append(radio, info);
    card.append(label, actions);
    fragment.appendChild(card);
  });

  addressListEl.innerHTML = "";
  addressListEl.appendChild(fragment);
  syncPlaceOrderBtn();
}

/* ─────────────────────────────────────────────
   API LOADERS
───────────────────────────────────────────── */

async function loadCart() {
  const data    = await CartAPI.get();
  state.cart    = data;
  renderCart();
}

async function loadAddresses() {
  const data       = await addressAPI.listAddresses();
  state.addresses  = Array.isArray(data) ? data : [];

  // Auto-select the default address if none selected yet
  if (!state.selectedAddress) {
    state.selectedAddress =
      state.addresses.find(a => a.is_default) ?? state.addresses[0] ?? null;
  }

  renderAddresses();
}

/* ─────────────────────────────────────────────
   EVENT HANDLERS
───────────────────────────────────────────── */

/** Address selection — event delegation on the container */
function onAddressChange(e) {
  if (e.target.type !== "radio" || e.target.name !== "address") return;

  state.selectedAddress =
    state.addresses.find(a => String(a.id) === e.target.value) ?? null;

  // Re-render to reflect selected styling without full DOM rebuild
  renderAddresses();
}

/** Place Order */
async function onPlaceOrder() {
  if (!state.selectedAddress) {
    emit("toast:error", { message: "Please select a delivery address." });
    return;
  }
  if (!state.cart?.items?.length) {
    emit("toast:error", { message: "Your cart is empty." });
    return;
  }

  placeOrderBtn.disabled = true;
  placeOrderBtn.textContent = "Placing order…";

  const ok = await safeLoad(async () => {
    const order = await OrderAPI.create(
      state.selectedAddress.id,
       state.paymentMethod
      );
    await loadCart();
    emit("toast:success", { message: "Order placed successfully 🎉" });
    window.location.href = `/api/v1/orders/${order.id}/tracking/`
  }, "Failed to place order. Please try again.");

  placeOrderBtn.textContent = "Place your order";
  if (!ok) placeOrderBtn.disabled = false;
  else syncPlaceOrderBtn();
}

async function onDeleteAddress(e){
  const deleteBtn = e.target.closest(".delete-address-btn");
  if(!deleteBtn) return;
  e.preventDefault()
  const id = deleteBtn.dataset.addressId;

  try {
    await addressAPI.deleteAddress(id);
    state.addresses = state.addresses.filter(
      addr => String(addr.id) !== String(id)
      
    );
    emit("toast:success", {message: "Address Deleted Successfully"})

    if(state.selectedAddress?.id == id){
      state.selectedAddress = null;
    }

    renderAddresses()

  } catch(err){
    emit("toast:error", {message: err.message})
  }

}
/** Address form submit */
async function onAddressSubmit(e) {
  e.preventDefault();
  clearModalError();

  const formData = new FormData(modalForm);
  const data     = Object.fromEntries(formData.entries());
  data.is_default = document.getElementById("is_default").checked;

  const saveBtn = modalForm.querySelector("#save");
  if (saveBtn) { saveBtn.disabled = true; saveBtn.textContent = "Saving…"; }

  const ok = await safeLoad(async () => {
    await addressAPI.createAddress(data);
    state.addresses = await addressAPI.listAddresses();
    renderAddresses();
    closeModal();
    emit("toast:success", { message: "Address saved ✅" });
  }, "Failed to save address.");

  if (saveBtn) {
    saveBtn.disabled = false;
    saveBtn.textContent = "Save Address";
  }
  if (!ok) setModalError("Could not save address. Please check your details.");
}

/** Close modal on backdrop click */
function onModalBackdropClick(e) {
  if (e.target === addressModal) closeModal();
}

/** Close modal on Escape key */
function onKeyDown(e) {
  if (e.key === "Escape" && !addressModal.classList.contains("hidden")) {
    closeModal();
  }
}

function bindEvents() {
  addressListEl.addEventListener("change", onAddressChange);
  addressListEl.addEventListener("click", onDeleteAddress);
  placeOrderBtn.addEventListener("click", onPlaceOrder);
  modalForm.addEventListener("submit", onAddressSubmit);
  closeModalBtn?.addEventListener("click", closeModal);
  cancelBtn?.addEventListener("click", closeModal);
  addressModal?.addEventListener("click", onModalBackdropClick);
  document.addEventListener("keydown", onKeyDown);

  // ✅ Inject the "Add new address" button after the address list
  injectAddAddressBtn();
}

function injectAddAddressBtn() {
  // Guard: don't inject twice
  if (document.getElementById("add-address-btn")) return;

  const btn = document.createElement("button");
  btn.id        = "add-address-btn";
  btn.className = "btn-add-address";
  btn.innerHTML = `<span>+</span> Add a new address`;

  // Insert it right after #list-addresses in the DOM
  addressListEl.insertAdjacentElement("afterend", btn);

  btn.addEventListener("click", openModal);
}

/* ─────────────────────────────────────────────
   INIT
───────────────────────────────────────────── */
(async function init() {
  bindEvents();
  loadCountries(); 

  await safeLoad(async () => {
    await Promise.all([loadCart(), loadAddresses()]);
  }, "Failed to load checkout. Please refresh the page.");
})();