document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       SIDEBAR TOGGLE
    ====================================================== */

    const sidebar =
        document.getElementById("sidebar");

    const sidebarToggle =
        document.getElementById("sidebarToggle");


    if (sidebar && sidebarToggle) {

        sidebarToggle.addEventListener(
            "click",
            function () {

                sidebar.classList.toggle("collapsed");

            }
        );

    }



    /* =====================================================
       PASSWORD CHANGE TOGGLE
    ====================================================== */

    const changePasswordButton =
        document.getElementById(
            "changePasswordButton"
        );

    const changePasswordPanel =
        document.getElementById(
            "changePasswordPanel"
        );

    const passwordArrow =
        document.getElementById(
            "passwordArrow"
        );


    if (
        changePasswordButton &&
        changePasswordPanel &&
        passwordArrow
    ) {

        changePasswordButton.addEventListener(
            "click",
            function () {

                const isOpen =
                    changePasswordPanel.classList.contains(
                        "open"
                    );


                if (isOpen) {

                    changePasswordPanel.classList.remove(
                        "open"
                    );

                    passwordArrow.classList.remove(
                        "fa-chevron-up"
                    );

                    passwordArrow.classList.add(
                        "fa-chevron-down"
                    );

                } else {

                    changePasswordPanel.classList.add(
                        "open"
                    );

                    passwordArrow.classList.remove(
                        "fa-chevron-down"
                    );

                    passwordArrow.classList.add(
                        "fa-chevron-up"
                    );

                }

            }
        );

    }



    /* =====================================================
       FONT SIZE
    ====================================================== */

    const fontSizeSelect =
        document.getElementById(
            "fontSizeSelect"
        );


    if (fontSizeSelect) {

        const savedFontSize =
            localStorage.getItem(
                "codeLensFontSize"
            ) || "medium";


        fontSizeSelect.value =
            savedFontSize;


        applyFontSize(
            savedFontSize
        );


        fontSizeSelect.addEventListener(
            "change",
            function () {

                const selectedSize =
                    fontSizeSelect.value;


                localStorage.setItem(
                    "codeLensFontSize",
                    selectedSize
                );


                applyFontSize(
                    selectedSize
                );

            }
        );

    }


    function applyFontSize(size) {

        document.documentElement.classList.remove(
            "font-small",
            "font-medium",
            "font-large"
        );


        if (size === "small") {

            document.documentElement.classList.add(
                "font-small"
            );

        } else if (size === "large") {

            document.documentElement.classList.add(
                "font-large"
            );

        } else {

            document.documentElement.classList.add(
                "font-medium"
            );

        }

    }



    /* =====================================================
       DARK MODE
    ====================================================== */

    const darkModeToggle =
        document.getElementById(
            "darkModeToggle"
        );


    if (darkModeToggle) {

        const currentTheme =
            localStorage.getItem(
                "codeLensTheme"
            ) || "dark";


        darkModeToggle.checked =
            currentTheme === "dark";


        darkModeToggle.addEventListener(
            "change",
            function () {

                const selectedTheme =
                    darkModeToggle.checked
                        ? "dark"
                        : "light";


                if (window.setCodeLensTheme) {

                    window.setCodeLensTheme(
                        selectedTheme
                    );

                } else {

                    document.documentElement.setAttribute(
                        "data-theme",
                        selectedTheme
                    );


                    localStorage.setItem(
                        "codeLensTheme",
                        selectedTheme
                    );

                }

            }
        );

    }



    /* =====================================================
       AUTO SAVE
    ====================================================== */

    const autoSaveToggle =
        document.getElementById(
            "autoSaveToggle"
        );

    const AUTO_SAVE_KEY =
        "autoSaveCode";


    if (autoSaveToggle) {

        const savedAutoSave =
            localStorage.getItem(
                AUTO_SAVE_KEY
            );


        if (savedAutoSave === null) {

            autoSaveToggle.checked = true;

            localStorage.setItem(
                AUTO_SAVE_KEY,
                "true"
            );

        } else {

            autoSaveToggle.checked =
                savedAutoSave === "true";

        }


        autoSaveToggle.addEventListener(
            "change",
            function () {

                const enabled =
                    autoSaveToggle.checked;


                localStorage.setItem(
                    AUTO_SAVE_KEY,
                    enabled
                        ? "true"
                        : "false"
                );


                console.log(
                    "Auto Save:",
                    enabled
                        ? "ON"
                        : "OFF"
                );

            }
        );

    }



    /* =====================================================
       LOGOUT MODAL
    ====================================================== */

    const logoutButton =
        document.getElementById(
            "logoutButton"
        );

    const logoutModal =
        document.getElementById(
            "logoutModal"
        );

    const cancelLogout =
        document.getElementById(
            "cancelLogout"
        );

    const confirmLogout =
        document.getElementById(
            "confirmLogout"
        );

    const logoutForm =
        document.getElementById(
            "logoutForm"
        );


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
       DELETE ACCOUNT MODAL
    ====================================================== */

    const deleteAccountButton =
        document.getElementById(
            "deleteAccountButton"
        );

    const deleteAccountModal =
        document.getElementById(
            "deleteAccountModal"
        );

    const cancelDeleteAccount =
        document.getElementById(
            "cancelDeleteAccount"
        );

    const confirmDeleteAccount =
        document.getElementById(
            "confirmDeleteAccount"
        );


    if (
        deleteAccountButton &&
        deleteAccountModal
    ) {

        deleteAccountButton.addEventListener(
            "click",
            function () {

                deleteAccountModal.classList.add(
                    "show"
                );

            }
        );

    }


    if (
        cancelDeleteAccount &&
        deleteAccountModal
    ) {

        cancelDeleteAccount.addEventListener(
            "click",
            function () {

                deleteAccountModal.classList.remove(
                    "show"
                );

            }
        );

    }


    if (deleteAccountModal) {

        deleteAccountModal.addEventListener(
            "click",
            function (event) {

                if (
                    event.target ===
                    deleteAccountModal
                ) {

                    deleteAccountModal.classList.remove(
                        "show"
                    );

                }

            }
        );

    }


    if (confirmDeleteAccount) {

        confirmDeleteAccount.addEventListener(
            "click",
            async function () {

                confirmDeleteAccount.disabled =
                    true;

                confirmDeleteAccount.textContent =
                    "Deleting...";


                try {

                    const response =
                        await fetch(
                            "/api/profile/delete-account",
                            {
                                method: "POST",
                                headers: {
                                    "Content-Type":
                                        "application/json",
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

                        throw new Error(
                            data.message ||
                            "Unable to delete account."
                        );

                    }


                    localStorage.clear();
                    sessionStorage.clear();


                    window.location.href =
                        "/login";

                }
                catch (error) {

                    console.error(
                        "DELETE ACCOUNT ERROR:",
                        error
                    );


                    confirmDeleteAccount.disabled =
                        false;

                    confirmDeleteAccount.textContent =
                        "Delete Account";

                    alert(
                        error.message ||
                        "Unable to delete account."
                    );

                }

            }
        );

    }



    /* =====================================================
       CLEAR ANALYSIS HISTORY
    ====================================================== */

    const clearHistoryButton =
        document.getElementById(
            "clearHistoryButton"
        );

    const clearHistoryModal =
        document.getElementById(
            "clearHistoryModal"
        );

    const cancelClearHistory =
        document.getElementById(
            "cancelClearHistory"
        );

    const confirmClearHistory =
        document.getElementById(
            "confirmClearHistory"
        );


    /* =====================================================
       OPEN CLEAR HISTORY POPUP
    ====================================================== */

    if (
        clearHistoryButton &&
        clearHistoryModal
    ) {

        clearHistoryButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                clearHistoryModal.classList.add(
                    "show"
                );

            }
        );

    }



    /* =====================================================
       CANCEL CLEAR HISTORY
    ====================================================== */

    if (
        cancelClearHistory &&
        clearHistoryModal
    ) {

        cancelClearHistory.addEventListener(
            "click",
            function () {

                clearHistoryModal.classList.remove(
                    "show"
                );

            }
        );

    }



    /* =====================================================
       CLOSE CLEAR HISTORY OUTSIDE
    ====================================================== */

    if (clearHistoryModal) {

        clearHistoryModal.addEventListener(
            "click",
            function (event) {

                if (
                    event.target ===
                    clearHistoryModal
                ) {

                    clearHistoryModal.classList.remove(
                        "show"
                    );

                }

            }
        );

    }



    /* =====================================================
       CONFIRM CLEAR HISTORY
    ====================================================== */

    if (confirmClearHistory) {

        confirmClearHistory.addEventListener(
            "click",
            async function () {

                const originalText =
                    confirmClearHistory.textContent;


                confirmClearHistory.disabled =
                    true;


                confirmClearHistory.textContent =
                    "Clearing...";


                try {

                    const response =
                        await fetch(
                            "/api/profile/clear-history",
                            {
                                method: "POST",
                                headers: {
                                    "Content-Type":
                                        "application/json",
                                    "Accept":
                                        "application/json"
                                }
                            }
                        );


                    const contentType =
                        response.headers.get(
                            "content-type"
                        ) || "";


                    let data = null;


                    if (
                        contentType.includes(
                            "application/json"
                        )
                    ) {

                        data =
                            await response.json();

                    }


                    if (
                        !response.ok ||
                        !data ||
                        !data.success
                    ) {

                        throw new Error(
                            data &&
                            data.message
                                ? data.message
                                : "Unable to clear history."
                        );

                    }



                    /* =================================
                       CLEAR ANALYZE DATA
                    ================================= */

                    localStorage.removeItem(
                        "codeLensAnalyzeCode"
                    );

                    localStorage.removeItem(
                        "codeLensAnalyzeLanguage"
                    );

                    localStorage.removeItem(
                        "codeLensAnalyzeFilename"
                    );

                    localStorage.removeItem(
                        "codeLensAnalyzeSource"
                    );

                    localStorage.removeItem(
                        "analysisId"
                    );



                    /* =================================
                       CLEAR SAVED CODE LOCAL DATA
                    ================================= */

                    localStorage.removeItem(
                        "codeLensSavedCodes"
                    );



                    /* =================================
                       CLEAR SESSION ANALYSIS DATA
                    ================================= */

                    sessionStorage.removeItem(
                        "codeLensAnalysisCode"
                    );

                    sessionStorage.removeItem(
                        "codeLensAnalysisLanguage"
                    );

                    sessionStorage.removeItem(
                        "codeLensAnalysisFilename"
                    );

                    sessionStorage.removeItem(
                        "codeLensAnalysisSource"
                    );

                    sessionStorage.removeItem(
                        "analysisId"
                    );



                    /* =================================
                       CLOSE POPUP
                    ================================= */

                    if (clearHistoryModal) {

                        clearHistoryModal.classList.remove(
                            "show"
                        );

                    }



                    /*
                     * IMPORTANT:
                     * NO SUCCESS ALERT
                     */

                    window.location.reload();

                }
                catch (error) {

                    console.error(
                        "CLEAR HISTORY ERROR:",
                        error
                    );


                    confirmClearHistory.disabled =
                        false;


                    confirmClearHistory.textContent =
                        originalText;



                    /* =================================
                       SHOW ERROR INSIDE POPUP
                    ================================= */

                    if (clearHistoryModal) {

                        const message =
                            clearHistoryModal.querySelector(
                                ".confirmation-modal p"
                            );


                        if (message) {

                            message.textContent =
                                error.message ||
                                "Unable to clear history.";

                        }

                    }

                }

            }
        );

    }



    /* =====================================================
       SEARCH
    ====================================================== */

    const searchInput =
        document.getElementById(
            "profileSearch"
        );


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            function () {

                const value =
                    searchInput.value
                        .toLowerCase()
                        .trim();


                const cards =
                    document.querySelectorAll(
                        ".profile-card"
                    );


                cards.forEach(
                    function (card) {

                        const text =
                            card.textContent
                                .toLowerCase();


                        if (
                            value === "" ||
                            text.includes(value)
                        ) {

                            card.style.display =
                                "";

                        } else {

                            card.style.display =
                                "none";

                        }

                    }
                );

            }
        );

    }



    /* =====================================================
       SAVE PASSWORD
    ====================================================== */

    const savePasswordButton =
        document.getElementById(
            "savePasswordButton"
        );


    if (savePasswordButton) {

        savePasswordButton.addEventListener(
            "click",
            async function () {

                const currentPassword =
                    document.getElementById(
                        "currentPassword"
                    );

                const newPassword =
                    document.getElementById(
                        "newPassword"
                    );

                const confirmPassword =
                    document.getElementById(
                        "confirmPassword"
                    );


                if (
                    !currentPassword ||
                    !newPassword ||
                    !confirmPassword
                ) {

                    return;

                }


                if (
                    currentPassword.value.trim() === ""
                ) {

                    alert(
                        "Please enter your current password."
                    );

                    currentPassword.focus();

                    return;

                }


                if (
                    newPassword.value.trim() === ""
                ) {

                    alert(
                        "Please enter your new password."
                    );

                    newPassword.focus();

                    return;

                }


                if (
                    confirmPassword.value.trim() === ""
                ) {

                    alert(
                        "Please confirm your new password."
                    );

                    confirmPassword.focus();

                    return;

                }


                if (
                    newPassword.value !==
                    confirmPassword.value
                ) {

                    alert(
                        "New password and confirm password do not match."
                    );

                    confirmPassword.focus();

                    return;

                }


                try {

                    savePasswordButton.disabled =
                        true;


                    savePasswordButton.textContent =
                        "Saving...";


                    const response =
                        await fetch(
                            "/api/profile/password",
                            {
                                method: "POST",
                                headers: {
                                    "Content-Type":
                                        "application/json",
                                    "Accept":
                                        "application/json"
                                },
                                body: JSON.stringify({
                                    current_password:
                                        currentPassword.value,
                                    new_password:
                                        newPassword.value
                                })
                            }
                        );


                    const data =
                        await response.json();


                    if (
                        !response.ok ||
                        !data.success
                    ) {

                        throw new Error(
                            data.message ||
                            "Unable to change password."
                        );

                    }


                    currentPassword.value = "";
                    newPassword.value = "";
                    confirmPassword.value = "";


                    alert(
                        data.message ||
                        "Password changed successfully."
                    );

                }
                catch (error) {

                    console.error(
                        "PASSWORD CHANGE ERROR:",
                        error
                    );


                    alert(
                        error.message ||
                        "Unable to change password."
                    );

                }
                finally {

                    savePasswordButton.disabled =
                        false;


                    savePasswordButton.textContent =
                        "Save Changes";

                }

            }
        );

    }



    /* =====================================================
       ESCAPE KEY
    ====================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key !== "Escape"
            ) {

                return;

            }


            /* Logout */

            if (
                logoutModal &&
                logoutModal.classList.contains(
                    "show"
                )
            ) {

                logoutModal.classList.remove(
                    "show"
                );

            }


            /* Delete account */

            if (
                deleteAccountModal &&
                deleteAccountModal.classList.contains(
                    "show"
                )
            ) {

                deleteAccountModal.classList.remove(
                    "show"
                );

            }


            /* Clear history */

            if (
                clearHistoryModal &&
                clearHistoryModal.classList.contains(
                    "show"
                )
            ) {

                clearHistoryModal.classList.remove(
                    "show"
                );

            }

        }
    );

});