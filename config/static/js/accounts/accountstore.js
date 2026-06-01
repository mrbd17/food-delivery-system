window.accountStore = (function () { 

    let state = {
        user: {
            name: "",
            email: "",
            phone: "",
            avatar: ""
        }
    };

    const listeners = new Set();

    function getState() {
        return state;
    }

    function setUser(newUser) {
        state.user = { ...state.user, ...newUser };
        notify();
    }

    function subscribe(fn) {
        listeners.add(fn);
        return () => listeners.delete(fn);
    }

    function notify() {
        listeners.forEach(fn => fn(state));
    }
    return {
        getState,
        setUser,
        subscribe
    };

})();