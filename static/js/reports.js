// =========================================================
// CODELENS - REPORTS PAGE
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    "use strict";


    // =====================================================
    // ELEMENTS
    // =====================================================

    const sidebar =
        document.querySelector(".sidebar");

    const sidebarToggle =
        document.getElementById("sidebarToggle");

    const openGenerateBtn =
        document.getElementById("openGenerateBtn");

    const generatePanel =
        document.getElementById("generatePanel");

    const generateBtn =
        document.getElementById("generateBtn");

    const reportType =
        document.getElementById("reportType");

    const reportList =
        document.getElementById("reportList");

    const globalSearch =
        document.getElementById("globalSearch");

    const logoutBtn =
        document.getElementById("logoutBtn");

    const logoutModal =
        document.getElementById("logoutModal");

    const cancelLogout =
        document.getElementById("cancelLogout");

    const confirmLogout =
        document.getElementById("confirmLogout");


    // =====================================================
    // SIDEBAR TOGGLE
    // =====================================================

    if (sidebarToggle && sidebar) {

        sidebarToggle.addEventListener(
            "click",
            function () {

                sidebar.classList.toggle("collapsed");

                document.body.classList.toggle(
                    "sidebar-collapsed"
                );

            }
        );

    }


    // =====================================================
    // OPEN / CLOSE GENERATE PANEL
    // =====================================================

    if (openGenerateBtn && generatePanel) {

        openGenerateBtn.addEventListener(
            "click",
            function () {

                if (
                    generatePanel.style.display === "none" ||
                    generatePanel.style.display === ""
                ) {

                    generatePanel.style.display = "block";

                } else {

                    generatePanel.style.display = "none";

                }

            }
        );

    }


    // =====================================================
    // GENERATED REPORTS THEME
    // =====================================================

    function applyGeneratedReportsTheme() {

        if (
            document.getElementById(
                "generatedReportsThemeStyle"
            )
        ) {
            return;
        }


        const style =
            document.createElement("style");


        style.id =
            "generatedReportsThemeStyle";


        style.textContent = `

            /* =================================================
               GENERATED REPORT FONT SIZE
            ================================================= */

            #reportList .report-card-content h4 {

                font-size: 16px !important;

                line-height: 1.35 !important;

            }


            #reportList .report-card-content p {

                font-size: 14px !important;

                line-height: 1.4 !important;

            }


            #reportList .report-card-content small {

                font-size: 12px !important;

                line-height: 1.3 !important;

            }


            #reportList .report-card-actions a,
            #reportList .report-card-actions button {

                font-size: 13px !important;

            }


            /* =================================================
               LIGHT MODE
            ================================================= */

            html[data-theme="light"] #reportList {

                background: #ffffff !important;

                color: #172033 !important;

            }


            html[data-theme="light"]
            #reportList .report-card {

                background: #ffffff !important;

                background-color: #ffffff !important;

                border: 1px solid #d9e2f0 !important;

                color: #172033 !important;

                box-shadow:
                    0 2px 8px
                    rgba(31, 41, 55, 0.06) !important;

            }


            html[data-theme="light"]
            #reportList .report-card:hover {

                background: #ffffff !important;

                border-color: #b9c8df !important;

                box-shadow:
                    0 5px 14px
                    rgba(31, 41, 55, 0.10) !important;

            }


            html[data-theme="light"]
            #reportList .report-card-icon {

                background: #f3e8ff !important;

                color: #9333ea !important;

            }


            html[data-theme="light"]
            #reportList .report-card-icon i {

                color: #9333ea !important;

            }


            html[data-theme="light"]
            #reportList .report-card-content h4 {

                color: #172033 !important;

            }


            html[data-theme="light"]
            #reportList .report-card-content p {

                color: #64748b !important;

            }


            html[data-theme="light"]
            #reportList .report-card-content small {

                color: #94a3b8 !important;

            }


            html[data-theme="light"]
            #reportList .view-report-btn {

                background: #eef4ff !important;

                color: #2563eb !important;

                border: 1px solid #cbdcfb !important;

            }


            html[data-theme="light"]
            #reportList .view-report-btn:hover {

                background: #e0ebff !important;

                color: #1d4ed8 !important;

            }


            html[data-theme="light"]
            #reportList .download-report-btn {

                background:
                    linear-gradient(
                        135deg,
                        #2563eb 0%,
                        #4f46e5 50%,
                        #b832e8 100%
                    ) !important;

                color: #ffffff !important;

            }


            /* =================================================
               BLUE DELETE BUTTON - LIGHT MODE
            ================================================= */

            html[data-theme="light"]
            #reportList .delete-report-btn {

                background: #eef4ff !important;

                color: #2563eb !important;

                border: 1px solid #cbdcfb !important;

                cursor: pointer !important;

            }


            html[data-theme="light"]
            #reportList .delete-report-btn:hover {

                background: #e0ebff !important;

                color: #1d4ed8 !important;

                border-color: #b9cdf5 !important;

            }


            html[data-theme="light"]
            #reportList .empty-state {

                background: #ffffff !important;

                color: #172033 !important;

                border-color: #d9e2f0 !important;

            }


            html[data-theme="light"]
            #reportList .empty-state h3 {

                color: #172033 !important;

            }


            html[data-theme="light"]
            #reportList .empty-state p {

                color: #64748b !important;

            }


            html[data-theme="light"]
            #reportList .empty-state i {

                color: #9333ea !important;

            }


            /* =================================================
               DARK MODE
            ================================================= */

            html[data-theme="dark"] #reportList {

                background: transparent !important;

                color: #ffffff !important;

            }


            html[data-theme="dark"]
            #reportList .report-card {

                background: #071225 !important;

                background-color: #071225 !important;

                border: 1px solid #263c59 !important;

                color: #ffffff !important;

                box-shadow:
                    0 2px 8px
                    rgba(0, 0, 0, 0.20) !important;

            }


            html[data-theme="dark"]
            #reportList .report-card:hover {

                background: #0b1930 !important;

                border-color: #385274 !important;

            }


            html[data-theme="dark"]
            #reportList .report-card-icon {

                background:
                    rgba(147, 51, 234, 0.18) !important;

                color: #c084fc !important;

            }


            html[data-theme="dark"]
            #reportList .report-card-icon i {

                color: #c084fc !important;

            }


            html[data-theme="dark"]
            #reportList .report-card-content h4 {

                color: #ffffff !important;

            }


            html[data-theme="dark"]
            #reportList .report-card-content p {

                color: #9aaac0 !important;

            }


            html[data-theme="dark"]
            #reportList .report-card-content small {

                color: #71839d !important;

            }


            html[data-theme="dark"]
            #reportList .view-report-btn {

                background: #10233e !important;

                color: #60a5fa !important;

                border: 1px solid #294563 !important;

            }


            html[data-theme="dark"]
            #reportList .view-report-btn:hover {

                background: #153052 !important;

                color: #93c5fd !important;

            }


            html[data-theme="dark"]
            #reportList .download-report-btn {

                background:
                    linear-gradient(
                        135deg,
                        #2563eb 0%,
                        #4f46e5 50%,
                        #b832e8 100%
                    ) !important;

                color: #ffffff !important;

            }


            /* =================================================
               BLUE DELETE BUTTON - DARK MODE
            ================================================= */

            html[data-theme="dark"]
            #reportList .delete-report-btn {

                background: #10233e !important;

                color: #60a5fa !important;

                border: 1px solid #294563 !important;

                cursor: pointer !important;

            }


            html[data-theme="dark"]
            #reportList .delete-report-btn:hover {

                background: #153052 !important;

                color: #93c5fd !important;

                border-color: #3d5f87 !important;

            }


            html[data-theme="dark"]
            #reportList .empty-state {

                background: #071225 !important;

                color: #ffffff !important;

                border-color: #263c59 !important;

            }


            html[data-theme="dark"]
            #reportList .empty-state h3 {

                color: #ffffff !important;

            }


            html[data-theme="dark"]
            #reportList .empty-state p {

                color: #9aaac0 !important;

            }


            html[data-theme="dark"]
            #reportList .empty-state i {

                color: #c084fc !important;

            }


            /* =================================================
               DELETE CONFIRMATION POPUP
            ================================================= */

            .delete-confirm-overlay {

                position: fixed !important;

                inset: 0 !important;

                z-index: 99999 !important;

                display: flex !important;

                align-items: center !important;

                justify-content: center !important;

                background:
                    rgba(0, 0, 0, 0.65) !important;

            }


            .delete-confirm-box {

                width: 390px !important;

                max-width: calc(100vw - 40px) !important;

                padding: 28px !important;

                border-radius: 14px !important;

                text-align: center !important;

                background: #071225 !important;

                border: 1px solid #263c59 !important;

                color: #ffffff !important;

                box-shadow:
                    0 20px 60px
                    rgba(0, 0, 0, 0.40) !important;

            }


            .delete-confirm-icon {

                width: 54px !important;

                height: 54px !important;

                margin: 0 auto 16px !important;

                border-radius: 50% !important;

                display: flex !important;

                align-items: center !important;

                justify-content: center !important;

                background:
                    rgba(37, 99, 235, 0.14) !important;

                color: #60a5fa !important;

                font-size: 22px !important;

            }


            .delete-confirm-box h3 {

                margin: 0 0 10px !important;

                color: #ffffff !important;

                font-size: 21px !important;

            }


            .delete-confirm-box p {

                margin: 0 0 22px !important;

                color: #9aaac0 !important;

                font-size: 15px !important;

            }


            .delete-confirm-buttons {

                display: flex !important;

                justify-content: center !important;

                gap: 10px !important;

            }


            .delete-cancel-btn,
            .delete-confirm-btn {

                min-width: 105px !important;

                padding: 10px 18px !important;

                border-radius: 8px !important;

                cursor: pointer !important;

                font-size: 14px !important;

                font-weight: 600 !important;

            }


            .delete-cancel-btn {

                background: #172942 !important;

                color: #dbe7f5 !important;

                border: 1px solid #304967 !important;

            }


            .delete-confirm-btn {

                background: #2563eb !important;

                color: #ffffff !important;

                border: 1px solid #2563eb !important;

            }


            .delete-confirm-btn:hover {

                background: #1d4ed8 !important;

                border-color: #1d4ed8 !important;

            }


            /* =================================================
               LIGHT DELETE POPUP
            ================================================= */

            html[data-theme="light"]
            .delete-confirm-box {

                background: #ffffff !important;

                border: 1px solid #d9e2f0 !important;

                color: #172033 !important;

                box-shadow:
                    0 20px 60px
                    rgba(31, 41, 55, 0.18) !important;

            }


            html[data-theme="light"]
            .delete-confirm-icon {

                background: #eef4ff !important;

                color: #2563eb !important;

            }


            html[data-theme="light"]
            .delete-confirm-box h3 {

                color: #172033 !important;

            }


            html[data-theme="light"]
            .delete-confirm-box p {

                color: #64748b !important;

            }


            html[data-theme="light"]
            .delete-cancel-btn {

                background: #f1f5f9 !important;

                color: #334155 !important;

                border: 1px solid #d8e0ea !important;

            }


            html[data-theme="light"]
            .delete-confirm-btn {

                background: #2563eb !important;

                color: #ffffff !important;

                border: 1px solid #2563eb !important;

            }


            html[data-theme="light"]
            .delete-confirm-btn:hover {

                background: #1d4ed8 !important;

                border-color: #1d4ed8 !important;

            }


            /* =================================================
               SUCCESS / ERROR POPUP
            ================================================= */

            .report-popup-overlay {

                position: fixed !important;

                inset: 0 !important;

                z-index: 99998 !important;

                display: flex !important;

                align-items: center !important;

                justify-content: center !important;

                background:
                    rgba(0, 0, 0, 0.65) !important;

            }


            .report-success-popup {

                width: 390px !important;

                max-width: calc(100vw - 40px) !important;

                padding: 28px !important;

                border-radius: 14px !important;

                text-align: center !important;

                background: #071225 !important;

                border: 1px solid #263c59 !important;

                color: #ffffff !important;

                box-shadow:
                    0 20px 60px
                    rgba(0, 0, 0, 0.40) !important;

            }


            .report-success-icon {

                width: 54px !important;

                height: 54px !important;

                margin: 0 auto 16px !important;

                border-radius: 50% !important;

                display: flex !important;

                align-items: center !important;

                justify-content: center !important;

                background:
                    rgba(34, 197, 94, 0.14) !important;

                color: #4ade80 !important;

                font-size: 22px !important;

            }


            .report-success-icon.error-icon {

                background:
                    rgba(220, 38, 38, 0.14) !important;

                color: #f87171 !important;

            }


            .report-success-popup h3 {

                margin: 0 0 10px !important;

                color: #ffffff !important;

                font-size: 21px !important;

            }


            .report-success-popup p {

                margin: 0 0 22px !important;

                color: #9aaac0 !important;

                font-size: 15px !important;

            }


            .report-popup-ok {

                min-width: 100px !important;

                padding: 10px 20px !important;

                border-radius: 8px !important;

                border: 1px solid #2563eb !important;

                background: #2563eb !important;

                color: #ffffff !important;

                cursor: pointer !important;

                font-size: 14px !important;

                font-weight: 600 !important;

            }


            .report-popup-ok:hover {

                background: #1d4ed8 !important;

            }


            html[data-theme="light"]
            .report-success-popup {

                background: #ffffff !important;

                border: 1px solid #d9e2f0 !important;

                color: #172033 !important;

                box-shadow:
                    0 20px 60px
                    rgba(31, 41, 55, 0.18) !important;

            }


            html[data-theme="light"]
            .report-success-popup h3 {

                color: #172033 !important;

            }


            html[data-theme="light"]
            .report-success-popup p {

                color: #64748b !important;

            }

        `;


        document.head.appendChild(style);

    }


    applyGeneratedReportsTheme();


    // =====================================================
    // WATCH LIGHT / DARK MODE CHANGES
    // =====================================================

    const themeObserver =
        new MutationObserver(
            function () {

                console.log(
                    "CodeLens theme changed:",
                    document.documentElement
                        .getAttribute("data-theme")
                );

            }
        );


    themeObserver.observe(
        document.documentElement,
        {
            attributes: true,
            attributeFilter: ["data-theme"]
        }
    );


    // =====================================================
    // LOAD GENERATED REPORTS
    // =====================================================

    async function loadReports() {

        if (!reportList) {
            return;
        }


        try {

            const response =
                await fetch(
                    "/api/reports",
                    {
                        method: "GET",
                        cache: "no-store"
                    }
                );


            const data =
                await response.json();


            console.log(
                "Reports API status:",
                response.status
            );


            console.log(
                "Reports API data:",
                data
            );


            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.message ||
                    "Unable to load reports."
                );

            }


            reportList.innerHTML = "";


            // =================================================
            // NO REPORTS
            // =================================================

            if (
                !data.reports ||
                data.reports.length === 0
            ) {

                reportList.innerHTML = `

                    <div class="empty-state">

                        <i class="fa-regular fa-file-pdf"></i>

                        <h3>
                            No Reports Generated
                        </h3>

                        <p>
                            Generate a report to see it here.
                        </p>

                    </div>

                `;

                return;

            }


            // =================================================
            // DISPLAY REPORTS
            // =================================================

            data.reports.forEach(
                function (report) {

                    const card =
                        document.createElement("div");


                    card.className =
                        "report-card";


                    // -----------------------------------------
                    // FILE PATH
                    // -----------------------------------------

                    let filePath =
                        report.file_path || "";


                    if (
                        filePath &&
                        !filePath.startsWith("/")
                    ) {

                        filePath =
                            "/static/" + filePath;

                    }


                    // -----------------------------------------
                    // DATE
                    // -----------------------------------------

                    let createdDate =
                        report.created_at || "";


                    if (createdDate) {

                        try {

                            createdDate =
                                new Date(
                                    createdDate
                                ).toLocaleString(
                                    "en-IN",
                                    {
                                        day: "2-digit",
                                        month: "short",
                                        year: "numeric",
                                        hour: "2-digit",
                                        minute: "2-digit"
                                    }
                                );

                        } catch (error) {

                            console.log(
                                "Date formatting error:",
                                error
                            );

                        }

                    }


                    // -----------------------------------------
                    // CARD
                    // -----------------------------------------

                    card.innerHTML = `

                        <div class="report-card-icon">

                            <i class="fa-solid fa-file-pdf"></i>

                        </div>


                        <div class="report-card-content">

                            <h4>
                                ${escapeHtml(
                                    report.report_name ||
                                    "CodeLens Report"
                                )}
                            </h4>


                            <p>

                                ${escapeHtml(
                                    report.report_type ||
                                    "Report"
                                )}

                                •

                                ${escapeHtml(
                                    (
                                        report.language ||
                                        "Unknown"
                                    ).toUpperCase()
                                )}

                            </p>


                            <small>

                                ${escapeHtml(
                                    createdDate ||
                                    "Generated recently"
                                )}

                            </small>

                        </div>


                        <div class="report-card-actions">

                            ${
                                filePath
                                    ? `

                                        <a
                                            href="${escapeHtml(filePath)}"
                                            target="_blank"
                                            class="view-report-btn"
                                        >

                                            <i
                                                class="fa-solid fa-eye"
                                            ></i>

                                            View

                                        </a>


                                        <a
                                            href="${escapeHtml(filePath)}"
                                            download
                                            class="download-report-btn"
                                        >

                                            <i
                                                class="fa-solid fa-download"
                                            ></i>

                                            Download

                                        </a>

                                      `
                                    : ""
                            }


                            <button
                                type="button"
                                class="delete-report-btn"
                                data-report-id="${escapeHtml(
                                    report.id
                                )}"
                            >

                                <i
                                    class="fa-solid fa-trash"
                                ></i>

                                Delete

                            </button>

                        </div>

                    `;


                    reportList.appendChild(card);


                    // =================================================
                    // DELETE BUTTON - DIRECT EVENT
                    // =================================================

                    const deleteButton =
                        card.querySelector(
                            ".delete-report-btn"
                        );


                    if (deleteButton) {

                        deleteButton.addEventListener(
                            "click",
                            function (event) {

                                event.preventDefault();

                                event.stopPropagation();


                                const reportId =
                                    this.getAttribute(
                                        "data-report-id"
                                    );


                                console.log(
                                    "Delete button clicked. Report ID:",
                                    reportId
                                );


                                if (!reportId) {

                                    console.error(
                                        "Report ID is missing."
                                    );


                                    showErrorPopup(
                                        "Delete Failed",
                                        "Report ID was not found."
                                    );


                                    return;

                                }


                                showDeleteConfirmPopup(
                                    reportId
                                );

                            }
                        );

                    }

                }
            );

        } catch (error) {

            console.error(
                "Load reports error:",
                error
            );


            reportList.innerHTML = `

                <div class="empty-state">

                    <i
                        class="fa-solid fa-triangle-exclamation"
                    ></i>

                    <h3>
                        Unable to Load Reports
                    </h3>

                    <p>
                        ${escapeHtml(
                            error.message ||
                            "Something went wrong."
                        )}
                    </p>

                </div>

            `;

        }

    }


    // =====================================================
    // GENERATE REPORT
    // =====================================================

    if (generateBtn) {

        generateBtn.addEventListener(
            "click",
            async function () {

                const selectedType =
                    reportType
                        ? reportType.value
                        : "Full Code Review";


                generateBtn.disabled =
                    true;


                const originalText =
                    generateBtn.innerHTML;


                generateBtn.innerHTML = `

                    <i
                        class="fa-solid fa-spinner fa-spin"
                    ></i>

                    Generating...

                `;


                try {

                    const response =
                        await fetch(
                            "/api/reports",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    report_type:
                                        selectedType
                                })
                            }
                        );


                    const data =
                        await response.json();


                    console.log(
                        "Generate report response:",
                        data
                    );


                    if (
                        !response.ok ||
                        !data.success
                    ) {

                        throw new Error(
                            data.message ||
                            "Unable to generate report."
                        );

                    }


                    await loadReports();


                    if (generatePanel) {

                        generatePanel.style.display =
                            "none";

                    }


                    showSuccessPopup(
                        "PDF Report Generated",
                        "Your PDF report has been generated successfully."
                    );


                } catch (error) {

                    console.error(
                        "Generate report error:",
                        error
                    );


                    showErrorPopup(
                        "Report Generation Failed",
                        error.message ||
                        "Unable to generate report."
                    );

                } finally {

                    generateBtn.disabled =
                        false;


                    generateBtn.innerHTML =
                        originalText;

                }

            }
        );

    }


    // =====================================================
    // DELETE REPORT
    // =====================================================

    async function deleteReport(reportId) {

        console.log(
            "Deleting report:",
            reportId
        );


        try {

            const response =
                await fetch(
                    `/api/reports/${encodeURIComponent(reportId)}`,
                    {
                        method: "DELETE",

                        headers: {
                            "Accept":
                                "application/json"
                        }
                    }
                );


            console.log(
                "Delete HTTP status:",
                response.status
            );


            const text =
                await response.text();


            console.log(
                "Delete API response:",
                text
            );


            let data;


            try {

                data =
                    text
                        ? JSON.parse(text)
                        : {};

            } catch (parseError) {

                console.error(
                    "Delete JSON parse error:",
                    parseError
                );


                throw new Error(
                    "Server returned an invalid response."
                );

            }


            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.message ||
                    "Unable to delete report."
                );

            }


            // Refresh list after successful deletion.
            // No success popup here.

            await loadReports();


        } catch (error) {

            console.error(
                "Delete report error:",
                error
            );


            showErrorPopup(
                "Delete Failed",
                error.message ||
                "Unable to delete report."
            );

        }

    }


    // =====================================================
    // DELETE CONFIRMATION POPUP
    // =====================================================

    function showDeleteConfirmPopup(reportId) {

        const existingPopup =
            document.getElementById(
                "deleteConfirmPopup"
            );


        if (existingPopup) {
            existingPopup.remove();
        }


        const popup =
            document.createElement("div");


        popup.id =
            "deleteConfirmPopup";


        popup.innerHTML = `

            <div class="delete-confirm-overlay">

                <div class="delete-confirm-box">

                    <div class="delete-confirm-icon">

                        <i
                            class="fa-solid fa-trash"
                        ></i>

                    </div>


                    <h3>
                        Delete Report?
                    </h3>


                    <p>
                        Are you sure you want to delete this report?
                    </p>


                    <div class="delete-confirm-buttons">

                        <button
                            type="button"
                            class="delete-cancel-btn"
                        >
                            Cancel
                        </button>


                        <button
                            type="button"
                            class="delete-confirm-btn"
                        >
                            Delete
                        </button>

                    </div>

                </div>

            </div>

        `;


        document.body.appendChild(popup);


        console.log(
            "Delete confirmation popup opened for:",
            reportId
        );


        const cancelButton =
            popup.querySelector(
                ".delete-cancel-btn"
            );


        const confirmButton =
            popup.querySelector(
                ".delete-confirm-btn"
            );


        // =================================================
        // CANCEL
        // =================================================

        if (cancelButton) {

            cancelButton.addEventListener(
                "click",
                function () {

                    popup.remove();

                }
            );

        }


        // =================================================
        // CONFIRM DELETE
        // =================================================

        if (confirmButton) {

            confirmButton.addEventListener(
                "click",
                async function () {

                    if (
                        confirmButton.disabled
                    ) {
                        return;
                    }


                    confirmButton.disabled =
                        true;


                    confirmButton.textContent =
                        "Deleting...";


                    await deleteReport(
                        reportId
                    );


                    popup.remove();

                }
            );

        }


        // =================================================
        // CLICK OUTSIDE
        // =================================================

        const overlay =
            popup.querySelector(
                ".delete-confirm-overlay"
            );


        if (overlay) {

            overlay.addEventListener(
                "click",
                function (event) {

                    if (
                        event.target === overlay
                    ) {

                        popup.remove();

                    }

                }
            );

        }

    }


    // =====================================================
    // SEARCH GENERATED REPORTS
    // =====================================================

    if (globalSearch) {

        globalSearch.addEventListener(
            "input",
            function () {

                const searchText =
                    this.value
                        .trim()
                        .toLowerCase();


                const cards =
                    document.querySelectorAll(
                        ".report-card"
                    );


                cards.forEach(
                    function (card) {

                        const text =
                            card.textContent
                                .toLowerCase();


                        if (
                            !searchText ||
                            text.includes(searchText)
                        ) {

                            card.style.display =
                                "flex";

                        } else {

                            card.style.display =
                                "none";

                        }

                    }
                );

            }
        );

    }


    // =====================================================
    // LOGOUT
    // =====================================================

    if (logoutBtn && logoutModal) {

        logoutBtn.addEventListener(
            "click",
            function () {

                logoutModal.style.display =
                    "flex";

            }
        );

    }


    if (cancelLogout && logoutModal) {

        cancelLogout.addEventListener(
            "click",
            function () {

                logoutModal.style.display =
                    "none";

            }
        );

    }


    if (confirmLogout) {

        confirmLogout.addEventListener(
            "click",
            function () {

                window.location.href =
                    "/logout";

            }
        );

    }


    // =====================================================
    // ESCAPE HTML
    // =====================================================

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


    // =====================================================
    // SUCCESS POPUP
    // =====================================================
    // Used only for successful report generation.

    function showSuccessPopup(
        title,
        message
    ) {

        const existingPopup =
            document.getElementById(
                "reportSuccessPopup"
            );


        if (existingPopup) {
            existingPopup.remove();
        }


        const popup =
            document.createElement("div");


        popup.id =
            "reportSuccessPopup";


        popup.innerHTML = `

            <div class="report-popup-overlay">

                <div class="report-success-popup">

                    <div class="report-success-icon">

                        <i
                            class="fa-solid fa-check"
                        ></i>

                    </div>


                    <h3>
                        ${escapeHtml(title)}
                    </h3>


                    <p>
                        ${escapeHtml(message)}
                    </p>


                    <button
                        type="button"
                        class="report-popup-ok"
                    >
                        OK
                    </button>

                </div>

            </div>

        `;


        document.body.appendChild(popup);


        const okButton =
            popup.querySelector(
                ".report-popup-ok"
            );


        if (okButton) {

            okButton.addEventListener(
                "click",
                function () {

                    popup.remove();

                }
            );

        }


        const overlay =
            popup.querySelector(
                ".report-popup-overlay"
            );


        if (overlay) {

            overlay.addEventListener(
                "click",
                function (event) {

                    if (
                        event.target === overlay
                    ) {

                        popup.remove();

                    }

                }
            );

        }

    }


    // =====================================================
    // ERROR POPUP
    // =====================================================

    function showErrorPopup(
        title,
        message
    ) {

        const popup =
            document.createElement("div");


        popup.className =
            "report-error-popup-wrapper";


        popup.innerHTML = `

            <div class="report-popup-overlay">

                <div class="report-success-popup">

                    <div
                        class="report-success-icon error-icon"
                    >

                        <i
                            class="fa-solid fa-xmark"
                        ></i>

                    </div>


                    <h3>
                        ${escapeHtml(title)}
                    </h3>


                    <p>
                        ${escapeHtml(message)}
                    </p>


                    <button
                        type="button"
                        class="report-popup-ok"
                    >
                        OK
                    </button>

                </div>

            </div>

        `;


        document.body.appendChild(popup);


        const button =
            popup.querySelector(
                ".report-popup-ok"
            );


        if (button) {

            button.addEventListener(
                "click",
                function () {

                    popup.remove();

                }
            );

        }


        const overlay =
            popup.querySelector(
                ".report-popup-overlay"
            );


        if (overlay) {

            overlay.addEventListener(
                "click",
                function (event) {

                    if (
                        event.target === overlay
                    ) {

                        popup.remove();

                    }

                }
            );

        }

    }


    // =====================================================
    // INITIAL LOAD
    // =====================================================

    loadReports();

});