import { OrderSocket } from '../ordersocket/ordersocket.js';
import { OrderAPI } from '../orders/orderAPI.js';
/* ─── XSS-safe DOM helpers ───────────────────────────────────────── */
function setText(el, value) {
  el.textContent = value ?? '';
}

function sanitize(value) {
  const el = document.createElement('div');
  el.textContent = String(value ?? '');
  return el.innerHTML;
}

function createEl(tag, attrs = {}, children = []){
  const el = document.createElement(tag);
  for (const [key, val] of Object.entries(attrs)){
    if (key === "className") el.className = val;
    else if (key === "dataset") Object.assign(el.dataset, val);
    else if (key.startsWith('aria')) el.setAttribute(key, val);
    else el[key] = val
  }

  for (const child of children){
    if(typeof child === "string") el.appendChild(document.createTextNode(child));
    else if (child instanceof Node) el.appendChild(child);
  }

  return el;
}

/* ─── URL extraction ─────────────────────────────────────────────── */
function extractOrderId(){
  const match = window.location.pathname.match(
    /\/orders\/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\//i
  )

  return match ? match[1] : null;
}
const STATUS_LABELS = {
  pending:    'Pending',
  processing: 'Processing',
  shipping:   'On the way',
  delivered:  'Delivered',
  cancelled:  'Cancelled',
};

const TIMELINE_STEPS = [
  {
    key:   'pending',
    title: 'Order placed',
    desc:  'Payment confirmed',
  },
  {
    key:   'processing',
    title: 'Processing',
    desc:  'Packed at warehouse',
  },
  {
    key:   'shipping',
    title: 'Picked up by courier',
    desc:  'Out for delivery',
  },
  {
    key:   'delivered',
    title: 'Delivered',
    desc:  'Est. 3:00 – 5:00 PM',
  },
];

const STATUS_ORDER = ['pending', 'processing', 'shipping', 'delivered'];

const DELIVERY_FEE = 35;
const CURRENCY    = 'EGP';

/* ─── Render: Header ─────────────────────────────────────────────── */
function renderHeader(order) {
  const section = document.getElementById('section-header');

  const numberEl  = document.getElementById('order-number');
  const badgeEl   = document.getElementById('status-badge');
  const arrivalEl = document.getElementById('arrival-time');
  const mapEl     = document.getElementById('map-text');

  setText(numberEl, order.order_number);

  badgeEl.dataset.status = order.status;
  setText(badgeEl, STATUS_LABELS[order.status] ?? order.status);

  setText(arrivalEl, order.status === 'delivered' ? 'Delivered' : 'Today, 3:00 – 5:00 PM');

  setText(mapEl, order.status === 'shipping'
    ? '📍 Live map · 4.2 km away'
    : `📦 ${order.delivery_address}`
  );

  reveal(section);
}

/* ─── Render: Progress ───────────────────────────────────────────── */
function renderProgress(status) {
  const timeline  = document.getElementById('timeline');
  const section   = document.getElementById('section-progress');
  const activeIdx = STATUS_ORDER.indexOf(status);

  timeline.innerHTML = '';

  TIMELINE_STEPS.forEach((step, i) => {
    let state = 'pending';
    if (i < activeIdx)  state = 'done';
    if (i === activeIdx) state = 'active';

    const dot  = createEl('div', { className: 'step-dot' });
    const body = createEl('div', { className: 'step-body' }, [
      createEl('div', { className: 'step-title' }, [step.title]),
      createEl('div', { className: 'step-desc'  }, [step.desc]),
    ]);

    const li = createEl('li', {
      className: `timeline-item is-${state === 'done' ? 'done' : state === 'active' ? 'active' : 'pending'}`,
      role: 'listitem',
      'aria-label': `${step.title}: ${state}`,
    }, [dot, body]);

    timeline.appendChild(li);
  });

  reveal(section);
}

/* ─── Render: Items ──────────────────────────────────────────────── */
function renderItems(order) {
  const list    = document.getElementById('items-list');
  const section = document.getElementById('section-items');

  list.innerHTML = '';

  for (const item of order.items) {
    const thumb    = createEl('div', { className: 'item-thumb', 'aria-hidden': 'true' });
    const nameEl   = createEl('div', { className: 'item-name'  });
    const qtyEl    = createEl('div', { className: 'item-qty'   });
    const priceEl  = createEl('div', { className: 'item-price' });
    const infoEl   = createEl('div', { className: 'item-info'  }, [nameEl, qtyEl]);

    setText(nameEl,  item.name);
    setText(qtyEl,   `Qty: ${item.quantity}`);
    setText(priceEl, `${CURRENCY} ${Number(item.price).toLocaleString()}`);

    const li = createEl('li', { className: 'item-row' }, [thumb, infoEl, priceEl]);
    list.appendChild(li);
  }

  renderSummary(order);
  reveal(section);
}

