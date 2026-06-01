const store = {

    state: {
        overview: {
            data: null,
            loading: false,
            error: null
        },
        personal: {
            data: null,
            loading: false,
            error: null
        }
    },

    listeners: [],

    subscribe(fn){
        this.listeners.push(fn);
        return () => {
            this.listeners = this.listeners.filter(listener => listener !== fn);
        };
    },

    notify(){
        console.log("STORE UPDATED", this.state);
        this.listeners.forEach(fn => fn(this.state));
    },

    set(key, value){
        // نعمل shallow clone للـ value علشان نقلل mutation bugs
        this.state[key] = {
            ...value,
             };
        this.notify();
    },

    get(key){
        return this.state[key];
    }
};
window.store = store;

export default store;
