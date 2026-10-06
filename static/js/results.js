/* =========================================================
   CODELENS - RESULTS PAGE
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    "use strict";


    /* =====================================================
       SIDEBAR
       ===================================================== */

    const sidebar = document.getElementById("sidebar");
    const sidebarToggle = document.getElementById("sidebarToggle");

    if (sidebar && sidebarToggle) {

        sidebarToggle.addEventListener("click", function () {

            sidebar.classList.toggle("collapsed");

        });

    }


    /* =====================================================
       ELEMENTS
       ===================================================== */

    const fileName = document.getElementById("fileName");

    const totalLines = document.getElementById("totalLines");
    const codeLines = document.getElementById("codeLines");
    const commentLines = document.getElementById("commentLines");
    const blankLines = document.getElementById("blankLines");
    const functions = document.getElementById("functions");
    const classes = document.getElementById("classes");
    const imports = document.getElementById("imports");
    const globalVars = document.getElementById("globalVars");

    const downloadReport =
        document.getElementById("downloadReport");

    const searchInput =
        document.getElementById("resultsSearch");


    /* =====================================================
       ANALYSIS ID
       ===================================================== */

    const analysisId =
        sessionStorage.getItem("analysisId") ||
        localStorage.getItem("analysisId");

    console.log("=================================");
    console.log("CODELENS RESULTS PAGE");
    console.log("Analysis ID:", analysisId);
    console.log("=================================");


    /* =====================================================
       DEFAULT STATE
       ===================================================== */

    if (!analysisId) {

        console.warn("No analysis ID found.");

        if (fileName) {

            fileName.textContent =
                "No analysis available";

        }

        setDefaultResults();

        return;

    }


    /* =====================================================
       DEFAULT RESULTS
       ===================================================== */

    function setDefaultResults() {

        setElement(totalLines, 0);
        setElement(codeLines, 0);
        setElement(commentLines, 0);
        setElement(blankLines, 0);
        setElement(functions, 0);
        setElement(classes, 0);
        setElement(imports, 0);
        setElement(globalVars, 0);


        const cards =
            document.querySelectorAll(".score-card");


        cards.forEach(function (card) {

            const strong =
                card.querySelector(
                    ".score-inner strong"
                );


            if (strong) {

                strong.textContent = "0";

            }


            const status =
                card.querySelector(
                    ".score-status"
                );


            if (status) {

                status.textContent =
                    "No Data";

            }


            const description =
                card.querySelector(
                    ".score-info p"
                );


            if (description) {

                description.textContent =
                    "No analysis yet";

            }


            const scoreCircle =
                card.querySelector(
                    ".score-circle"
                );


            if (scoreCircle) {

                scoreCircle.style.setProperty(
                    "--score-percent",
                    "0%"
                );


                scoreCircle.style.background =
                    "conic-gradient(#24364d 0% 100%)";

            }

        });

    }


    /* =====================================================
       LOAD ANALYSIS
       ===================================================== */

    async function loadAnalysis() {

        try {

            console.log(
                "Loading analysis:",
                analysisId
            );


            const response =
                await fetch(
                    `/api/analysis/${encodeURIComponent(analysisId)}`,
                    {
                        method: "GET",

                        headers: {
                            "Accept":
                                "application/json"
                        },

                        credentials:
                            "same-origin"
                    }
                );


            const responseText =
                await response.text();


            console.log(
                "Analysis API status:",
                response.status
            );


            console.log(
                "Analysis API raw response:",
                responseText
            );


            let data;


            try {

                data =
                    JSON.parse(responseText);

            } catch (error) {

                console.error(
                    "Invalid JSON response:",
                    responseText
                );


                throw new Error(
                    "Server returned invalid JSON."
                );

            }


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    data.message ||
                    "Unable to load analysis."
                );

            }


            console.log(
                "FULL API DATA:",
                data
            );


            let analysis =
                data.analysis ||
                data.data ||
                data.result ||
                data;


            if (
                analysis &&
                analysis.analysis &&
                typeof analysis.analysis === "object"
            ) {

                analysis =
                    analysis.analysis;

            }


            console.log(
                "FINAL ANALYSIS OBJECT:",
                analysis
            );


            displayAnalysis(analysis);


        } catch (error) {

            console.error(
                "Load analysis error:",
                error
            );


            if (fileName) {

                fileName.textContent =
                    "Unable to load analysis";

            }


            setDefaultResults();

        }

    }


    /* =====================================================
       DISPLAY ANALYSIS
       ===================================================== */

    function displayAnalysis(analysis) {

        if (!analysis) {

            console.warn(
                "Analysis object is empty."
            );


            setDefaultResults();

            return;

        }


        console.log(
            "================================="
        );


        console.log(
            "DISPLAY ANALYSIS"
        );


        console.log(
            analysis
        );


        console.log(
            "================================="
        );


        /* =================================================
           FILE NAME
           ================================================= */

        if (fileName) {

            fileName.textContent =
                analysis.filename ||
                analysis.file_name ||
                analysis.name ||
                "Pasted Code";

        }


        /* =================================================
           PARSE ANALYSIS RESULT
           ================================================= */

        let result = {};


        const rawResult =
            analysis.analysis_result ||
            analysis.analysisResult ||
            analysis.result ||
            analysis.results ||
            {};


        try {

            if (typeof rawResult === "string") {

                result =
                    JSON.parse(
                        rawResult || "{}"
                    );

            } else if (
                rawResult &&
                typeof rawResult === "object"
            ) {

                result =
                    rawResult;

            }

        } catch (error) {

            console.error(
                "Could not parse analysis_result:",
                error
            );


            result = {};

        }


        console.log(
            "PARSED RESULT:",
            result
        );


        /* =================================================
           ISSUES
           ================================================= */

        let issues = [];


        if (Array.isArray(result.issues)) {

            issues =
                result.issues;

        } else if (
            Array.isArray(analysis.issues)
        ) {

            issues =
                analysis.issues;

        } else if (
            result.issue_list &&
            Array.isArray(result.issue_list)
        ) {

            issues =
                result.issue_list;

        }


        console.log(
            "ISSUES:",
            issues
        );


        /* =================================================
           METRICS
           ================================================= */

        let metrics =
            result.metrics ||
            analysis.metrics ||
            result.code_metrics ||
            result.statistics ||
            {};


        if (
            typeof metrics === "string"
        ) {

            try {

                metrics =
                    JSON.parse(metrics);

            } catch (error) {

                metrics = {};

            }

        }


        console.log(
            "METRICS:",
            metrics
        );


        /* =================================================
           UPDATE CODE METRICS
           ================================================= */

        setElement(
            totalLines,
            getNumber(
                metrics.total_lines,
                metrics.totalLines,
                metrics.lines,
                result.total_lines,
                analysis.total_lines,
                0
            )
        );


        setElement(
            codeLines,
            getNumber(
                metrics.code_lines,
                metrics.codeLines,
                metrics.source_lines,
                result.code_lines,
                analysis.code_lines,
                0
            )
        );


        setElement(
            commentLines,
            getNumber(
                metrics.comment_lines,
                metrics.commentLines,
                metrics.comments,
                result.comment_lines,
                analysis.comment_lines,
                0
            )
        );


        setElement(
            blankLines,
            getNumber(
                metrics.blank_lines,
                metrics.blankLines,
                metrics.blank,
                result.blank_lines,
                analysis.blank_lines,
                0
            )
        );


        setElement(
            functions,
            getNumber(
                metrics.functions,
                metrics.function_count,
                result.functions,
                result.function_count,
                analysis.functions,
                0
            )
        );


        setElement(
            classes,
            getNumber(
                metrics.classes,
                metrics.class_count,
                result.classes,
                result.class_count,
                analysis.classes,
                0
            )
        );


        setElement(
            imports,
            getNumber(
                metrics.imports,
                metrics.import_count,
                result.imports,
                result.import_count,
                analysis.imports,
                0
            )
        );


        setElement(
            globalVars,
            getNumber(
                metrics.global_vars,
                metrics.globalVars,
                metrics.global_variables,
                result.global_vars,
                result.globalVars,
                analysis.global_vars,
                0
            )
        );


        /* =================================================
           DISPLAY ISSUES
           ================================================= */

        displayIssues(issues);


        /* =================================================
           UPDATE FIVE SCORE CARDS
           ================================================= */

        updateScores(
            analysis,
            result,
            metrics,
            issues
        );


        /* =================================================
           SEARCH
           ================================================= */

        if (
            searchInput &&
            searchInput.value.trim()
        ) {

            performResultsSearch(
                searchInput.value
            );

        }

    }


    /* =====================================================
       NUMBER HELPER
       ===================================================== */

    function getNumber(...values) {

        for (
            let i = 0;
            i < values.length;
            i++
        ) {

            const value =
                values[i];


            if (
                value !== null &&
                value !== undefined &&
                value !== "" &&
                !Number.isNaN(Number(value))
            ) {

                return Number(value);

            }

        }


        return 0;

    }


    /* =====================================================
       SET ELEMENT
       ===================================================== */

    function setElement(
        element,
        value
    ) {

        if (!element) {

            return;

        }


        element.textContent =
            value === null ||
            value === undefined
                ? "0"
                : value;

    }


    /* =====================================================
       DISPLAY ISSUES
       ===================================================== */

    function displayIssues(issues) {

        const issuePanel =
            document.querySelector(
                ".issues-panel"
            );


        if (!issuePanel) {

            return;

        }


        /* =================================================
           TOTAL
           ================================================= */

        const issueHeader =
            issuePanel.querySelector(
                ".panel-header h3"
            );


        if (issueHeader) {

            issueHeader.innerHTML =
                `Issues Found <span>(Total: ${issues.length})</span>`;

        }


        /* =================================================
           COUNTS
           ================================================= */

        let errors = 0;
        let warnings = 0;
        let info = 0;


        issues.forEach(function (issue) {

            const severity =
                String(
                    issue.severity ||
                    issue.level ||
                    issue.type ||
                    "Info"
                ).toLowerCase();


            if (
                severity === "error" ||
                severity === "critical"
            ) {

                errors++;

            } else if (
                severity === "warning" ||
                severity === "warn"
            ) {

                warnings++;

            } else {

                info++;

            }

        });


        /* =================================================
           TABS
           ================================================= */

        const issueTabs =
            issuePanel.querySelectorAll(
                ".issue-tab"
            );


        if (issueTabs.length >= 4) {

            issueTabs[0].innerHTML =
                `All Issues <span>${issues.length}</span>`;


            issueTabs[1].innerHTML =
                `Errors <span>${errors}</span>`;


            issueTabs[2].innerHTML =
                `Warnings <span>${warnings}</span>`;


            issueTabs[3].innerHTML =
                `Info <span>${info}</span>`;

        }


        /* =================================================
           TABLE
           ================================================= */

        const issueTable =
            issuePanel.querySelector(
                ".issue-table"
            );


        if (!issueTable) {

            return;

        }


        issueTable
            .querySelectorAll(".issue-row")
            .forEach(function (row) {

                row.remove();

            });


        const oldEmpty =
            issueTable.querySelector(
                ".issue-empty"
            );


        if (oldEmpty) {

            oldEmpty.remove();

        }


        /* =================================================
           NO ISSUES
           ================================================= */

        if (issues.length === 0) {

            const empty =
                document.createElement(
                    "div"
                );


            empty.className =
                "issue-empty";


            empty.innerHTML = `
                <div class="empty-icon">
                    <i class="fi fi-rr-check"></i>
                </div>

                <h4>No issues found</h4>

                <p>
                    Your code passed the available checks.
                </p>
            `;


            issueTable.appendChild(
                empty
            );


            return;

        }


        /* =================================================
           ISSUE ROWS
           ================================================= */

        issues.forEach(function (issue) {

            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "issue-row";


            const severity =
                issue.severity ||
                issue.level ||
                issue.type ||
                "Info";


            const title =
                issue.issue ||
                issue.title ||
                issue.name ||
                issue.rule ||
                issue.type ||
                "Code Issue";


            const line =
                issue.line ??
                issue.line_number ??
                issue.lineNumber ??
                "-";


            const details =
                issue.details ||
                issue.message ||
                issue.description ||
                issue.explanation ||
                "Review this issue.";


            row.innerHTML = `

                <span class="issue-severity">

                    <span class="severity-badge ${getSeverityClass(severity)}">

                        ${escapeHtml(severity)}

                    </span>

                </span>


                <span class="issue-name">

                    ${escapeHtml(title)}

                </span>


                <span class="issue-line">

                    ${escapeHtml(String(line))}

                </span>


                <span class="issue-details">

                    ${escapeHtml(details)}

                </span>

            `;


            issueTable.appendChild(
                row
            );

        });

    }


    /* =====================================================
       SEVERITY CLASS
       ===================================================== */

    function getSeverityClass(
        severity
    ) {

        const value =
            String(severity)
                .toLowerCase();


        if (
            value === "error" ||
            value === "critical"
        ) {

            return "error";

        }


        if (
            value === "warning" ||
            value === "warn"
        ) {

            return "warning";

        }


        return "info";

    }


    /* =====================================================
       UPDATE FIVE SCORES
       ===================================================== */

    function updateScores(
        analysis,
        result,
        metrics,
        issues
    ) {

        console.log(
            "================================="
        );


        console.log(
            "UPDATING 5 SCORE CARDS"
        );


        console.log(
            "================================="
        );


        const scores =
            analysis.scores ||
            result.scores ||
            {};


        const quality =
            getNumber(
                scores.quality,
                scores.overall_quality,
                analysis.quality_score,
                result.quality_score,
                0
            );


        const maintainability =
            getNumber(
                scores.maintainability,
                analysis.maintainability,
                result.maintainability,
                quality
            );


        const complexity =
            getNumber(
                scores.complexity,
                analysis.complexity_score,
                result.complexity_score,
                0
            );


        const readability =
            getNumber(
                scores.readability,
                analysis.readability,
                result.readability,
                quality
            );


        const security =
            getNumber(
                scores.security,
                analysis.security,
                result.security,
                0
            );


        console.log(
            "Quality:",
            quality
        );


        console.log(
            "Maintainability:",
            maintainability
        );


        console.log(
            "Complexity:",
            complexity
        );


        console.log(
            "Readability:",
            readability
        );


        console.log(
            "Security:",
            security
        );


        const scoreCards =
            document.querySelectorAll(
                ".score-card"
            );


        console.log(
            "Score cards found:",
            scoreCards.length
        );


        if (scoreCards.length < 5) {

            console.error(
                "5 score cards not found."
            );


            return;

        }


        /* =================================================
           SCORE CARD 1 - QUALITY
           BLUE
           ================================================= */

        updateScoreCard(
            scoreCards[0],
            quality,
            100,
            "#2196F3"
        );


        /* =================================================
           SCORE CARD 2 - MAINTAINABILITY
           GREEN
           ================================================= */

        updateScoreCard(
            scoreCards[1],
            maintainability,
            100,
            "#22C55E"
        );


        /* =================================================
           SCORE CARD 3 - COMPLEXITY
           ORANGE
           ================================================= */

        updateScoreCard(
            scoreCards[2],
            complexity,
            50,
            "#F59E0B"
        );


        /* =================================================
           SCORE CARD 4 - READABILITY
           PINK
           ================================================= */

        updateScoreCard(
            scoreCards[3],
            readability,
            100,
            "#EC4899"
        );


        /* =================================================
           SCORE CARD 5 - SECURITY
           PURPLE
           ================================================= */

        updateScoreCard(
            scoreCards[4],
            security,
            100,
            "#A855F7"
        );

    }


    /* =====================================================
       UPDATE SCORE CARD
       ===================================================== */

    function updateScoreCard(
        card,
        score,
        max,
        donutColor
    ) {

        if (!card) {

            return;

        }


        let numericScore =
            Number(score);


        if (
            Number.isNaN(numericScore) ||
            !Number.isFinite(numericScore)
        ) {

            numericScore = 0;

        }


        numericScore =
            Math.max(
                0,
                Math.min(
                    numericScore,
                    max
                )
            );


        const roundedScore =
            Math.round(
                numericScore
            );


        /* =================================================
           SCORE NUMBER
           ================================================= */

        const strong =
            card.querySelector(
                ".score-inner strong"
            );


        if (strong) {

            strong.textContent =
                roundedScore;

        }


        /* =================================================
           DONUT PERCENTAGE
           ================================================= */

        const percentage =
            max > 0
                ? (
                    numericScore /
                    max
                ) * 100
                : 0;


        const safePercentage =
            Math.max(
                0,
                Math.min(
                    100,
                    percentage
                )
            );


        /* =================================================
           DONUT ELEMENTS
           ================================================= */

        const scoreElements = [

            card.querySelector(
                ".score-circle"
            ),

            card.querySelector(
                ".score-ring"
            ),

            card.querySelector(
                ".score-donut"
            ),

            card.querySelector(
                ".score-progress"
            ),

            card.querySelector(
                ".progress-ring"
            )

        ].filter(Boolean);


        scoreElements.forEach(
            function (element) {

                element.style.setProperty(
                    "--score-color",
                    donutColor
                );


                element.style.setProperty(
                    "--donut-color",
                    donutColor
                );


                element.style.setProperty(
                    "--score-percent",
                    `${safePercentage}%`
                );


                element.style.background =
                    `conic-gradient(
                        ${donutColor} 0% ${safePercentage}%,
                        #24364d ${safePercentage}% 100%
                    )`;


                element.style.borderColor =
                    donutColor;


                if (
                    element.tagName &&
                    element.tagName.toLowerCase() ===
                    "circle"
                ) {

                    element.style.stroke =
                        donutColor;

                }


                const svgCircles =
                    element.querySelectorAll
                        ? element.querySelectorAll(
                            "circle"
                        )
                        : [];


                svgCircles.forEach(
                    function (circle) {

                        circle.style.stroke =
                            donutColor;

                    }
                );

            }
        );


        /* =================================================
           STATUS
           ================================================= */

        const status =
            card.querySelector(
                ".score-status"
            );


        const description =
            card.querySelector(
                ".score-info p"
            );


        let statusText =
            "Needs Improvement";


        if (
            roundedScore >=
            max * 0.85
        ) {

            statusText =
                "Excellent";


        } else if (
            roundedScore >=
            max * 0.65
        ) {

            statusText =
                "Good";


        } else if (
            roundedScore >=
            max * 0.40
        ) {

            statusText =
                "Fair";

        }


        if (status) {

            status.textContent =
                statusText;

        }


        if (description) {

            description.textContent =
                statusText +
                " code quality";

        }

    }


    /* =====================================================
       SEARCH MESSAGE
       ===================================================== */

    function createSearchMessage() {

        let message =
            document.getElementById(
                "resultsSearchMessage"
            );


        if (message) {

            return message;

        }


        message =
            document.createElement(
                "div"
            );


        message.id =
            "resultsSearchMessage";


        message.style.fontSize =
            "15px";


        message.style.margin =
            "18px 0 14px 24px";


        message.style.color =
            "#ffffff";


        message.style.fontWeight =
            "400";


        message.style.width =
            "100%";


        message.style.boxSizing =
            "border-box";


        const resultsTop =
            document.querySelector(
                ".results-top"
            );


        if (resultsTop) {

            resultsTop.parentNode.insertBefore(
                message,
                resultsTop
            );


            return message;

        }


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


        mainContent.insertBefore(
            message,
            mainContent.firstChild
        );


        return message;

    }


    /* =====================================================
       REMOVE SEARCH MESSAGE
       ===================================================== */

    function removeSearchMessage() {

        const message =
            document.getElementById(
                "resultsSearchMessage"
            );


        if (message) {

            message.remove();

        }

    }


    /* =====================================================
       SEARCH MESSAGE
       ===================================================== */

    function updateSearchMessage(
        value
    ) {

        const searchValue =
            String(value || "").trim();


        if (!searchValue) {

            removeSearchMessage();

            return;

        }


        const message =
            createSearchMessage();


        if (message) {

            message.textContent =
                `Search results for "${searchValue}"`;

        }

    }


    /* =====================================================
       SEARCH BLOCKS
       ===================================================== */

    function getResultsSearchBlocks() {

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

            return [];

        }


        const blocks = [];


        const resultsTop =
            mainContent.querySelector(
                ".results-top"
            );


        if (resultsTop) {

            blocks.push(resultsTop);

        }


        const fileInfo =
            mainContent.querySelector(
                ".file-info-bar"
            );


        if (fileInfo) {

            blocks.push(fileInfo);

        }


        mainContent
            .querySelectorAll(
                ".score-card"
            )
            .forEach(function (card) {

                if (!blocks.includes(card)) {

                    blocks.push(card);

                }

            });


        const issuePanel =
            mainContent.querySelector(
                ".issues-panel"
            );


        if (
            issuePanel &&
            !blocks.includes(issuePanel)
        ) {

            blocks.push(issuePanel);

        }


        const metricsPanel =
            mainContent.querySelector(
                ".metrics-panel"
            );


        if (
            metricsPanel &&
            !blocks.includes(metricsPanel)
        ) {

            blocks.push(metricsPanel);

        }


        return blocks;

    }


    /* =====================================================
       PERFORM SEARCH
       ===================================================== */

    function performResultsSearch(
        value
    ) {

        const searchValue =
            String(value || "")
                .trim()
                .toLowerCase();


        updateSearchMessage(
            value
        );


        const blocks =
            getResultsSearchBlocks();


        /* =================================================
           EMPTY SEARCH
           ================================================= */

        if (!searchValue) {

            blocks.forEach(function (block) {

                block.style.display =
                    "";

            });


            document
                .querySelectorAll(
                    ".issue-row"
                )
                .forEach(function (row) {

                    row.style.display =
                        "";

                });


            return;

        }


        /* =================================================
           SEARCH MAIN BLOCKS
           ================================================= */

        blocks.forEach(function (block) {

            const text =
                (
                    block.innerText ||
                    block.textContent ||
                    ""
                ).toLowerCase();


            block.style.display =
                text.includes(
                    searchValue
                )
                    ? ""
                    : "none";

        });


        /* =================================================
           SEARCH ISSUE ROWS
           ================================================= */

        const issuePanel =
            document.querySelector(
                ".issues-panel"
            );


        if (!issuePanel) {

            return;

        }


        const issueRows =
            issuePanel.querySelectorAll(
                ".issue-row"
            );


        let issueMatch = false;


        issueRows.forEach(function (row) {

            const text =
                (
                    row.innerText ||
                    row.textContent ||
                    ""
                ).toLowerCase();


            const matches =
                text.includes(
                    searchValue
                );


            row.style.display =
                matches
                    ? ""
                    : "none";


            if (matches) {

                issueMatch = true;

            }

        });


        if (issueMatch) {

            issuePanel.style.display =
                "";

        }

    }


    /* =====================================================
       SEARCH INPUT
       ===================================================== */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            function () {

                performResultsSearch(
                    searchInput.value
                );

            }
        );


        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter"
                ) {

                    event.preventDefault();


                    performResultsSearch(
                        searchInput.value
                    );

                }

            }
        );

    }


    /* =====================================================
       DOWNLOAD REPORT
       ===================================================== */

    if (downloadReport) {

        downloadReport.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                /*
                 * Result page-ல் Download Report
                 * click செய்தால் actual JSON download
                 * செய்யாமல் Reports page-க்கு செல்லும்.
                 */

                window.location.href =
                    "/reports";

            }
        );

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
       START
       ===================================================== */

    loadAnalysis();

});