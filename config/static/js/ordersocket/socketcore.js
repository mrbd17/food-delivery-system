export class SocketCore {
    constructor(url){
        this.url = url;
        this.ws = null,
        this.state = "idle";
        this.retries = 0;
        this.maxRetries = 1;
        this.manuallyClosed = false;
        this.reconnectTimer = null;
        this.pingInterval = null;
        this.lastPong = null;
    }
    connect(){
        if(this.state === "open" || this.state === "connecting") return;

        this.state = "connecting";

        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            this.state = "open";
            this.retries = 0;
            this.startHeartbeat();
        };

        this.ws.onmessage = (e) => {
            this.handleRawMessage(e.data);
        }

        this.ws.onclose = () => {
            this.state = "closed";
            this.stopHeartbeat();
            if(!this.manuallyClosed){
            this.scheduleReconnect();
            };
        }

    }    

    send(data) {
        if (this.state !== "open") return;

        this.ws.send(JSON.stringify(data));
    };

    handleRawMessage(raw){
        try {
            const data = JSON.parse(raw)

            if (data.type === "pong") {
                this.handlePong(data)
                return
            }

            if (this.onMessage){
                this.onMessage(data)
            }
        } catch(err) {
            console.log("Invalid Ws message",err)
        }
    };

    startHeartbeat(){
        this.lastPong = Date.now();

        this.pingInterval = setInterval(() => {
            if (this.state !== "open") return;

            const now = Date.now();

            if(now - this.lastPong > 30000){
                this.ws.close();
                return;
            }

            this.send({
                type: "ping",
                ts:now
            })
        }, 10000);
    }

    handlePong(data){
        this.lastPong = Date.now();
    }

    stopHeartbeat(){
        if (this.pingInterval){
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }

    scheduleReconnect(){
        if (this.retries >= this.maxRetries) return;

        const jitter = Math.random() * 1000;

        const delay = Math.min(
            1000 * 2 ** this.retries + jitter, 30000
        );
        this.reconnectTimer = setTimeout(() => {
            this.retries++;
            this.connect()
        }, delay)

    }
 
    disconnect(){
        this.manuallyClosed = true;

        this.stopHeartbeat();

        if(this.reconnectTimer){
            clearTimeout(this.reconnectTimer);
        }

        if(this.ws){
            this.ws.close();
            this.ws = null;
        }

        this.state = "closed";
    }

}