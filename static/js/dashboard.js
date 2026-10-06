/* =========================================================
   CODELENS - DASHBOARD JS
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    "use strict";


    /* =====================================================
       SIDEBAR
       ===================================================== */

    const sidebarToggle =
        document.getElementById("sidebarToggle");

    const sidebar =
        document.querySelector(".sidebar");


    if (sidebarToggle && sidebar) {

        sidebarToggle.addEventListener("click", function () {

            sidebar.classList.toggle("collapsed");

        });

    }


    /* =====================================================
       LOGOUT MODAL
       ===================================================== */

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


    function openLogoutModal() {

        if (logoutModal) {
            logoutModal.classList.add("show");
        }

    }


    function closeLogoutModal() {

        if (logoutModal) {
            logoutModal.classList.remove("show");
        }

    }


    if (logoutButton) {

        logoutButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                openLogoutModal();

            }
        );

    }


    if (cancelLogout) {

        cancelLogout.addEventListener(
            "click",
            function () {

                closeLogoutModal();

            }
        );

    }


    if (confirmLogout) {

        confirmLogout.addEventListener(
            "click",
            function () {

                if (logoutForm) {

                    logoutForm.submit();

                } else {

                    window.location.href = "/logout";

                }

            }
        );

    }


    if (logoutModal) {

        logoutModal.addEventListener(
            "click",
            function (event) {

                if (event.target === logoutModal) {

                    closeLogoutModal();

                }

            }
        );

    }


    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                closeLogoutModal();

            }

        }
    );


    /* =====================================================
       DASHBOARD SEARCH
       ===================================================== */

    const globalSearch =
        document.getElementById("globalSearch");

    const dashboardSearch =
        document.getElementById("dashboardSearch");

    const searchInput =
        globalSearch || dashboardSearch;


    let searchMessage = null;


    function getDashboardSearchTargets() {

        return Array.from(
            document.querySelectorAll(
                ".dashboard-content .stat-card, " +
                ".dashboard-content .analyze-card, " +
                ".dashboard-content .recent-card, " +
                ".dashboard-content .quality-card"
            )
        );

    }


    function createSearchMessage() {

        if (searchMessage) {
            return searchMessage;
        }


        searchMessage =
            document.createElement("div");

        searchMessage.className =
            "dashboard-search-message";

        searchMessage.style.display =
            "none";

        searchMessage.style.margin =
            "0 0 16px 0";

        searchMessage.style.fontSize =
            "15px";

        searchMessage.style.color =
            "var(--muted, #999)";

        return searchMessage;

    }


    function placeSearchMessage(message) {

        const mainContent =
            document.querySelector(
                ".dashboard-content"
            );


        if (!mainContent) {
            return;
        }


        let titleContainer = null;


        const pageTitle =
            mainContent.querySelector(
                ".welcome-section h1"
            );


        if (pageTitle) {

            titleContainer = pageTitle;


            while (
                titleContainer.parentElement &&
                titleContainer.parentElement !== mainContent
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

                return;

            }

        }


        if (message.parentElement !== mainContent) {

            mainContent.insertBefore(
                message,
                mainContent.firstElementChild
            );

        }

    }


    function getSearchKeywords(text) {

        text =
            text.toLowerCase();

        let keywords = "";


        if (text.includes("total analyses")) {

            keywords =
                "analysis analyses analyze";

        }

        else if (text.includes("issues found")) {

            keywords =
                "issues issue problems violations";

        }

        else if (text.includes("reports")) {

            keywords =
                "report reports generate";

        }

        else if (text.includes("saved code")) {

            keywords =
                "saved save code";

        }

        else if (text.includes("recent analyses")) {

            keywords =
                "recent analysis analyses history results";

        }

        else if (text.includes("code quality")) {

            keywords =
                "quality code maintainability reliability security readability review";

        }

        else {

            keywords = text;

        }


        return keywords;

    }


    function performDashboardSearch() {

        if (!searchInput) {
            return;
        }


        const query =
            searchInput.value
                .trim()
                .toLowerCase();


        const targets =
            getDashboardSearchTargets();


        const message =
            createSearchMessage();


        placeSearchMessage(message);


        if (!query) {

            targets.forEach(function (target) {

                target.style.display = "";

            });


            message.style.display =
                "none";

            return;

        }


        message.textContent =
            'Search results for "' +
            searchInput.value.trim() +
            '"';


        message.style.display =
            "block";


        let matchCount = 0;


        targets.forEach(function (target) {

            const text =
                target.textContent
                    .toLowerCase();


            const keywords =
                getSearchKeywords(text);


            const isMatch =
                text.includes(query) ||
                keywords.includes(query);


            if (isMatch) {

                target.style.display =
                    "";

                matchCount++;

            } else {

                target.style.display =
                    "none";

            }

        });


        if (matchCount === 0) {

            message.textContent =
                'No results found for "' +
                searchInput.value.trim() +
                '"';

        }

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            performDashboardSearch
        );


        searchInput.addEventListener(
            "keyup",
            performDashboardSearch
        );

    }


    /* =====================================================
       GENERATE REPORT
       ===================================================== */

    const generateReportButton =
        document.querySelector(
            ".generate-report-btn"
        );


    if (generateReportButton) {

        generateReportButton.addEventListener(
            "click",
            function () {

                window.location.href =
                    "/reports";

            }
        );

    }


    /* =====================================================
       THEME DETECTION
       ===================================================== */

    function isLightMode() {

        const body =
            document.body;

        const html =
            document.documentElement;


        /* -----------------------------------------------
           Common class names
        ------------------------------------------------ */

        if (
            body.classList.contains("light-mode") ||
            body.classList.contains("light-theme") ||
            html.classList.contains("light-mode") ||
            html.classList.contains("light-theme")
        ) {

            return true;

        }


        /* -----------------------------------------------
           Data theme
        ------------------------------------------------ */

        const bodyTheme =
            body.getAttribute("data-theme");

        const htmlTheme =
            html.getAttribute("data-theme");


        if (
            bodyTheme === "light" ||
            htmlTheme === "light"
        ) {

            return true;

        }


        if (
            bodyTheme === "dark" ||
            htmlTheme === "dark"
        ) {

            return false;

        }


        /* -----------------------------------------------
           CSS class used by some theme systems
        ------------------------------------------------ */

        if (
            body.classList.contains("dark-blue-ui")
        ) {

            /*
             * dark-blue-ui alone does not always mean
             * dark mode because the theme system may
             * override it.
             *
             * Continue checking localStorage below.
             */

        }


        /* -----------------------------------------------
           LocalStorage theme detection
        ------------------------------------------------ */

        const storedTheme =
            localStorage.getItem("theme") ||
            localStorage.getItem("codeLensTheme") ||
            localStorage.getItem("selectedTheme");


        if (
            storedTheme === "light" ||
            storedTheme === "light-mode"
        ) {

            return true;

        }


        if (
            storedTheme === "dark" ||
            storedTheme === "dark-mode"
        ) {

            return false;

        }


        /* -----------------------------------------------
           CSS variable fallback
        ------------------------------------------------ */

        const bgColor =
            getComputedStyle(body)
                .getPropertyValue("--bg")
                .trim()
                .toLowerCase();


        if (
            bgColor === "#ffffff" ||
            bgColor === "#fff" ||
            bgColor === "white" ||
            bgColor === "rgb(255, 255, 255)"
        ) {

            return true;

        }


        /* -----------------------------------------------
           Default
        ------------------------------------------------ */

        return false;

    }


    /* =====================================================
       RECENT ANALYSES THEME STYLE
       ===================================================== */

    function applyRecentAnalysesTheme() {

        const table =
            document.querySelector(
                ".analysis-table"
            );


        if (!table) {
            return;
        }


        const light =
            isLightMode();


        /* =================================================
           COLORS
        ================================================= */

        const colors = light

            ? {

                tableBackground:
                    "#ffffff",

                rowBackground:
                    "#ffffff",

                hoverBackground:
                    "#f5f8ff",

                primaryText:
                    "#172033",

                secondaryText:
                    "#475569",

                mutedText:
                    "#64748b",

                border:
                    "#e2e8f0",

                icon:
                    "#7149ef",

                issueText:
                    "#dc2626",

                issueBackground:
                    "#fee2e2",

                issueBorder:
                    "#fecaca"

            }

            : {

                tableBackground:
                    "#101c2f",

                rowBackground:
                    "#101c2f",

                hoverBackground:
                    "#172942",

                primaryText:
                    "#f1f5f9",

                secondaryText:
                    "#cbd5e1",

                mutedText:
                    "#94a3b8",

                border:
                    "#263b58",

                icon:
                    "#8b6cf6",

                issueText:
                    "#f87171",

                issueBackground:
                    "rgba(239, 68, 68, 0.14)",

                issueBorder:
                    "rgba(248, 113, 113, 0.35)"

            };


        /* =================================================
           TABLE
        ================================================= */

        table.style.setProperty(
            "background",
            colors.tableBackground,
            "important"
        );


        const tbody =
            table.querySelector("tbody");


        if (tbody) {

            tbody.style.setProperty(
                "background",
                colors.tableBackground,
                "important"
            );

        }


        /* =================================================
           ALL ROWS
        ================================================= */

        const rows =
            table.querySelectorAll(
                "tbody tr"
            );


        rows.forEach(function (row) {

            row.style.setProperty(
                "background",
                colors.rowBackground,
                "important"
            );


            row.style.setProperty(
                "color",
                colors.primaryText,
                "important"
            );


            row.style.setProperty(
                "border-color",
                colors.border,
                "important"
            );


            /* ---------------------------------------------
               CELLS
            --------------------------------------------- */

            const cells =
                row.querySelectorAll("td");


            cells.forEach(function (cell) {

                cell.style.setProperty(
                    "background",
                    colors.rowBackground,
                    "important"
                );


                cell.style.setProperty(
                    "color",
                    colors.primaryText,
                    "important"
                );


                cell.style.setProperty(
                    "border-color",
                    colors.border,
                    "important"
                );

            });


            /* ---------------------------------------------
               Filename
            --------------------------------------------- */

            const filename =
                row.querySelector(
                    ".recent-file-name span"
                );


            if (filename) {

                filename.style.setProperty(
                    "color",
                    colors.primaryText,
                    "important"
                );


                filename.style.setProperty(
                    "font-weight",
                    "600",
                    "important"
                );

            }


            /* ---------------------------------------------
               File icon
            --------------------------------------------- */

            const fileIcon =
                row.querySelector(
                    ".recent-file-name i"
                );


            if (fileIcon) {

                fileIcon.style.setProperty(
                    "color",
                    colors.icon,
                    "important"
                );

            }


            /* ---------------------------------------------
               Language
            --------------------------------------------- */

            if (cells[1]) {

                cells[1].style.setProperty(
                    "color",
                    colors.secondaryText,
                    "important"
                );

            }


            /* ---------------------------------------------
               Date
            --------------------------------------------- */

            if (cells[3]) {

                cells[3].style.setProperty(
                    "color",
                    colors.mutedText,
                    "important"
                );

            }


            /* ---------------------------------------------
               Issue Count
            --------------------------------------------- */

            const issueBadge =
                row.querySelector(
                    ".issue-count"
                );


            if (issueBadge) {

                issueBadge.style.setProperty(
                    "color",
                    colors.issueText,
                    "important"
                );


                issueBadge.style.setProperty(
                    "background",
                    colors.issueBackground,
                    "important"
                );


                issueBadge.style.setProperty(
                    "border",
                    "1px solid " +
                    colors.issueBorder,
                    "important"
                );

            }

        });


        /* =================================================
           EMPTY STATE
        ================================================= */

        const emptyState =
            table.querySelector(
                ".table-empty-state"
            );


        if (emptyState) {

            emptyState.style.setProperty(
                "background",
                colors.rowBackground,
                "important"
            );


            emptyState.style.setProperty(
                "color",
                colors.primaryText,
                "important"
            );


            const emptyTitle =
                emptyState.querySelector("h3");


            if (emptyTitle) {

                emptyTitle.style.setProperty(
                    "color",
                    colors.primaryText,
                    "important"
                );

            }


            const emptyText =
                emptyState.querySelector("p");


            if (emptyText) {

                emptyText.style.setProperty(
                    "color",
                    colors.mutedText,
                    "important"
                );

            }


            const emptyIcon =
                emptyState.querySelector(
                    ".table-empty-icon"
                );


            if (emptyIcon) {

                emptyIcon.style.setProperty(
                    "color",
                    colors.icon,
                    "important"
                );

            }

        }

    }


    /* =====================================================
       THEME STYLE OVERRIDE
       ===================================================== */

    function createRecentAnalysesThemeStyle() {

        const existing =
            document.getElementById(
                "codeLensRecentAnalysesThemeStyle"
            );


        if (existing) {

            existing.remove();

        }


        const style =
            document.createElement("style");


        style.id =
            "codeLensRecentAnalysesThemeStyle";


        style.textContent = `

            /* ==========================================
               RECENT ANALYSES - THEME SUPPORT
            ========================================== */

            .analysis-table tbody tr {
                transition:
                    background-color 0.2s ease,
                    color 0.2s ease;
            }


            .analysis-table tbody tr:hover {
                background: var(
                    --recent-row-hover,
                    #172942
                ) !important;
            }


            .analysis-table tbody tr:hover td {
                background: var(
                    --recent-row-hover,
                    #172942
                ) !important;
            }


            /* ------------------------------------------
               LIGHT MODE
            ------------------------------------------ */

            body.light-mode .analysis-table tbody tr,
            html.light-mode .analysis-table tbody tr,
            body.light-theme .analysis-table tbody tr,
            html.light-theme .analysis-table tbody tr {

                background:
                    #ffffff !important;

                color:
                    #172033 !important;

            }


            body.light-mode
            .analysis-table tbody tr td,
            html.light-mode
            .analysis-table tbody tr td,
            body.light-theme
            .analysis-table tbody tr td,
            html.light-theme
            .analysis-table tbody tr td {

                background:
                    #ffffff !important;

                color:
                    #172033 !important;

                border-color:
                    #e2e8f0 !important;

            }


            body.light-mode
            .analysis-table tbody tr:hover,
            html.light-mode
            .analysis-table tbody tr:hover,
            body.light-theme
            .analysis-table tbody tr:hover,
            html.light-theme
            .analysis-table tbody tr:hover {

                background:
                    #f5f8ff !important;

            }


            body.light-mode
            .analysis-table tbody tr:hover td,
            html.light-mode
            .analysis-table tbody tr:hover td,
            body.light-theme
            .analysis-table tbody tr:hover td,
            html.light-theme
            .analysis-table tbody tr:hover td {

                background:
                    #f5f8ff !important;

            }


            /* ------------------------------------------
               DARK MODE
            ------------------------------------------ */

            body.dark-mode .analysis-table tbody tr,
            html.dark-mode .analysis-table tbody tr,
            body.dark-theme .analysis-table tbody tr,
            html.dark-theme .analysis-table tbody tr,
            body.dark-blue-ui .analysis-table tbody tr,
            html.dark-blue-ui .analysis-table tbody tr {

                background:
                    #101c2f !important;

                color:
                    #f1f5f9 !important;

            }


            body.dark-mode
            .analysis-table tbody tr td,
            html.dark-mode
            .analysis-table tbody tr td,
            body.dark-theme
            .analysis-table tbody tr td,
            html.dark-theme
            .analysis-table tbody tr td,
            body.dark-blue-ui
            .analysis-table tbody tr td,
            html.dark-blue-ui
            .analysis-table tbody tr td {

                background:
                    #101c2f !important;

                color:
                    #f1f5f9 !important;

                border-color:
                    #263b58 !important;

            }


            body.dark-mode
            .analysis-table tbody tr:hover,
            html.dark-mode
            .analysis-table tbody tr:hover,
            body.dark-theme
            .analysis-table tbody tr:hover,
            html.dark-theme
            .analysis-table tbody tr:hover,
            body.dark-blue-ui
            .analysis-table tbody tr:hover,
            html.dark-blue-ui
            .analysis-table tbody tr:hover {

                background:
                    #172942 !important;

            }


            body.dark-mode
            .analysis-table tbody tr:hover td,
            html.dark-mode
            .analysis-table tbody tr:hover td,
            body.dark-theme
            .analysis-table tbody tr:hover td,
            html.dark-theme
            .analysis-table tbody tr:hover td,
            body.dark-blue-ui
            .analysis-table tbody tr:hover td,
            html.dark-blue-ui
            .analysis-table tbody tr:hover td {

                background:
                    #172942 !important;

            }


            /* ------------------------------------------
               FILENAME
            ------------------------------------------ */

            body.light-mode
            .recent-file-name span,
            html.light-mode
            .recent-file-name span,
            body.light-theme
            .recent-file-name span,
            html.light-theme
            .recent-file-name span {

                color:
                    #172033 !important;

            }


            body.dark-mode
            .recent-file-name span,
            html.dark-mode
            .recent-file-name span,
            body.dark-theme
            .recent-file-name span,
            html.dark-theme
            .recent-file-name span,
            body.dark-blue-ui
            .recent-file-name span,
            html.dark-blue-ui
            .recent-file-name span {

                color:
                    #f1f5f9 !important;

            }


            /* ------------------------------------------
               FILE ICON
            ------------------------------------------ */

            .recent-file-name i {

                color:
                    #7149ef !important;

            }


            /* ------------------------------------------
               ISSUE BADGE
            ------------------------------------------ */

            body.light-mode .issue-count,
            html.light-mode .issue-count,
            body.light-theme .issue-count,
            html.light-theme .issue-count {

                color:
                    #dc2626 !important;

                background:
                    #fee2e2 !important;

                border:
                    1px solid #fecaca !important;

            }


            body.dark-mode .issue-count,
            html.dark-mode .issue-count,
            body.dark-theme .issue-count,
            html.dark-theme .issue-count,
            body.dark-blue-ui .issue-count,
            html.dark-blue-ui .issue-count {

                color:
                    #f87171 !important;

                background:
                    rgba(239, 68, 68, 0.14) !important;

                border:
                    1px solid rgba(248, 113, 113, 0.35) !important;

            }

        `;


        document.head.appendChild(style);

    }


    createRecentAnalysesThemeStyle();


    /* =====================================================
       WATCH FOR THEME CHANGES
       ===================================================== */

    function watchThemeChanges() {

        const observer =
            new MutationObserver(
                function (mutations) {

                    let themeChanged = false;


                    mutations.forEach(
                        function (mutation) {

                            if (
                                mutation.type === "attributes" &&
                                (
                                    mutation.attributeName ===
                                    "class" ||
                                    mutation.attributeName ===
                                    "data-theme"
                                )
                            ) {

                                themeChanged = true;

                            }

                        }
                    );


                    if (themeChanged) {

                        setTimeout(
                            function () {

                                applyRecentAnalysesTheme();

                            },
                            10
                        );

                    }

                }
            );


        observer.observe(
            document.documentElement,
            {
                attributes: true
            }
        );


        observer.observe(
            document.body,
            {
                attributes: true
            }
        );

    }


    watchThemeChanges();


    /* =====================================================
       DASHBOARD API
       ===================================================== */

    function loadDashboardData() {

        fetch(
            "/api/dashboard-stats",
            {
                method: "GET",
                cache: "no-store"
            }
        )

        .then(function (response) {

            console.log(
                "Dashboard API status:",
                response.status
            );


            if (!response.ok) {

                throw new Error(
                    "Dashboard API failed: HTTP " +
                    response.status
                );

            }


            return response.json();

        })


        .then(function (data) {

            console.log(
                "Dashboard API DATA:",
                data
            );


            /* =============================================
               STAT CARDS
            ============================================= */

            const statCards =
                document.querySelectorAll(
                    ".stats-grid .stat-card"
                );


            /* TOTAL ANALYSES */

            if (statCards[0]) {

                const value =
                    statCards[0].querySelector("h2");


                if (value) {

                    value.textContent =
                        Number(
                            data.total_analyses
                        ) || 0;

                }

            }


            /* ISSUES FOUND */

            if (statCards[1]) {

                const value =
                    statCards[1].querySelector("h2");


                if (value) {

                    value.textContent =
                        Number(
                            data.total_issues
                        ) || 0;

                }

            }


            /* REPORTS */

            if (statCards[2]) {

                const value =
                    statCards[2].querySelector("h2");


                if (value) {

                    value.textContent =
                        Number(
                            data.reports
                        ) || 0;

                }

            }


            /* SAVED CODE */

            if (statCards[3]) {

                const value =
                    statCards[3].querySelector("h2");


                if (value) {

                    value.textContent =
                        Number(
                            data.saved_code
                        ) || 0;

                }

            }


            /* =============================================
               RECENT ANALYSES
            ============================================= */

            displayRecentAnalyses(
                data.recent_analyses || []
            );


            /* =============================================
               CODE QUALITY
            ============================================= */

            updateQuality(
                data.quality_score || 0,
                data.quality_breakdown || {}
            );


            /* =============================================
               SEARCH AGAIN
            ============================================= */

            if (
                searchInput &&
                searchInput.value.trim() !== ""
            ) {

                performDashboardSearch();

            }


        })


        .catch(function (error) {

            console.error(
                "Dashboard API ERROR:",
                error
            );

        });

    }


    /* =====================================================
       RECENT ANALYSES
       ===================================================== */

    function displayRecentAnalyses(analyses) {

        const tableBody =
            document.querySelector(
                ".analysis-table tbody"
            );


        if (!tableBody) {

            console.error(
                "Recent analyses table body not found."
            );

            return;

        }


        tableBody.innerHTML = "";


        /* =================================================
           NO ANALYSES
        ================================================= */

        if (
            !Array.isArray(analyses) ||
            analyses.length === 0
        ) {

            tableBody.innerHTML = `

                <tr class="empty-table-row">

                    <td colspan="4">

                        <div class="table-empty-state">

                            <div class="table-empty-icon">

                                <i class="fa-solid fa-chart-simple"></i>

                            </div>


                            <h3>
                                No analyses yet
                            </h3>


                            <p>
                                Your recent code analyses
                                will appear here.
                            </p>

                        </div>

                    </td>

                </tr>

            `;


            applyRecentAnalysesTheme();

            return;

        }


        /* =================================================
           ANALYSIS ROWS
        ================================================= */

        analyses.forEach(function (analysis) {

            const row =
                document.createElement("tr");


            /* ---------------------------------------------
               FILENAME
            --------------------------------------------- */

            const filename =
                escapeHtml(
                    analysis.filename ||
                    "Untitled"
                );


            /* ---------------------------------------------
               LANGUAGE
            --------------------------------------------- */

            const language =
                escapeHtml(
                    analysis.language ||
                    "Unknown"
                );


            /* ---------------------------------------------
               ISSUES
            --------------------------------------------- */

            const issues =
                Number(
                    analysis.issues_count
                ) || 0;


            /* ---------------------------------------------
               DATE
            --------------------------------------------- */

            const date =
                formatDate(
                    analysis.created_at
                );


            /* ---------------------------------------------
               ROW HTML
            --------------------------------------------- */

            row.innerHTML = `

                <td>

                    <div class="recent-file-name">

                        <i class="fa-solid fa-file-code"></i>

                        <span>
                            ${filename}
                        </span>

                    </div>

                </td>


                <td>

                    ${language}

                </td>


                <td>

                    <span class="issue-count">

                        ${issues}

                    </span>

                </td>


                <td>

                    ${date}

                </td>

            `;


            tableBody.appendChild(row);

        });


        /* =================================================
           APPLY CURRENT THEME
        ================================================= */

        applyRecentAnalysesTheme();

    }


    /* =====================================================
       CODE QUALITY REVIEW
       ===================================================== */

    function updateQuality(
        qualityScore,
        breakdown
    ) {

        qualityScore =
            Math.round(
                Number(qualityScore) || 0
            );


        /* =============================================
           DONUT CENTER
        ============================================= */

        const donutCenter =
            document.querySelector(
                ".donut-center span"
            );


        if (donutCenter) {

            donutCenter.textContent =
                qualityScore + "%";

        }


        /* =============================================
           DONUT
        ============================================= */

        const donut =
            document.querySelector(
                ".quality-donut"
            );


        if (donut) {

            donut.style.setProperty(
                "--quality-score",
                qualityScore + "%"
            );


            donut.style.background =
                "conic-gradient(" +
                "#7149ef 0% " +
                qualityScore +
                "%, " +
                "#1b304d " +
                qualityScore +
                "% 100%)";

        }


        /* =============================================
           QUALITY ITEMS
        ============================================= */

        const qualityItems =
            document.querySelectorAll(
                ".quality-details .quality-item"
            );


        const values = [

            breakdown.quality,

            breakdown.maintainability,

            breakdown.reliability,

            breakdown.security,

            breakdown.readability

        ];


        qualityItems.forEach(
            function (item, index) {

                const strong =
                    item.querySelector("strong");


                if (!strong) {
                    return;
                }


                const value =
                    Math.round(
                        Number(
                            values[index]
                        ) || 0
                    );


                strong.textContent =
                    value + "%";

            }
        );

    }


    /* =====================================================
       QUALITY PERIOD
       ===================================================== */

    const qualityPeriod =
        document.getElementById(
            "qualityPeriod"
        );


    if (qualityPeriod) {

        qualityPeriod.addEventListener(
            "change",
            function () {

                console.log(
                    "Quality period:",
                    this.value
                );

            }
        );

    }


    /* =====================================================
       DATE FORMAT
       ===================================================== */

    function formatDate(dateValue) {

        if (!dateValue) {

            return "Unknown date";

        }


        const date =
            new Date(dateValue);


        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return escapeHtml(
                String(dateValue)
            );

        }


        return date.toLocaleDateString(
            "en-IN",
            {
                day: "2-digit",
                month: "short",
                year: "numeric"
            }
        );

    }


    /* =====================================================
       HTML ESCAPE
       ===================================================== */

    function escapeHtml(value) {

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
       INITIAL LOAD
       ===================================================== */

    applyRecentAnalysesTheme();

    loadDashboardData();

});