/* ─── Render: Summary ────────────────────────────────────────────── */
function renderSummary(order) {
  const subtotal = Number(order.subtotal);
  const total    = subtotal + DELIVERY_FEE;

  setText(document.getElementById('summary-subtotal'),
    `${CURRENCY} ${subtotal.toLocaleString()}`);

  setText(document.getElementById('summary-delivery'),
    `${CURRENCY} ${DELIVERY_FEE}`);

  setText(document.getElementById('summary-total'),
    `${CURRENCY} ${total.toLocaleString()}`);
}

/* ─── Full render ────────────────────────────────────────────────── */
function renderOrder(order) {
  renderHeader(order);
  renderProgress(order.status);
  renderItems(order);

  const actionBar = document.getElementById('action-bar');
  actionBar.classList.remove('hidden');

  const cancelBtn = document.getElementById('btn-cancel');
  const nonCancellable = ['delivered', 'cancelled'];
  cancelBtn.disabled = nonCancellable.includes(order.status);
}


/* ─── Partial update (realtime) ──────────────────────────────────── */
function applyStatusUpdate(newStatus) {
  const badgeEl   = document.getElementById('status-badge');
  const cancelBtn = document.getElementById('btn-cancel');

  badgeEl.dataset.status = newStatus;
  setText(badgeEl, STATUS_LABELS[newStatus] ?? newStatus);

  renderProgress(newStatus);

  const nonCancellable = ['delivered', 'cancelled'];
  cancelBtn.disabled = nonCancellable.includes(newStatus);

  showToast(`Status updated: ${STATUS_LABELS[newStatus] ?? newStatus}`, 'info');
}

/* ─── UI utilities ───────────────────────────────────────────────── */
function reveal(el) {
  el.classList.remove('hidden');
  el.classList.add('reveal');
}

function showSkeleton() {
  document.getElementById('skeleton').classList.remove('hidden');
}

function hideSkeleton() {
  document.getElementById('skeleton').classList.add('hidden');
}

function showError(message) {
  const content = document.getElementById('content');
  content.innerHTML = '';

  const box = createEl('div', { className: 'error-state' }, [
    createEl('h2', {}, ['Unable to load order']),
    createEl('p',  {}, [message]),
  ]);

  content.appendChild(box);
}

let toastTimer = null;
function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  toast.className = `toast toast--${type}`;
  setText(toast, message);

  toast.classList.remove('hidden');
  requestAnimationFrame(() => toast.classList.add('show'));

  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.classList.add('hidden'), 300);
  }, 3500);
}

/* ─── Buttons ────────────────────────────────────────────────────── */
function bindButtons(socket) {
  document.getElementById('btn-back').addEventListener('click', () => {
    history.back();
  });

  document.getElementById('btn-cancel').addEventListener('click',onCancelOrder);

  document.getElementById('btn-support').addEventListener('click', () => {
    window.location.href = '/support/';
  });
}

async function onCancelOrder(){
  const orderId = extractOrderId();

  if(!orderId) return;

  try {
    await OrderAPI.cancel(orderId);
  }catch(err){
    console.log(err);
  }
}

/* ─── WebSocket integration ──────────────────────────────────────── */
function connectSocket(orderId) {
  const socket = new OrderSocket(orderId);

  socket.on('order.updated', (payload) => {
    if (payload?.status) applyStatusUpdate(payload.status);
  });

  socket.on('order.cancelled', () => {
    applyStatusUpdate('cancelled');
    showToast('Your order has been cancelled.', 'error');
    document.getElementById('btn-cancel').disabled = true;
  });
    
  socket.connect();
  return socket;
}

/* ─── Bootstrap ──────────────────────────────────────────────────── */
async function init() {
  const orderId = extractOrderId();

  if (!orderId) {
    showError('Invalid order URL. Please go back and try again.');
    return;
  }

  showSkeleton();

  try {
    const order  = await OrderAPI.detail(orderId);
    hideSkeleton();
    renderOrder(order);

    const socket = connectSocket(orderId);
    bindButtons(socket);

    window.addEventListener('beforeunload', () => socket.disconnect());
  } catch (err) {
    hideSkeleton();
    showError('Could not load order details. Please refresh.');
    console.error('[OrderTracking] fetch error:', err);
  }
}

init();