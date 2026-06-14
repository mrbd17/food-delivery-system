import {CartAPI} from '../cart/cartAPI.js';
import {addressAPI} from "../checkout/address.js";
import {OrderAPI} from "../orders/orderAPI.js"
import {loadCountries} from "../checkout/country.js"
const state = {
  cart:            null,   
  addresses:       [],     
  selectedAddress: null,   
  paymentMethod:   'card', 
  step:            1,      
};

// ─── DOM REFS ─────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

const els = {
  // Address
  sectionAddress:        $('section-address'),
  addressLoading:        $('address-loading'),
  addressList:           $('address-list'),
  addAddressToggle:      $('add-address-toggle'),
  addAddressForm:        $('add-address-form'),
  btnShowAddForm:        $('btn-show-add-form'),
  btnCancelAddForm:      $('btn-cancel-add-form'),
  addressFormError:      $('address-form-error'),
  addressConfirmFooter:  $('address-confirm-footer'),
  btnConfirmAddress:     $('btn-confirm-address'),
  selectedAddressPreview:$('selected-address-preview'),
  btnChangeAddress:      $('btn-change-address'),

  // Payment
  sectionPayment:        $('section-payment'),
  paymentBody:           $('payment-body'),
  selectedPaymentPreview:$('selected-payment-preview'),
  btnChangePayment:      $('btn-change-payment'),
  btnConfirmPayment:     $('btn-confirm-payment'),
  optCard:               $('opt-card'),
  optCod:                $('opt-cod'),

  // Review & Place Order
  sectionReview:         $('section-review'),
  reviewItems:           $('review-items'),
  btnPlaceOrder:         $('btn-place-order'),
  btnPlaceOrderSidebar:  $('btn-place-order-sidebar'),
  placeOrderError:       $('place-order-error'),

  // Summary
  summaryLoading:        $('summary-loading'),
  summaryContent:        $('summary-content'),
  summaryCount:          $('summary-count'),
  summarySubtotal:       $('summary-subtotal'),
  summaryTax:            $('summary-tax'),
  summaryTotal:          $('summary-total'),

  // Cart preview
  cartPreview:           $('cart-preview'),
  cartPreviewItems:      $('cart-preview-items'),

  // Toast
  toast:                 $('toast'),
};

// ─── INIT ─────────────────────────────────────────────────────────────────────
(async function init() {
  await Promise.all([loadCart(), loadAddresses(), loadCountries()]);
  bindEvents();
})();

// ─── LOAD CART ────────────────────────────────────────────────────────────────
async function loadCart() {
  try {
    const data = await CartAPI.get();
    state.cart = data;
    renderOrderSummary(data);
    renderCartPreview(data);
  } catch (err) {
    els.summaryLoading.textContent = 'Could not load cart.';
    console.error(err);
  }
}

function renderOrderSummary(cart) {
  const items    = cart.items || [];
  const subtotal = parseFloat(cart.subtotal || 0);
  const tax      = subtotal * 0.08;
  const total    = subtotal + tax;
  const count    = items.reduce((sum, i) => sum + (i.quantity || 1), 0);

  els.summaryCount.textContent    = count;
  els.summarySubtotal.textContent = fmt(subtotal);
  els.summaryTax.textContent      = fmt(tax);
  els.summaryTotal.textContent    = fmt(total);

  els.summaryLoading.classList.add('hidden');
  els.summaryContent.classList.remove('hidden');
}

function renderCartPreview(cart) {
  const items = cart.items || [];
  if (!items.length) return;

  els.cartPreviewItems.innerHTML = items.map(item => `
    <div class="cart-preview-item">
      <div class="cart-preview-thumb">
        ${item.image
          ? `<img src="${item.image}" alt="${item.name || ''}" />`
          : '📦'}
      </div>
      <div class="cart-preview-info">
        <div class="cart-preview-name">${item.name || item.menu_item?.name || 'Item'}</div>
        <div class="cart-preview-qty">Qty: ${item.quantity}</div>
      </div>
      <div class="cart-preview-price">${fmt(item.price_snapshot || item.price || 0)}</div>
    </div>
  `).join('');

  els.cartPreview.classList.remove('hidden');
}

// ─── LOAD ADDRESSES ───────────────────────────────────────────────────────────
async function loadAddresses() {
  try {
    const data     = await addressAPI.listAddresses();
    state.addresses = Array.isArray(data) ? data : (data.results || []);
    renderAddressList();
  } catch (err) {
    els.addressLoading.textContent = 'Could not load addresses.';
    console.error(err);
  }
}

