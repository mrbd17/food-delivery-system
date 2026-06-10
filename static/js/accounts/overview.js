// overview.js
// Simple overview section that reads from window.accountStore and updates UI.
(function(){
  if(!window.accountStore){
    window.accountStore = { _state: {}, _subs: [], getState(){return this._state}, setState(p){ this._state = Object.assign({}, this._state, p); this._subs.forEach(s=>s(this._state)); return this._state }, subscribe(fn){ this._subs.push(fn); return ()=>{ this._subs = this._subs.filter(s=>s!==fn) } } };
  }

  window.initOverview = function initOverview(container){
    const root = container || document;
    const nameEl = root.querySelector('.overview-name');
    const emailEl = root.querySelector('.overview-email');
    const avatarEl = root.querySelector('.overview-avatar');

    function render(state){
      if(!state) state = window.accountStore.getState();
      if(nameEl && state.name) nameEl.textContent = state.name;
      if(emailEl && state.email) emailEl.textContent = state.email;
      if(avatarEl && state.avatar) avatarEl.src = state.avatar;
    }

    render();
    const unsub = window.accountStore.subscribe(render);

    return function cleanup(){ unsub(); };
  };

})();
