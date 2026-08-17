(() => {
    "use strict";

    const menu = document.getElementById(
        "mainMenu"
    );

    const healthText = document.getElementById(
        "backendHealth"
    );

    const healthDot = document.getElementById(
        "backendHealthDot"
    );


    if (menu) {
        menu.addEventListener(
            "click",
            (event) => {
                const item = event.target.closest(
                    ".nav-item"
                );

                if (!item) {
                    return;
                }

                for (
                    const link
                    of menu.querySelectorAll(
                        ".nav-item"
                    )
                ) {
                    link.classList.remove(
                        "active"
                    );
                }

                item.classList.add(
                    "active"
                );
            }
        );
    }


    async function checkBackend() {
        try {
            const response = await fetch(
                "/api/v1/health",
                {
                    cache: "no-store",
                }
            );

            const payload = await response.json();

            if (
                response.ok
                &&
                payload.ok
            ) {
                healthText.textContent = "Работает";

                healthDot.classList.remove(
                    "error"
                );

                healthDot.classList.add(
                    "ok"
                );

                return;
            }

            throw new Error(
                "health failed"
            );

        } catch (error) {
            healthText.textContent = "Ошибка";

            healthDot.classList.remove(
                "ok"
            );

            healthDot.classList.add(
                "error"
            );
        }
    }


    checkBackend();

    window.setInterval(
        checkBackend,
        10000
    );
})();
