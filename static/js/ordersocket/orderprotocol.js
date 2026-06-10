export class OrderProtocol {
    constructor(core, bus){
        this.core = core;
        this.bus = bus;   
        this.handlers = new Map();
        this.registerHandlers();

        this.core.onMessage = (data) => this.route(data);
    }

    registerHandlers() {
        this.on("order.updated", (data) => {
            this.bus.emit("order.updated", data)
        });

        this.on("order.cancelled", (data) => {
            this.bus.emit("order.cancelled", data)
        });

        this.on("order.established", (data) => {
            this.bus.emit("order.established", data);
        });
    };

    on(type, handler){
        this.handlers.set(type, handler)
    }

    route(data){
        if(!this.isValid(data)) return;

        const handler = this.handlers.get(data.type);

        if(!handler){
            this.bus.emit("unknown_event", data)
            return;
        };

        handler(data)
    };

    isValid(data){
        if(!data || typeof data !== "object") return false;
        if(typeof data.type !=="string") return false;
        return true;
    }

    send(type, payload){
        this.core.send({
            type,
            payload, 
            
        });
    };

    cancel(order_id){
        this.send("order_cancel", {order_id})
    }
}