function renderAddressList() {
  els.addressLoading.classList.add('hidden');

  if (!state.addresses.length) {
    els.addressList.classList.add('hidden');
    els.addressConfirmFooter.classList.add('hidden');
    return;
  }

  els.addressList.innerHTML = state.addresses.map((addr, idx) => `
    <div class="address-card ${idx === 0 ? 'selected' : ''}"
         data-id="${addr.id}" role="button" tabindex="0">
      <input type="radio" name="address" value="${addr.id}"
             ${idx === 0 ? 'checked' : ''} />
      <div class="address-info">
        <strong>${addr.full_name || addr.name || 'Address'}</strong>
        <p>${addr.street_address || addr.address_line1 || ''}</p>
        ${addr.apartment ? `<p>${addr.apartment}</p>` : ''}
        <p>${[addr.city, addr.state, addr.postal_code].filter(Boolean).join(', ')}</p>
        <p>${addr.country || ''}</p>
        ${addr.phone ? `<p>📞 ${addr.phone}</p>` : ''}
        <div class="address-card-actions">
          <button class="address-action-btn delete" data-delete="${addr.id}">Remove</button>
        </div>
      </div>
    </div>
  `).join('');

  els.addressList.classList.remove('hidden');
  els.addressConfirmFooter.classList.remove('hidden');

  // Pre-select first address
  if (state.addresses.length) selectAddress(state.addresses[0]);

  // Card click → select
  els.addressList.querySelectorAll('.address-card').forEach(card => {
    card.addEventListener('click', e => {
      if (e.target.closest('.address-action-btn')) return;
      const id   = parseInt(card.dataset.id, 10);
      const addr = state.addresses.find(a => a.id === id);
      if (addr) {
        selectAddress(addr);
        els.addressList.querySelectorAll('.address-card').forEach(c =>
          c.classList.toggle('selected', c.dataset.id == addr.id)
        );
        els.addressList.querySelectorAll('input[type=radio]').forEach(r =>
          r.checked = r.value == addr.id
        );
      }
    });
  });

  // Delete buttons
  els.addressList.querySelectorAll('[data-delete]').forEach(btn => {
    btn.addEventListener('click', async e => {
      e.stopPropagation();
      const id = btn.dataset.delete;
      await handleDeleteAddress(id);
    });
  });
}

function selectAddress(addr) {
  state.selectedAddress = addr;
}
// ─── BIND EVENTS ──────────────────────────────────────────────────────────────
function bindEvents() {

  // Show add-address form
  els.btnShowAddForm.addEventListener('click', () => {
    els.addAddressForm.classList.remove('hidden');
    els.addAddressToggle.classList.add('hidden');
    els.addressConfirmFooter.classList.add('hidden');
  });

  // Cancel add-address form
  els.btnCancelAddForm.addEventListener('click', () => {
    els.addAddressForm.classList.add('hidden');
    els.addAddressToggle.classList.remove('hidden');
    if (state.addresses.length) els.addressConfirmFooter.classList.remove('hidden');
  });

  // Submit new address
  els.addAddressForm.addEventListener('submit', handleAddAddress);

  // Confirm address → go to step 2
  els.btnConfirmAddress.addEventListener('click', () => {
    if (!state.selectedAddress) {
      showToast('Please select a delivery address.', 'error');
      return;
    }
    lockStep(1);
    unlockStep(2);
  });

  // Change address
  els.btnChangeAddress.addEventListener('click', () => {
    unlockStep(1);
    lockStep(2);
    lockStep(3);
  });

  // Payment radio highlight
  document.querySelectorAll('input[name="payment"]').forEach(radio => {
    radio.addEventListener('change', () => {
      document.querySelectorAll('.payment-option').forEach(opt =>
        opt.classList.remove('selected')
      );
      radio.closest('.payment-option').classList.add('selected');
      state.paymentMethod = radio.value;
    });
  });

  // Confirm payment → go to step 3
  els.btnConfirmPayment.addEventListener('click', () => {
    lockStep(2);
    unlockStep(3);
    renderReviewItems();
  });

  // Change payment
  els.btnChangePayment.addEventListener('click', () => {
    unlockStep(2);
    lockStep(3);
  });

  // Place order (both buttons)
  [els.btnPlaceOrder, els.btnPlaceOrderSidebar].forEach(btn => {
    btn.addEventListener('click', handlePlaceOrder);
  });
}

