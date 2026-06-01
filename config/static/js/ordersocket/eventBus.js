export class EventBus {
    constructor(){
        this.events = {}
    };

    on(event, cb){
        if(!this.events[event]){
            this.events[event] = []
        };

        this.events[event].push(cb)
    };

    emit(event, data){
        (this.events[event] || []).forEach(cb => cb(data))
    }
    
}