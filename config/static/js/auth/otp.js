document.addEventListener("DOMContentLoaded", () => {
    console.log("JS Loaded ✅");

    const inputs = document.querySelectorAll(".otp-input");
    const form = document.getElementById("otp-form");
    const hiddenInput = document.getElementById("otp_code");
    const resendBtn = document.querySelector(".resend a")
    const submitBtn = document.querySelector(".verify-btn")
    
    let timer = 60;

    function updateHiddenInput() {
        const otp = [...inputs].map(i => i.value).join("");
        hiddenInput.value = otp;
        return otp;
    }

   

    function startLoading() {

        submitBtn.disabled = true;
        submitBtn.innerText = "Verifying..."

        submitBtn.classList.add("loading")
    }

    function stopLoading() {

        submitBtn.disabled = false;
        submitBtn.innerText = "verify"

        submitBtn.classList.remove("loading")
    }


    function showError(msg) {

        let error = document.querySelector(".otp-error");

        if(!error){
            error = document.createElement("div");
            error.className = "otp-error"

            form.prepend(error);
        }

        error.innerText = msg;


        form.classList.add("shake");

        setTimeout(() => {
            form.classList.remove("shake");
        }, 400)
    }


    function autoSubmit() {
        otp = updateHiddenInput();

        if(otp.length === inputs.length) {

            startLoading();

            setTimeout(() => {
                form.submit();
            }, 600 )
        }
    }

    inputs.forEach((input, index) => {
        input.addEventListener("input", () => {
            input.value = input.value.replace(/[^0-9]/g, "");

            if(input.value && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }

            autoSubmit();
        });

        input.addEventListener("keydown", (e) => {
            if(e.key === "Backspace") {
                if(!input.value && index > 0 ) {
                    inputs[index - 1].focus();
                }
            }
        });


        input.addEventListener("paste", (e) => {
            e.preventDefault();

            const paste = e.clipboardData
                .getData("text")
                .replace(/\D/g,"")
                .split("");
            
            paste.forEach((num, i) => {
                if(i < inputs.length) {
                    inputs[i].value = num;
                }
            });

            autoSubmit();
            
        });
    });

    function startTimer() {
        resendBtn.classList.add("disabled");

        const interval = setInterval(() => {

            timer--;

            resendBtn.innerText = `Resend (${timer}s)`;

            if(timer <= 0){

                clearInterval(interval);

                resendBtn.innerText = "Resend";

                resendBtn.classList.remove("disabled");

                timer = 60;
            }
        }, 1000);
    }

    startTimer();

});

