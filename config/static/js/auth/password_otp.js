document.addEventListener("DOMContentLoaded", () => {

    console.log("OTP JS Loaded ✅");

    const inputs = document.querySelectorAll(".otp-input");
    const form = document.getElementById("otp-form");
    const hiddenInput = document.getElementById("otp_code");

    const submitBtn = document.querySelector(".verify-btn");
    const resendBtn = document.querySelector(".resend-btn");

    let timer = 1;


    /* ==========================
       Update Hidden Input
    ========================== */
    function updateHiddenInput() {

        const otp = [...inputs]
            .map(input => input.value)
            .join("");

        hiddenInput.value = otp;

        return otp;
    }


    /* ==========================
       Button Loading
    ========================== */
    function startLoading() {

        submitBtn.disabled = true;
        submitBtn.innerText = "Verifying...";
    }

    function stopLoading() {

        submitBtn.disabled = false;
        submitBtn.innerText = "Verify";
    }


    /* ==========================
       Auto Submit
    ========================== */
    function autoSubmit() {

        const otp = updateHiddenInput();

        if (otp.length === inputs.length) {

            startLoading();

            setTimeout(() => {
                form.submit();
            }, 400);
        }
    }


    /* ==========================
       Input Logic
    ========================== */
    inputs.forEach((input, index) => {

        /* Allow Numbers Only */
        input.addEventListener("input", () => {

            input.value = input.value.replace(/[^0-9]/g, "");

            if (input.value && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }

            autoSubmit();
        });


        /* Backspace */
        input.addEventListener("keydown", (e) => {

            if (e.key === "Backspace") {

                if (!input.value && index > 0) {
                    inputs[index - 1].focus();
                }
            }
        });


        /* Paste Support */
        input.addEventListener("paste", (e) => {

            e.preventDefault();

            const pasteData = e.clipboardData
                .getData("text")
                .replace(/\D/g, "")
                .split("");

            pasteData.forEach((num, i) => {

                if (i < inputs.length) {
                    inputs[i].value = num;
                }
            });

            autoSubmit();
        });

    });


    /* ==========================
       Resend Timer
    ========================== */
    function startTimer() {

        resendBtn.classList.add("disabled");

        let interval = setInterval(() => {

            timer--;

            resendBtn.innerText = `Resend (${timer}s)`;

            if (timer <= 0) {

                clearInterval(interval);

                resendBtn.innerText = "Resend Code";

                resendBtn.classList.remove("disabled");

                timer = 1;
            }

        }, 1000);
    }


    startTimer();

});
