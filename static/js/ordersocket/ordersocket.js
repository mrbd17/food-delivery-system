import {SocketCore} from './socketcore.js';
import {OrderProtocol} from './orderprotocol.js';
import {EventBus} from './eventBus.js';

export class OrderSocket{
    constructor(orderId){
        this.orderId = orderId;
        this.bus = new EventBus();
        this.core = new SocketCore(
            `ws://127.0.0.1:8000/ws/orders/${this.orderId}/`
        );
        this.protocol = new OrderProtocol(this.core, this.bus);
    }

    connect(){
        this.core.connect();
    }

    disconnect(){
        this.core.disconnect();
    }

    on(event, cb){
        this.bus.on(event, cb);
    }

    cancel(){
        this.protocol.cancel(this.orderId);
    }


}