// ─── STEP MANAGEMENT ─────────────────────────────────────────────────────────
function lockStep(step) {
  if (step === 1) {
    els.sectionAddress.classList.add('locked');

    if (state.selectedAddress) {
      const a = state.selectedAddress;
      els.selectedAddressPreview.innerHTML = `
        <strong>${a.full_name || a.name || 'Address'}</strong><br/>
        ${a.street_address || ''} ${a.apartment ? ', ' + a.apartment : ''}<br/>
        ${[a.city, a.state, a.postal_code].filter(Boolean).join(', ')}<br/>
        ${a.country || ''}
      `;
      els.selectedAddressPreview.classList.remove('hidden');
    }

    els.btnChangeAddress.classList.remove('hidden');
    els.addressConfirmFooter.classList.add('hidden');
    // Allow clicking header to change
    els.sectionAddress.classList.remove('locked');
    els.sectionAddress.querySelector('.section-body').style.display = 'none';
  }

  if (step === 2) {
    els.sectionPayment.classList.add('locked');
    const label = state.paymentMethod === 'CARD' ? 'Credit / Debit Card' : 'cash';
    els.selectedPaymentPreview.textContent = `✓ ${label}`;
    els.selectedPaymentPreview.classList.remove('hidden');
    els.btnChangePayment.classList.remove('hidden');
  }

  if (step === 3) {
    els.sectionReview.classList.add('locked');
  }
}

function unlockStep(step) {
  if (step === 1) {
    els.sectionAddress.querySelector('.section-body').style.display = '';
    els.selectedAddressPreview.classList.add('hidden');
  }

  if (step === 2) {
    els.sectionPayment.classList.remove('locked');
    els.sectionPayment.querySelector('.section-body').style.display = '';
    els.selectedPaymentPreview.classList.add('hidden');
  }

  if (step === 3) {
    els.sectionReview.classList.remove('locked');
    els.sectionReview.querySelector('.section-body').style.display = '';
  }

  state.step = step;
}

// ─── REVIEW ITEMS ─────────────────────────────────────────────────────────────
function renderReviewItems() {
  const items = state.cart?.items || [];

  els.reviewItems.innerHTML = items.length
    ? items.map(item => `
        <div class="review-item">
          <div class="item-img">
            ${item.image
              ? `<img src="${item.image}" alt="${item.name || ''}" />`
              : '📦'}
          </div>
          <div class="item-details">
            <div class="item-name">${item.name || item.menu_item?.name || 'Item'}</div>
            <div class="item-qty">Qty: ${item.quantity}</div>
            <div class="item-price">${fmt(item.price_snapshot || item.price || 0)}</div>
          </div>
        </div>
      `).join('')
    : '<p style="color:#666">No items in cart.</p>';
}

// ─── ADD ADDRESS ──────────────────────────────────────────────────────────────
async function handleAddAddress(e) {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form));

  hideError(els.addressFormError);

  try {
    const newAddr = await addressAPI.createAddress(data);
    state.addresses.unshift(newAddr);
    renderAddressList();
    selectAddress(newAddr);
    form.reset();
    els.addAddressForm.classList.add('hidden');
    els.addAddressToggle.classList.remove('hidden');
    showToast('Address added!', 'success');
  } catch (err) {
    showError(els.addressFormError, err.message || 'Failed to add address.');
  }
}

// ─── DELETE ADDRESS ───────────────────────────────────────────────────────────
async function handleDeleteAddress(id) {
  try {
    await addressAPI.deleteAddress(id);
    state.addresses = state.addresses.filter(a => a.id !== id);
    if (state.selectedAddress?.id === id) state.selectedAddress = state.addresses[0] || null;
    renderAddressList();
    showToast('Address removed.', 'success');
  } catch (err) {
    showToast('Could not remove address.', 'error');
  }
}

// ─── PLACE ORDER ─────────────────────────────────────────────────────────────
async function handlePlaceOrder() {
  if (!state.selectedAddress) {
    showToast('Please select a delivery address first.', 'error');
    return;
  }

  hideError(els.placeOrderError);
  els.btnPlaceOrder.disabled         = true;
  els.btnPlaceOrderSidebar.disabled  = true;
  els.btnPlaceOrder.textContent      = 'Placing order…';

  try {
    const order = await OrderAPI.create(state.selectedAddress.id, state.paymentMethod);
    showToast('Order placed successfully! 🎉', 'success');

    // Redirect to order confirmation after short delay
    setTimeout(() => {
      window.location.href = `/orders/${order.id}/`;
    }, 1500);
  } catch (err) {
    showError(els.placeOrderError, err.message || 'Failed to place order. Please try again.');
    els.btnPlaceOrder.disabled        = false;
    els.btnPlaceOrderSidebar.disabled = false;
    els.btnPlaceOrder.textContent     = 'Place Your Order';
  }
}

// ─── HELPERS ──────────────────────────────────────────────────────────────────
function fmt(amount) {
  return '$' + parseFloat(amount).toFixed(2);
}

function showError(el, msg) {
  el.textContent = msg;
  el.classList.remove('hidden');
}

function hideError(el) {
  el.textContent = '';
  el.classList.add('hidden');
}

let toastTimer;
function showToast(msg, type = '') {
  clearTimeout(toastTimer);
  els.toast.textContent   = msg;
  els.toast.className     = `toast${type ? ' ' + type : ''}`;
  toastTimer = setTimeout(() => els.toast.classList.add('hidden'), 3000);
}

