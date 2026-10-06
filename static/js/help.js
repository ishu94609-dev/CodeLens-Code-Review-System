document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       SIDEBAR TOGGLE
    ====================================================== */

    const sidebar = document.getElementById("sidebar");
    const sidebarToggle = document.getElementById("sidebarToggle");

    if (sidebar && sidebarToggle) {
        sidebarToggle.addEventListener("click", function () {
            sidebar.classList.toggle("collapsed");
        });
    }


    /* =====================================================
       PROFILE AVATAR - LOGIN USER FIRST LETTER
    ====================================================== */

    const headerAvatar =
        document.querySelector(".header-avatar");

    if (headerAvatar) {

        fetch("/api/profile", {
            method: "GET",
            credentials: "same-origin"
        })
        .then(function (response) {

            if (!response.ok) {
                throw new Error("Unable to load profile.");
            }

            return response.json();

        })
        .then(function (data) {

            /*
             * Support different API response formats.
             */
            const user =
                data.user ||
                data.profile ||
                data;

            const username =
                user.username ||
                user.name ||
                user.full_name ||
                user.email ||
                "";

            if (username) {

                const firstLetter =
                    String(username)
                        .trim()
                        .charAt(0)
                        .toUpperCase();

                if (firstLetter) {
                    headerAvatar.textContent =
                        firstLetter;
                }
            }

        })
        .catch(function (error) {

            console.error(
                "Profile Avatar Error:",
                error
            );

        });

    }


    /* =====================================================
       FAQ ACCORDION
    ====================================================== */

    const faqQuestions =
        document.querySelectorAll(".faq-question");

    faqQuestions.forEach(function (question) {

        question.addEventListener("click", function () {

            const currentItem =
                question.closest(".faq-item");

            if (!currentItem) {
                return;
            }

            const currentAnswer =
                currentItem.querySelector(".faq-answer");

            document.querySelectorAll(".faq-item")
                .forEach(function (item) {

                    if (item !== currentItem) {

                        item.classList.remove("open");

                        const answer =
                            item.querySelector(".faq-answer");

                        if (answer) {
                            answer.style.maxHeight = null;
                        }
                    }
                });

            currentItem.classList.toggle("open");

            if (
                currentItem.classList.contains("open") &&
                currentAnswer
            ) {

                currentAnswer.style.maxHeight =
                    currentAnswer.scrollHeight + "px";

            } else if (currentAnswer) {

                currentAnswer.style.maxHeight = null;

            }

        });

    });


    /* =====================================================
       SUPPORT CARD NAVIGATION
    ====================================================== */

    const supportLinks =
        document.querySelectorAll(
            ".support-link[data-target]"
        );

    supportLinks.forEach(function (link) {

        link.addEventListener("click", function () {

            const targetId =
                link.getAttribute("data-target");

            const target =
                document.getElementById(targetId);

            if (target) {

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }

        });

    });


    /* =====================================================
       SEARCH
    ====================================================== */

    const globalSearch =
        document.getElementById("globalSearch");

    const helpSearch =
        document.getElementById("helpSearch");


    /* =====================================================
       SEARCH RESULT MESSAGE
    ====================================================== */

    function createSearchMessage() {

        let message =
            document.getElementById(
                "helpSearchMessage"
            );

        if (message) {
            return message;
        }

        message =
            document.createElement("div");

        message.id =
            "helpSearchMessage";

        message.style.fontSize = "15px";
        message.style.margin = "18px 0 14px 24px";
        message.style.color = "#ffffff";
        message.style.fontFamily = "inherit";
        message.style.fontWeight = "400";
        message.style.width = "100%";
        message.style.boxSizing = "border-box";

        const mainContent =
            document.querySelector(".main-content") ||
            document.querySelector(".content") ||
            document.querySelector("main");

        if (!mainContent) {
            return message;
        }

        let pageTitle =
            mainContent.querySelector(".page-title");

        if (!pageTitle) {
            pageTitle =
                mainContent.querySelector(".main-title");
        }

        if (!pageTitle) {
            pageTitle =
                mainContent.querySelector("h1");
        }

        /*
         * Put message BELOW the complete title/header row.
         */

        if (pageTitle) {

            let titleContainer = pageTitle;

            while (
                titleContainer.parentElement &&
                titleContainer.parentElement !== mainContent
            ) {
                titleContainer =
                    titleContainer.parentElement;
            }

            if (
                titleContainer.parentElement === mainContent
            ) {

                mainContent.insertBefore(
                    message,
                    titleContainer.nextSibling
                );

            } else {

                mainContent.appendChild(message);

            }

        } else {

            mainContent.insertBefore(
                message,
                mainContent.firstChild
            );

        }

        return message;
    }


    function removeSearchMessage() {

        const message =
            document.getElementById(
                "helpSearchMessage"
            );

        if (message) {
            message.remove();
        }

    }


    function updateSearchMessage(searchValue) {

        if (!searchValue) {

            removeSearchMessage();

            return;
        }

        const message =
            createSearchMessage();

        message.textContent =
            `Search results for "${searchValue}"`;
    }


    /* =====================================================
       SEARCH FUNCTION
    ====================================================== */

    function performSearch(value) {

        const searchValue =
            String(value || "")
                .toLowerCase()
                .trim();

        const faqItems =
            document.querySelectorAll(".faq-item");

        const supportCards =
            document.querySelectorAll(
                ".support-card, .support-link"
            );

        const sections =
            document.querySelectorAll(
                ".help-section, .support-section"
            );


        /* EMPTY SEARCH */

        if (searchValue === "") {

            faqItems.forEach(function (item) {
                item.style.display = "";
            });

            supportCards.forEach(function (card) {
                card.style.display = "";
            });

            sections.forEach(function (section) {
                section.style.display = "";
            });

            removeSearchMessage();

            return;
        }


        updateSearchMessage(searchValue);


        /* FAQ FILTER */

        faqItems.forEach(function (item) {

            const text =
                item.textContent.toLowerCase();

            item.style.display =
                text.includes(searchValue)
                    ? ""
                    : "none";

        });


        /* SUPPORT CARD FILTER */

        supportCards.forEach(function (card) {

            const text =
                card.textContent.toLowerCase();

            card.style.display =
                text.includes(searchValue)
                    ? ""
                    : "none";

        });


        /* SECTION FILTER */

        sections.forEach(function (section) {

            const text =
                section.textContent.toLowerCase();

            section.style.display =
                text.includes(searchValue)
                    ? ""
                    : "none";

        });

    }


    /* =====================================================
       GLOBAL HEADER SEARCH
    ====================================================== */

    if (globalSearch) {

        globalSearch.addEventListener(
            "input",
            function () {

                if (helpSearch) {
                    helpSearch.value =
                        globalSearch.value;
                }

                performSearch(
                    globalSearch.value
                );

            }
        );

        globalSearch.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    performSearch(
                        globalSearch.value
                    );

                }

            }
        );

    }


    /* =====================================================
       HELP PAGE SEARCH
    ====================================================== */

    if (helpSearch) {

        helpSearch.addEventListener(
            "input",
            function () {

                if (globalSearch) {
                    globalSearch.value =
                        helpSearch.value;
                }

                performSearch(
                    helpSearch.value
                );

            }
        );

        helpSearch.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    performSearch(
                        helpSearch.value
                    );

                }

            }
        );

    }


    /* =====================================================
       LOGOUT ELEMENTS
    ====================================================== */

    const logoutButton =
        document.getElementById("logoutButton");

    const logoutModal =
        document.getElementById("logoutModal");

    const cancelLogout =
        document.getElementById("cancelLogout");

    const confirmLogout =
        document.getElementById("confirmLogout");

    const logoutForm =
        document.getElementById("logoutForm");


    /* =====================================================
       OPEN LOGOUT MODAL
    ====================================================== */

    if (logoutButton && logoutModal) {

        logoutButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                logoutModal.classList.add("show");

            }
        );

    }


    /* =====================================================
       CANCEL LOGOUT
    ====================================================== */

    if (cancelLogout && logoutModal) {

        cancelLogout.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                logoutModal.classList.remove("show");

            }
        );

    }


    /* =====================================================
       CLICK OUTSIDE LOGOUT MODAL
    ====================================================== */

    if (logoutModal) {

        logoutModal.addEventListener(
            "click",
            function (event) {

                if (event.target === logoutModal) {

                    logoutModal.classList.remove("show");

                }

            }
        );

    }


    /* =====================================================
       CONFIRM LOGOUT
       FIXED
    ====================================================== */

    if (confirmLogout) {

        confirmLogout.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();


                /* -----------------------------------------
                   If logout form exists, submit it
                ----------------------------------------- */

                if (logoutForm) {

                    /*
                     * requestSubmit() properly triggers
                     * the browser form submission.
                     */

                    if (
                        typeof logoutForm.requestSubmit ===
                        "function"
                    ) {

                        logoutForm.requestSubmit();

                    } else {

                        logoutForm.submit();

                    }

                    return;
                }


                /* -----------------------------------------
                   Fallback:
                   If form is missing, go to /logout
                ----------------------------------------- */

                window.location.href = "/logout";

            }
        );

    }


    /* =====================================================
       LOGOUT FORM SUBMIT
       EXTRA SAFETY
    ====================================================== */

    if (logoutForm) {

        logoutForm.addEventListener(
            "submit",
            function () {

                console.log(
                    "CodeLens logout form submitted."
                );

            }
        );

    }


    /* =====================================================
       ESC KEY
    ====================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                if (
                    logoutModal &&
                    logoutModal.classList.contains("show")
                ) {

                    logoutModal.classList.remove("show");

                }

            }

        }
    );


    /* =====================================================
       CONTACT SUPPORT
    ====================================================== */

    const contactSupportLinks =
        document.querySelectorAll(
            ".support-link"
        );

    contactSupportLinks.forEach(function (link) {

        const linkText =
            link.textContent
                .trim()
                .toLowerCase();

        /* Only Contact Support link */
        if (!linkText.includes("contact support")) {
            return;
        }

        link.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();
                event.stopPropagation();

                const subject =
                    "CodeLens Support Request";

                const message =
                    "Hello CodeLens Support,\n\n" +
                    "I need assistance regarding CodeLens.\n\n" +
                    "Issue:\n\n" +
                    "Thank you.";

                const formData =
                    new FormData();

                formData.append(
                    "subject",
                    subject
                );

                formData.append(
                    "message",
                    message
                );

                try {

                    const response =
                        await fetch(
                            "/contact-support",
                            {
                                method: "POST",
                                body: formData
                            }
                        );

                    const result =
                        await response.json();

                    if (result.success) {

                        alert(
                            "Support request sent successfully."
                        );

                    } else {

                        alert(
                            result.message ||
                            "Unable to send support request."
                        );

                    }

                } catch (error) {

                    console.error(
                        "Contact Support Error:",
                        error
                    );

                    alert(
                        "Unable to send support request."
                    );

                }

            }
        );

    });


    /* =====================================================
       INITIALIZATION
    ====================================================== */

    console.log(
        "CodeLens Help & Support initialized successfully."
    );

});