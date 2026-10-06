/* =========================================================
   CODELENS - GLOBAL THEME
   Applies Dark / Light theme to ALL PAGES
   ========================================================= */

(function () {
    "use strict";

    const THEME_KEY = "codeLensTheme";

    /* =====================================================
       APPLY THEME
       ===================================================== */

    function applyTheme(theme) {

        if (theme !== "light" && theme !== "dark") {
            theme = "dark";
        }

        document.documentElement.setAttribute(
            "data-theme",
            theme
        );

        localStorage.setItem(
            THEME_KEY,
            theme
        );

        /* Update all dark mode toggles on current page */
        const toggles = document.querySelectorAll(
            "#darkModeToggle"
        );

        toggles.forEach(function (toggle) {
            toggle.checked = theme === "dark";
        });
    }


    /* =====================================================
       GET SAVED THEME
       ===================================================== */

    function getSavedTheme() {

        const savedTheme =
            localStorage.getItem(THEME_KEY);

        if (
            savedTheme === "light" ||
            savedTheme === "dark"
        ) {
            return savedTheme;
        }

        return "dark";
    }


    /* =====================================================
       APPLY BEFORE PAGE LOAD
       ===================================================== */

    const initialTheme = getSavedTheme();

    document.documentElement.setAttribute(
        "data-theme",
        initialTheme
    );


    /* =====================================================
       GLOBAL THEME FUNCTION
       ===================================================== */

    window.setCodeLensTheme = function (theme) {
        applyTheme(theme);
    };


    /* =====================================================
       INITIALIZE AFTER DOM LOAD
       ===================================================== */

    document.addEventListener(
        "DOMContentLoaded",
        function () {

            const currentTheme =
                document.documentElement.getAttribute(
                    "data-theme"
                ) || "dark";

            applyTheme(currentTheme);


            /* =============================================
               DARK MODE TOGGLE
               ============================================= */

            const darkModeToggle =
                document.getElementById(
                    "darkModeToggle"
                );

            if (darkModeToggle) {

                darkModeToggle.checked =
                    currentTheme === "dark";

                darkModeToggle.addEventListener(
                    "change",
                    function () {

                        if (darkModeToggle.checked) {

                            applyTheme("dark");

                        } else {

                            applyTheme("light");

                        }
                    }
                );
            }

        }
    );

})();

/* =========================================================
   CODELENS GLOBAL FONT SIZE
   SMALL / MEDIUM / LARGE
   ========================================================= */

(function () {
    "use strict";

    const THEME_KEY = "codeLensTheme";
    const FONT_SIZE_KEY = "codeLensFontSize";

    /* =========================
       THEME
    ========================= */

    function applyTheme(theme) {
        if (theme !== "light" && theme !== "dark") {
            theme = "dark";
        }

        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem(THEME_KEY, theme);

        document.querySelectorAll("#darkModeToggle").forEach(toggle => {
            toggle.checked = theme === "dark";
        });
    }

    function getSavedTheme() {
        const theme = localStorage.getItem(THEME_KEY);

        if (theme === "light" || theme === "dark") {
            return theme;
        }

        return "dark";
    }


    /* =========================
       FONT SIZE
    ========================= */

    function applyFontSize(size) {

        if (!["small", "medium", "large"].includes(size)) {
            size = "medium";
        }

        document.documentElement.setAttribute(
            "data-font-size",
            size
        );

        localStorage.setItem(
            FONT_SIZE_KEY,
            size
        );

        document.querySelectorAll("#fontSizeSelect").forEach(select => {
            select.value = size;
        });
    }


    function getSavedFontSize() {

        const size = localStorage.getItem(
            FONT_SIZE_KEY
        );

        if (
            size === "small" ||
            size === "medium" ||
            size === "large"
        ) {
            return size;
        }

        return "medium";
    }


    /* =========================
       GLOBAL FUNCTIONS
    ========================= */

    window.setCodeLensTheme = function (theme) {
        applyTheme(theme);

        window.dispatchEvent(
            new CustomEvent(
                "codeLensThemeChanged",
                {
                    detail: {
                        theme: theme
                    }
                }
            )
        );
    };


    window.getCodeLensTheme = function () {
        return document.documentElement.getAttribute(
            "data-theme"
        ) || getSavedTheme();
    };


    window.setCodeLensFontSize = function (size) {

        applyFontSize(size);

        window.dispatchEvent(
            new CustomEvent(
                "codeLensFontSizeChanged",
                {
                    detail: {
                        fontSize: size
                    }
                }
            )
        );
    };


    window.getCodeLensFontSize = function () {

        return document.documentElement.getAttribute(
            "data-font-size"
        ) || getSavedFontSize();
    };


    /* =========================
       APPLY BEFORE PAGE LOAD
    ========================= */

    const savedTheme = getSavedTheme();
    const savedFontSize = getSavedFontSize();

    document.documentElement.setAttribute(
        "data-theme",
        savedTheme
    );

    document.documentElement.setAttribute(
        "data-font-size",
        savedFontSize
    );


    /* =========================
       DOM READY
    ========================= */

    document.addEventListener(
        "DOMContentLoaded",
        function () {

            applyTheme(getSavedTheme());
            applyFontSize(getSavedFontSize());


            /* FONT DROPDOWN */

            document.querySelectorAll(
                "#fontSizeSelect"
            ).forEach(select => {

                select.value =
                    getSavedFontSize();

                select.addEventListener(
                    "change",
                    function () {

                        window.setCodeLensFontSize(
                            this.value
                        );

                    }
                );

            });


            /* DARK MODE */

            document.querySelectorAll(
                "#darkModeToggle"
            ).forEach(toggle => {

                toggle.checked =
                    getSavedTheme() === "dark";

                toggle.addEventListener(
                    "change",
                    function () {

                        window.setCodeLensTheme(
                            this.checked
                                ? "dark"
                                : "light"
                        );

                    }
                );

            });

        }
    );

})();