/* =========================================================
   CODELENS - SAVED CODE PAGE
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    "use strict";


    /* =====================================================
       ELEMENTS
       ===================================================== */

    const sidebar =
        document.getElementById("sidebar");

    const sidebarToggle =
        document.getElementById("sidebarToggle");

    const globalSearch =
        document.getElementById("globalSearch");

    const savedSearch =
        document.getElementById("savedSearch");

    const languageFilter =
        document.getElementById("languageFilter");

    const savedList =
        document.getElementById("savedList");

    const emptyState =
        document.getElementById("emptyState");

    const newCodeButton =
        document.getElementById("newCodeButton");

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
       SIDEBAR TOGGLE
       ===================================================== */

    if (
        sidebarToggle &&
        sidebar
    ) {

        sidebarToggle.addEventListener(
            "click",
            function () {

                sidebar.classList.toggle(
                    "collapsed"
                );

            }
        );

    }


    /* =====================================================
       DATA
       ===================================================== */

    let savedCodes = [];


    /* =====================================================
       LOAD SAVED CODE
       ===================================================== */

    async function loadSavedCode() {

        try {

            const response =
                await fetch(
                    "/api/saved-code",
                    {
                        method: "GET",

                        headers: {
                            "Accept":
                                "application/json"
                        },

                        cache:
                            "no-store"
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Failed to load saved code."
                );

            }


            const data =
                await response.json();


            if (
                data &&
                data.success &&
                Array.isArray(
                    data.saved_code
                )
            ) {

                savedCodes =
                    data.saved_code;

            } else {

                savedCodes = [];

            }


            renderSavedCode();


        } catch (error) {

            console.error(
                "LOAD SAVED CODE ERROR:",
                error
            );


            savedCodes = [];


            renderSavedCode();

        }

    }


    /* =====================================================
       SEARCH MESSAGE
       ===================================================== */

    function createSearchMessage() {

        let message =
            document.getElementById(
                "savedSearchMessage"
            );


        if (message) {
            return message;
        }


        message =
            document.createElement(
                "div"
            );


        message.id =
            "savedSearchMessage";


        message.style.fontSize =
            "15px";


        message.style.margin =
            "18px 0 14px 24px";


        message.style.color =
            "#ffffff";


        message.style.fontFamily =
            "inherit";


        message.style.fontWeight =
            "400";


        message.style.width =
            "100%";


        message.style.boxSizing =
            "border-box";


        const mainContent =
            document.querySelector(
                ".main-content"
            ) ||
            document.querySelector(
                ".content"
            ) ||
            document.querySelector(
                "main"
            );


        if (!mainContent) {
            return message;
        }


        let pageTitle =
            mainContent.querySelector(
                ".page-title"
            );


        if (!pageTitle) {

            pageTitle =
                mainContent.querySelector(
                    ".main-title"
                );

        }


        if (!pageTitle) {

            pageTitle =
                mainContent.querySelector(
                    "h1"
                );

        }


        if (pageTitle) {

            /*
             * Find the complete top-level
             * title/header row.
             */

            let titleContainer =
                pageTitle;


            while (
                titleContainer.parentElement &&
                titleContainer.parentElement !==
                    mainContent
            ) {

                titleContainer =
                    titleContainer.parentElement;

            }


            if (
                titleContainer.parentElement ===
                mainContent
            ) {

                mainContent.insertBefore(
                    message,
                    titleContainer.nextSibling
                );

            } else {

                mainContent.appendChild(
                    message
                );

            }

        } else {

            mainContent.insertBefore(
                message,
                mainContent.firstChild
            );

        }


        return message;

    }


    /* =====================================================
       REMOVE SEARCH MESSAGE
       ===================================================== */

    function removeSearchMessage() {

        const message =
            document.getElementById(
                "savedSearchMessage"
            );


        if (message) {
            message.remove();
        }

    }


    /* =====================================================
       UPDATE SEARCH MESSAGE
       ===================================================== */

    function updateSearchMessage(
        value
    ) {

        if (!value) {

            removeSearchMessage();

            return;

        }


        const message =
            createSearchMessage();


        message.textContent =
            `Search results for "${value}"`;

    }


    /* =====================================================
       RENDER SAVED CODE
       ===================================================== */

    function renderSavedCode() {

        if (!savedList) {
            return;
        }


        /* =================================================
           SEARCH VALUE
           ================================================= */

        const searchText =
            savedSearch
                ? savedSearch.value
                    .trim()
                    .toLowerCase()
                : "";


        /* =================================================
           LANGUAGE VALUE
           ================================================= */

        const selectedLanguage =
            languageFilter
                ? languageFilter.value
                    .trim()
                    .toLowerCase()
                : "all";


        /* =================================================
           UPDATE SEARCH MESSAGE
           ================================================= */

        updateSearchMessage(
            searchText
        );


        /* =================================================
           FILTER SAVED CODE
           ================================================= */

        const filteredCodes =
            savedCodes.filter(
                function (item) {

                    const filename =
                        String(
                            item.filename ||
                            ""
                        ).toLowerCase();


                    const language =
                        String(
                            item.language ||
                            ""
                        ).toLowerCase();


                    const code =
                        String(
                            item.code ||
                            ""
                        ).toLowerCase();


                    /*
                     * Search:
                     * filename
                     * language
                     * code
                     */

                    const matchesSearch =
                        searchText === "" ||
                        filename.includes(
                            searchText
                        ) ||
                        language.includes(
                            searchText
                        ) ||
                        code.includes(
                            searchText
                        );


                    const matchesLanguage =
                        selectedLanguage ===
                            "all" ||
                        language ===
                            selectedLanguage;


                    return (
                        matchesSearch &&
                        matchesLanguage
                    );

                }
            );


        /* =================================================
           REMOVE OLD GENERATED CARDS
           ================================================= */

        const oldCards =
            savedList.querySelectorAll(
                ".saved-code-card"
            );


        oldCards.forEach(
            function (card) {

                card.remove();

            }
        );


        /* =================================================
           EMPTY STATE
           ================================================= */

        if (
            filteredCodes.length === 0
        ) {

            if (emptyState) {

                emptyState.style.display =
                    "flex";


                const heading =
                    emptyState.querySelector(
                        "h3"
                    );


                const paragraph =
                    emptyState.querySelector(
                        "p"
                    );


                if (
                    savedCodes.length === 0
                ) {

                    if (heading) {

                        heading.textContent =
                            "No Saved Code";

                    }


                    if (paragraph) {

                        paragraph.textContent =
                            "Your saved code snippets will appear here.";

                    }

                } else {

                    if (heading) {

                        heading.textContent =
                            "No Matching Code";

                    }


                    if (paragraph) {

                        paragraph.textContent =
                            "No saved code matches your search.";

                    }

                }

            }


            return;

        }


        /* =================================================
           HIDE EMPTY STATE
           ================================================= */

        if (emptyState) {

            emptyState.style.display =
                "none";

        }


        /* =================================================
           CREATE CARDS
           ================================================= */

        filteredCodes.forEach(
            function (item) {


                /* =========================================
                   CARD
                   ========================================= */

                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "saved-code-card";


                /* =========================================
                   HEADER
                   ========================================= */

                const header =
                    document.createElement(
                        "div"
                    );


                header.className =
                    "code-card-header";


                /* =========================================
                   TITLE AREA
                   ========================================= */

                const titleArea =
                    document.createElement(
                        "div"
                    );


                titleArea.className =
                    "code-card-title";


                /* =========================================
                   FILE ICON
                   ========================================= */

                const icon =
                    document.createElement(
                        "div"
                    );


                icon.className =
                    "code-file-icon";


                icon.innerHTML =
                    '<i class="fa-solid fa-code"></i>';


                /* =========================================
                   FILE NAME
                   ========================================= */

                const title =
                    document.createElement(
                        "div"
                    );


                title.textContent =
                    item.filename ||
                    "Untitled";


                title.title =
                    item.filename ||
                    "Untitled";


                titleArea.appendChild(
                    icon
                );


                titleArea.appendChild(
                    title
                );


                /* =========================================
                   LANGUAGE
                   ========================================= */

                const language =
                    document.createElement(
                        "span"
                    );


                language.className =
                    "code-language";


                language.textContent =
                    String(
                        item.language ||
                        "Unknown"
                    ).toUpperCase();


                /* =========================================
                   HEADER APPEND
                   ========================================= */

                header.appendChild(
                    titleArea
                );


                header.appendChild(
                    language
                );


                /* =========================================
                   CODE PREVIEW
                   ========================================= */

                const preview =
                    document.createElement(
                        "pre"
                    );


                preview.className =
                    "code-preview";


                preview.textContent =
                    item.code ||
                    "";


                preview.setAttribute(
                    "aria-label",
                    "Saved code preview"
                );


                /* =========================================
                   FOOTER
                   ========================================= */

                const footer =
                    document.createElement(
                        "div"
                    );


                footer.className =
                    "code-card-footer";


                /* =========================================
                   DATE
                   ========================================= */

                const date =
                    document.createElement(
                        "span"
                    );


                date.className =
                    "saved-date";


                if (item.created_at) {

                    date.textContent =
                        "Saved: " +
                        item.created_at;

                } else {

                    date.textContent =
                        "Saved Code";

                }


                /* =========================================
                   ACTIONS
                   ========================================= */

                const actions =
                    document.createElement(
                        "div"
                    );


                actions.className =
                    "code-card-actions";


                /* =========================================
                   COPY BUTTON
                   ========================================= */

                const copyButton =
                    document.createElement(
                        "button"
                    );


                copyButton.type =
                    "button";


                copyButton.className =
                    "copy-code-btn";


                copyButton.innerHTML =
                    '<i class="fa-regular fa-copy"></i> Copy';


                copyButton.addEventListener(
                    "click",
                    async function () {

                        const code =
                            item.code ||
                            "";


                        try {

                            if (
                                navigator.clipboard &&
                                window.isSecureContext
                            ) {

                                await navigator.clipboard.writeText(
                                    code
                                );

                            } else {

                                const textarea =
                                    document.createElement(
                                        "textarea"
                                    );


                                textarea.value =
                                    code;


                                textarea.style.position =
                                    "fixed";


                                textarea.style.left =
                                    "-9999px";


                                document.body.appendChild(
                                    textarea
                                );


                                textarea.select();


                                document.execCommand(
                                    "copy"
                                );


                                textarea.remove();

                            }


                            copyButton.innerHTML =
                                '<i class="fa-solid fa-check"></i> Copied';


                            setTimeout(
                                function () {

                                    copyButton.innerHTML =
                                        '<i class="fa-regular fa-copy"></i> Copy';

                                },
                                1500
                            );


                        } catch (error) {

                            console.error(
                                "COPY ERROR:",
                                error
                            );


                            alert(
                                "Unable to copy code."
                            );

                        }

                    }
                );


                /* =========================================
                   DELETE BUTTON
                   ========================================= */

                const deleteButton =
                    document.createElement(
                        "button"
                    );


                deleteButton.type =
                    "button";


                deleteButton.className =
                    "delete-code-btn";


                deleteButton.innerHTML =
                    '<i class="fa-regular fa-trash-can"></i> Delete';


                deleteButton.addEventListener(
                    "click",
                    function () {

                        showDeleteModal(
                            item
                        );

                    }
                );


                /* =========================================
                   APPEND ACTIONS
                   ========================================= */

                actions.appendChild(
                    copyButton
                );


                actions.appendChild(
                    deleteButton
                );


                /* =========================================
                   APPEND FOOTER
                   ========================================= */

                footer.appendChild(
                    date
                );


                footer.appendChild(
                    actions
                );


                /* =========================================
                   APPEND CARD
                   ========================================= */

                card.appendChild(
                    header
                );


                card.appendChild(
                    preview
                );


                card.appendChild(
                    footer
                );


                savedList.appendChild(
                    card
                );

            }
        );

    }


    /* =====================================================
       DELETE MODAL
       ===================================================== */

    function showDeleteModal(
        item
    ) {

        const oldModal =
            document.getElementById(
                "dynamicDeleteModal"
            );


        if (oldModal) {

            oldModal.remove();

        }


        /* =============================================
           OVERLAY
           ============================================= */

        const overlay =
            document.createElement(
                "div"
            );


        overlay.className =
            "modal-overlay show";


        overlay.id =
            "dynamicDeleteModal";


        /* =============================================
           MODAL
           ============================================= */

        const modal =
            document.createElement(
                "div"
            );


        modal.className =
            "confirmation-modal";


        modal.innerHTML = `

            <div class="modal-icon">

                <i class="fa-solid fa-trash"></i>

            </div>


            <h3>
                Delete Saved Code?
            </h3>


            <p>
                Are you sure you want to delete
                <strong>
                    ${escapeHtml(
                        item.filename ||
                        "this code"
                    )}
                </strong>?
            </p>


            <div class="modal-actions">

                <button
                    type="button"
                    class="modal-cancel"
                    id="cancelDeleteCode">

                    Cancel

                </button>


                <button
                    type="button"
                    class="modal-confirm"
                    id="confirmDeleteCode">

                    Delete

                </button>

            </div>

        `;


        overlay.appendChild(
            modal
        );


        document.body.appendChild(
            overlay
        );


        /* =============================================
           BUTTONS
           ============================================= */

        const cancelButton =
            document.getElementById(
                "cancelDeleteCode"
            );


        const confirmButton =
            document.getElementById(
                "confirmDeleteCode"
            );


        /* =============================================
           CANCEL
           ============================================= */

        if (cancelButton) {

            cancelButton.addEventListener(
                "click",
                function () {

                    overlay.remove();

                }
            );

        }


        /* =============================================
           CLICK OUTSIDE
           ============================================= */

        overlay.addEventListener(
            "click",
            function (event) {

                if (
                    event.target ===
                    overlay
                ) {

                    overlay.remove();

                }

            }
        );


        /* =============================================
           CONFIRM DELETE
           ============================================= */

        if (confirmButton) {

            confirmButton.addEventListener(
                "click",
                async function () {

                    confirmButton.disabled =
                        true;


                    confirmButton.textContent =
                        "Deleting...";


                    try {

                        const response =
                            await fetch(
                                `/api/saved-code/${item.id}`,
                                {
                                    method:
                                        "DELETE",

                                    headers: {
                                        "Accept":
                                            "application/json"
                                    }
                                }
                            );


                        const data =
                            await response.json();


                        if (
                            !response.ok ||
                            !data.success
                        ) {

                            alert(
                                data.message ||
                                "Unable to delete saved code."
                            );


                            confirmButton.disabled =
                                false;


                            confirmButton.textContent =
                                "Delete";


                            return;

                        }


                        overlay.remove();


                        await loadSavedCode();


                    } catch (error) {

                        console.error(
                            "DELETE ERROR:",
                            error
                        );


                        alert(
                            "Unable to connect to the server."
                        );


                        confirmButton.disabled =
                            false;


                        confirmButton.textContent =
                            "Delete";

                    }

                }
            );

        }

    }


    /* =====================================================
       ESCAPE HTML
       ===================================================== */

    function escapeHtml(
        value
    ) {

        return String(value)

            .replace(
                /&/g,
                "&amp;"
            )

            .replace(
                /</g,
                "&lt;"
            )

            .replace(
                />/g,
                "&gt;"
            )

            .replace(
                /"/g,
                "&quot;"
            )

            .replace(
                /'/g,
                "&#039;"
            );

    }


    /* =====================================================
       SAVED SEARCH
       ===================================================== */

    if (savedSearch) {

        savedSearch.addEventListener(
            "input",
            function () {

                const value =
                    savedSearch.value;


                /*
                 * Keep header search synchronized.
                 */

                if (globalSearch) {

                    globalSearch.value =
                        value;

                }


                renderSavedCode();

            }
        );


        savedSearch.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key ===
                    "Enter"
                ) {

                    event.preventDefault();

                    renderSavedCode();

                }

            }
        );

    }


    /* =====================================================
       LANGUAGE FILTER
       ===================================================== */

    if (languageFilter) {

        languageFilter.addEventListener(
            "change",
            function () {

                renderSavedCode();

            }
        );

    }


    /* =====================================================
       GLOBAL SEARCH
       ===================================================== */

    if (globalSearch) {

        globalSearch.addEventListener(
            "input",
            function () {

                const value =
                    globalSearch.value;


                if (savedSearch) {

                    savedSearch.value =
                        value;

                }


                renderSavedCode();

            }
        );


        globalSearch.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key ===
                    "Enter"
                ) {

                    event.preventDefault();

                    renderSavedCode();

                }

            }
        );

    }


    /* =====================================================
       NEW CODE
       ===================================================== */

    if (newCodeButton) {

        newCodeButton.addEventListener(
            "click",
            function () {

                window.location.href =
                    "/analyze";

            }
        );

    }


    /* =====================================================
       LOGOUT
       ===================================================== */

    if (
        logoutButton &&
        logoutModal
    ) {

        logoutButton.addEventListener(
            "click",
            function () {

                logoutModal.classList.add(
                    "show"
                );

            }
        );

    }


    /* =====================================================
       CANCEL LOGOUT
       ===================================================== */

    if (
        cancelLogout &&
        logoutModal
    ) {

        cancelLogout.addEventListener(
            "click",
            function () {

                logoutModal.classList.remove(
                    "show"
                );

            }
        );

    }


    /* =====================================================
       CLOSE LOGOUT MODAL OUTSIDE
       ===================================================== */

    if (logoutModal) {

        logoutModal.addEventListener(
            "click",
            function (event) {

                if (
                    event.target ===
                    logoutModal
                ) {

                    logoutModal.classList.remove(
                        "show"
                    );

                }

            }
        );

    }


    /* =====================================================
       CONFIRM LOGOUT
       ===================================================== */

    if (
        confirmLogout &&
        logoutForm
    ) {

        confirmLogout.addEventListener(
            "click",
            function () {

                logoutForm.submit();

            }
        );

    }


    /* =====================================================
       ESC KEY
       ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key ===
                "Escape"
            ) {

                if (logoutModal) {

                    logoutModal.classList.remove(
                        "show"
                    );

                }


                const deleteModal =
                    document.getElementById(
                        "dynamicDeleteModal"
                    );


                if (deleteModal) {

                    deleteModal.remove();

                }

            }

        }
    );


    /* =====================================================
       INITIAL LOAD
       ===================================================== */

    loadSavedCode();

});