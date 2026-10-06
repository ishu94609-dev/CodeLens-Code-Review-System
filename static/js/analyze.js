/* =========================================================
   CODELENS - ANALYZE PAGE
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    "use strict";

    /* =====================================================
       STORAGE KEYS
    ===================================================== */

    const ANALYZE_CODE_KEY = "codeLensAnalyzeCode";
    const ANALYZE_LANGUAGE_KEY = "codeLensAnalyzeLanguage";
    const ANALYZE_FILENAME_KEY = "codeLensAnalyzeFilename";
    const ANALYZE_SOURCE_KEY = "codeLensAnalyzeSource";
    const ANALYSIS_ID_KEY = "analysisId";

    /* Profile > Auto Save */
    const AUTO_SAVE_KEY = "autoSaveCode";


    /* =====================================================
       ELEMENTS
    ===================================================== */

    const sidebar =
        document.querySelector(".sidebar");

    const sidebarToggle =
        document.getElementById("sidebarToggle");

    const pasteOption =
        document.getElementById("pasteOption");

    const uploadOption =
        document.getElementById("uploadOption");

    const pastePanel =
        document.getElementById("pastePanel");

    const uploadPanel =
        document.getElementById("uploadPanel");

    const codeInput =
        document.getElementById("codeInput");

    const uploadedCode =
        document.getElementById("uploadedCode");

    const languageSelect =
        document.getElementById("languageSelect");

    const uploadInput =
        document.getElementById("fileInput");

    const browseFile =
        document.getElementById("browseFile");

    const analyzePasteButton =
        document.getElementById("analyzePasteButton");

    const analyzeUploadButton =
        document.getElementById("analyzeUploadButton");

    const clearCode =
        document.getElementById("clearCode");

    const lineCount =
        document.getElementById("lineCount");

    const uploadLineCount =
        document.getElementById("uploadLineCount");

    const analyzeSearch =
        document.getElementById("analyzeSearch");


    /* =====================================================
       CURRENT FILENAME
    ===================================================== */

    let currentFilename =
        localStorage.getItem(
            ANALYZE_FILENAME_KEY
        ) || "";


    /* =====================================================
       PROFILE AUTO SAVE CHECK
    ===================================================== */

    function isAutoSaveEnabled() {

        const savedValue =
            localStorage.getItem(
                AUTO_SAVE_KEY
            );

        /*
         * If the setting does not exist,
         * Profile page treats Auto Save as ON.
         */
        if (savedValue === null) {
            return true;
        }

        return savedValue === "true";
    }


    /* =====================================================
       AUTO SAVE TO SAVED CODE
    ===================================================== */

    async function autoSaveAnalyzedCode(
        code,
        language,
        filename
    ) {

        /*
         * Profile -> Auto Save OFF
         * Do not save to Saved Code.
         *
         * Analysis and Results will still continue.
         */
        if (!isAutoSaveEnabled()) {

            console.log(
                "CodeLens: Auto Save is OFF."
            );

            return;
        }


        try {

            const response =
                await fetch(
                    "/api/saved-code",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",

                            "Accept":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                code: code,
                                language: language,
                                filename: filename
                            })
                    }
                );


            const responseText =
                await response.text();

            let data = null;


            try {

                data =
                    responseText
                        ? JSON.parse(
                            responseText
                        )
                        : null;

            } catch (error) {

                console.warn(
                    "CodeLens: Saved Code returned invalid response."
                );

                return;
            }


            if (
                response.ok &&
                (
                    data?.success === true ||
                    data?.saved === true ||
                    data?.id !== undefined
                )
            ) {

                console.log(
                    "CodeLens: Code automatically saved.",
                    filename
                );

                return;
            }


            /*
             * Some backend implementations may return
             * a normal 200 response without success:true.
             * Do not stop the analysis flow.
             */
            if (response.ok) {

                console.log(
                    "CodeLens: Saved Code request completed."
                );

                return;
            }


            console.warn(
                "CodeLens: Auto Save failed.",
                data
            );

        } catch (error) {

            /*
             * Auto Save must NEVER stop Results page.
             */
            console.warn(
                "CodeLens: Auto Save request failed.",
                error
            );
        }
    }


    /* =====================================================
       SIDEBAR
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
       SHOW PANEL
    ===================================================== */

    function showPanel(source) {

        source =
            String(source || "")
                .toLowerCase()
                .trim();


        if (pastePanel) {

            pastePanel.classList.add(
                "hidden"
            );

            pastePanel.style.display =
                "none";
        }


        if (uploadPanel) {

            uploadPanel.classList.add(
                "hidden"
            );

            uploadPanel.style.display =
                "none";
        }


        if (pasteOption) {

            pasteOption.classList.remove(
                "active"
            );
        }


        if (uploadOption) {

            uploadOption.classList.remove(
                "active"
            );
        }


        if (source === "paste") {

            if (pastePanel) {

                pastePanel.classList.remove(
                    "hidden"
                );

                pastePanel.style.display =
                    "";
            }


            if (pasteOption) {

                pasteOption.classList.add(
                    "active"
                );
            }
        }


        if (source === "upload") {

            if (uploadPanel) {

                uploadPanel.classList.remove(
                    "hidden"
                );

                uploadPanel.style.display =
                    "";
            }


            if (uploadOption) {

                uploadOption.classList.add(
                    "active"
                );
            }
        }


        localStorage.setItem(
            ANALYZE_SOURCE_KEY,
            source
        );
    }


    if (pasteOption) {

        pasteOption.addEventListener(
            "click",
            function () {

                showPanel("paste");

            }
        );
    }


    if (uploadOption) {

        uploadOption.addEventListener(
            "click",
            function () {

                showPanel("upload");

            }
        );
    }


    /* =====================================================
       LANGUAGE DETECTION
    ===================================================== */

    function detectLanguage(filename) {

        const extension =
            String(filename || "")
                .split(".")
                .pop()
                .toLowerCase();


        const languageMap = {

            py: "python",

            java: "java",

            c: "c",

            h: "c",

            cpp: "cpp",

            cc: "cpp",

            cxx: "cpp",

            hpp: "cpp",

            js: "javascript",

            jsx: "javascript",

            mjs: "javascript"

        };


        return (
            languageMap[extension] ||
            ""
        );
    }


    function setLanguage(language) {

        if (
            !languageSelect ||
            !language
        ) {
            return;
        }


        language =
            String(language)
                .toLowerCase()
                .trim();


        const options =
            Array.from(
                languageSelect.options
            );


        const matchingOption =
            options.find(
                function (option) {

                    return (
                        String(
                            option.value
                        )
                            .toLowerCase()
                            .trim() ===
                        language
                    );

                }
            );


        if (matchingOption) {

            languageSelect.value =
                matchingOption.value;
        }
    }


    /* =====================================================
       SAVED NAME DISPLAY
    ===================================================== */

    function createSavedNameDisplay() {

        if (
            document.getElementById(
                "savedCodeNameDisplay"
            )
        ) {
            return;
        }


        const possibleHeadings =
            document.querySelectorAll(
                "h1, h2, h3, h4, h5, h6, " +
                ".section-title, .card-title, .page-title"
            );


        let pasteHeading = null;


        possibleHeadings.forEach(
            function (element) {

                if (pasteHeading) {
                    return;
                }


                const text =
                    element.textContent
                        .trim()
                        .toLowerCase();


                if (
                    text.includes(
                        "paste your code"
                    )
                ) {

                    pasteHeading =
                        element;
                }

            }
        );


        if (!pasteHeading) {
            return;
        }


        const display =
            document.createElement(
                "span"
            );


        display.id =
            "savedCodeNameDisplay";


        display.style.cssText = `
            display: none;
            margin-left: 80px;
            margin-top: 7px;
            position: relative;
            top: 5px;
            font-size: 14px;
            line-height: 1.4;
            font-weight: 600;
            color: #9db8ff;
            white-space: nowrap;
            vertical-align: middle;
        `;


        pasteHeading.appendChild(
            display
        );


        updateSavedNameDisplay();
    }


    function updateSavedNameDisplay() {

        const display =
            document.getElementById(
                "savedCodeNameDisplay"
            );


        if (!display) {
            return;
        }


        const filename =
            localStorage.getItem(
                ANALYZE_FILENAME_KEY
            ) ||
            currentFilename ||
            "";


        if (filename) {

            display.textContent =
                "Saved as: " + filename;

            display.style.display =
                "inline-block";

        } else {

            display.textContent =
                "";

            display.style.display =
                "none";
        }
    }


    /* =====================================================
       LINE COUNT
    ===================================================== */

    function countLines(code) {

        if (!code) {
            return 0;
        }


        return code.split("\n").length;
    }


    function updateLineCounter(
        textarea,
        counter
    ) {

        if (
            !textarea ||
            !counter
        ) {
            return;
        }


        counter.textContent =
            "Lines: " +
            countLines(
                textarea.value
            );
    }


    /* =====================================================
       PASTE CODE INPUT
    ===================================================== */

    if (codeInput) {

        codeInput.addEventListener(
            "input",
            function () {

                updateLineCounter(
                    codeInput,
                    lineCount
                );


                /*
                 * Keep code in localStorage
                 * for Analyze/Results restore.
                 *
                 * This is NOT Saved Code.
                 * Profile Auto Save does not
                 * control this draft storage.
                 */
                localStorage.setItem(
                    ANALYZE_CODE_KEY,
                    codeInput.value
                );


                localStorage.setItem(
                    ANALYZE_SOURCE_KEY,
                    "paste"
                );

            }
        );
    }


    /* =====================================================
       CLEAR CODE
    ===================================================== */

    if (clearCode) {

        clearCode.addEventListener(
            "click",
            function () {

                if (codeInput) {

                    codeInput.value =
                        "";
                }


                if (uploadedCode) {

                    uploadedCode.value =
                        "";
                }


                if (lineCount) {

                    lineCount.textContent =
                        "Lines: 0";
                }


                if (uploadLineCount) {

                    uploadLineCount.textContent =
                        "Lines: 0";
                }


                localStorage.removeItem(
                    ANALYZE_CODE_KEY
                );


                localStorage.removeItem(
                    ANALYZE_FILENAME_KEY
                );


                sessionStorage.removeItem(
                    "codeLensAnalysisFilename"
                );


                currentFilename =
                    "";


                updateSavedNameDisplay();


                localStorage.setItem(
                    ANALYZE_SOURCE_KEY,
                    "paste"
                );


                if (codeInput) {

                    codeInput.focus();
                }

            }
        );
    }


    /* =====================================================
       BROWSE FILE
    ===================================================== */

    if (
        browseFile &&
        uploadInput
    ) {

        browseFile.addEventListener(
            "click",
            function () {

                uploadInput.click();

            }
        );
    }


    /* =====================================================
       FILE UPLOAD
    ===================================================== */

    if (uploadInput) {

        uploadInput.addEventListener(
            "change",
            function () {

                const file =
                    uploadInput.files &&
                    uploadInput.files[0];


                if (!file) {
                    return;
                }


                const reader =
                    new FileReader();


                reader.onload =
                    function (event) {

                        const code =
                            event.target.result ||
                            "";


                        if (uploadedCode) {

                            uploadedCode.value =
                                code;
                        }


                        if (codeInput) {

                            codeInput.value =
                                code;
                        }


                        updateLineCounter(
                            uploadedCode,
                            uploadLineCount
                        );


                        updateLineCounter(
                            codeInput,
                            lineCount
                        );


                        const detectedLanguage =
                            detectLanguage(
                                file.name
                            );


                        if (
                            detectedLanguage
                        ) {

                            setLanguage(
                                detectedLanguage
                            );


                            localStorage.setItem(
                                ANALYZE_LANGUAGE_KEY,
                                detectedLanguage
                            );
                        }


                        localStorage.setItem(
                            ANALYZE_CODE_KEY,
                            code
                        );


                        currentFilename =
                            file.name;


                        localStorage.setItem(
                            ANALYZE_FILENAME_KEY,
                            file.name
                        );


                        updateSavedNameDisplay();


                        localStorage.setItem(
                            ANALYZE_SOURCE_KEY,
                            "upload"
                        );


                        showPanel(
                            "upload"
                        );

                    };


                reader.onerror =
                    function () {

                        showMessage(
                            "Unable to read the selected file."
                        );

                    };


                reader.readAsText(
                    file
                );
            }
        );
    }


    /* =====================================================
       GET CODE EXTENSION
    ===================================================== */

    function getCodeExtension() {

        const language =
            languageSelect
                ? String(
                    languageSelect.value ||
                    ""
                )
                    .trim()
                    .toLowerCase()
                : "";


        if (
            language === "python"
        ) {
            return ".py";
        }


        if (
            language === "java"
        ) {
            return ".java";
        }


        if (
            language === "cpp"
        ) {
            return ".cpp";
        }


        if (
            language === "c"
        ) {
            return ".c";
        }


        if (
            language === "javascript"
        ) {
            return ".js";
        }


        return "";
    }


    /* =====================================================
       SAVE AS POPUP
    ===================================================== */

    function showSaveAsPopup() {

        const oldPopup =
            document.getElementById(
                "saveAsPopup"
            );


        if (oldPopup) {
            oldPopup.remove();
        }


        const oldStyle =
            document.getElementById(
                "saveAsPopupStyles"
            );


        if (oldStyle) {
            oldStyle.remove();
        }


        let existingFilename =
            localStorage.getItem(
                ANALYZE_FILENAME_KEY
            ) ||
            currentFilename ||
            "";


        const extension =
            getCodeExtension();


        if (!existingFilename) {

            existingFilename =
                "code" +
                extension;
        }


        const popup =
            document.createElement(
                "div"
            );


        popup.id =
            "saveAsPopup";


        popup.innerHTML = `

            <div class="save-as-overlay">

                <div class="save-as-box">

                    <div class="save-as-icon">

                        <i class="fa-solid fa-floppy-disk"></i>

                    </div>


                    <h3>
                        Save Code
                    </h3>


                    <p class="save-as-description">
                        Enter a name for your code
                    </p>


                    <input
                        type="text"
                        id="saveAsFilenameInput"
                        class="save-as-input"
                        placeholder="Enter code name"
                        autocomplete="off"
                    >


                    <div class="save-as-buttons">

                        <button
                            type="button"
                            id="saveAsCancelButton"
                            class="save-as-cancel"
                        >
                            Cancel
                        </button>


                        <button
                            type="button"
                            id="saveAsConfirmButton"
                            class="save-as-confirm"
                        >

                            <i class="fa-solid fa-floppy-disk"></i>

                            Save

                        </button>

                    </div>

                </div>

            </div>
        `;


        document.body.appendChild(
            popup
        );


        /* =================================================
           POPUP CSS
        ================================================= */

        const style =
            document.createElement(
                "style"
            );


        style.id =
            "saveAsPopupStyles";


        style.textContent = `

            .save-as-overlay {

                position: fixed;
                inset: 0;
                z-index: 99999;

                display: flex;

                align-items: center;
                justify-content: center;

                background:
                    rgba(0, 0, 0, 0.60);

                backdrop-filter:
                    blur(3px);
            }


            .save-as-box {

                width: 380px;

                max-width:
                    calc(100vw - 40px);

                padding:
                    20px 28px;

                border-radius:
                    10px;

                background:
                    linear-gradient(
                        135deg,
                        #050b18 0%,
                        #0b1b35 48%,
                        #111827 100%
                    );

                border:
                    1px solid
                    rgba(96, 130, 175, 0.25);

                box-shadow:
                    0 20px 55px
                    rgba(0, 0, 0, 0.60);

                text-align:
                    center;

                color:
                    #ffffff;
            }


            .save-as-icon {

                width: 42px;
                height: 42px;

                margin:
                    0 auto 8px;

                border-radius:
                    50%;

                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    center;

                background:
                    rgba(59, 130, 246, 0.14);

                color:
                    #60a5fa;

                font-size:
                    18px;
            }


            .save-as-box h3 {

                margin:
                    0 0 4px;

                font-size:
                    20px;

                font-weight:
                    700;

                color:
                    #ffffff;
            }


            .save-as-description {

                margin:
                    0 0 13px;

                font-size:
                    14px;

                color:
                    rgba(205, 216, 232, 0.75);
            }


            .save-as-input {

                width:
                    100%;

                height:
                    40px;

                box-sizing:
                    border-box;

                padding:
                    0 13px;

                border:
                    1px solid
                    rgba(112, 139, 174, 0.30);

                border-radius:
                    7px;

                outline:
                    none;

                font-family:
                    inherit;

                font-size:
                    14px;

                color:
                    #ffffff;

                background:
                    rgba(0, 8, 20, 0.55);
            }


            .save-as-input::placeholder {

                color:
                    rgba(190, 204, 224, 0.48);
            }


            .save-as-input:focus {

                border-color:
                    rgba(59, 130, 246, 0.75);

                box-shadow:
                    0 0 0 3px
                    rgba(59, 130, 246, 0.10);
            }


            .save-as-buttons {

                margin-top:
                    13px;

                display:
                    flex;

                justify-content:
                    center;

                align-items:
                    center;

                gap:
                    9px;
            }


            .save-as-buttons button {

                min-width:
                    82px;

                height:
                    37px;

                padding:
                    0 15px;

                border-radius:
                    7px;

                cursor:
                    pointer;

                font-family:
                    inherit;

                font-size:
                    14px;

                font-weight:
                    600;
            }


            .save-as-cancel {

                color:
                    #e5e7eb;

                background:
                    rgba(30, 45, 65, 0.72);

                border:
                    1px solid
                    rgba(120, 145, 175, 0.28);
            }


            .save-as-confirm {

                color:
                    #ffffff;

                border:
                    none;

                background:
                    linear-gradient(
                        135deg,
                        #2563eb 0%,
                        #4f46e5 50%,
                        #9333ea 100%
                    );

                box-shadow:
                    0 5px 15px
                    rgba(79, 70, 229, 0.25);
            }


            .save-as-confirm i {

                margin-right:
                    5px;
            }


            /* =================================================
               ANALYZE ACTION BUTTONS
            ================================================= */

            #codeLensAnalyzeActions {

                position:
                    absolute !important;

                right:
                    14px !important;

                bottom:
                    -5px !important;

                z-index:
                    20 !important;

                display:
                    flex !important;

                flex-direction:
                    row !important;

                align-items:
                    center !important;

                justify-content:
                    flex-end !important;

                gap:
                    10px !important;

                width:
                    auto !important;

                height:
                    auto !important;

                flex-wrap:
                    nowrap !important;
            }


            #codeLensAnalyzeActions button {

                position:
                    relative !important;

                display:
                    inline-flex !important;

                align-items:
                    center !important;

                justify-content:
                    center !important;

                flex:
                    0 0 175px !important;

                width:
                    175px !important;

                min-width:
                    175px !important;

                max-width:
                    175px !important;

                height:
                    40px !important;

                min-height:
                    40px !important;

                margin:
                    0 !important;

                padding:
                    0 16px !important;

                box-sizing:
                    border-box !important;

                white-space:
                    nowrap !important;

                border-radius:
                    8px !important;
            }

        `;


        document.head.appendChild(
            style
        );


        const buttonParent =
            analyzePasteButton
                ? analyzePasteButton.parentElement
                : null;


        if (buttonParent) {

            buttonParent.style.position =
                "relative";
        }


        const input =
            document.getElementById(
                "saveAsFilenameInput"
            );


        const cancelButton =
            document.getElementById(
                "saveAsCancelButton"
            );


        const confirmButton =
            document.getElementById(
                "saveAsConfirmButton"
            );


        if (input) {

            input.value =
                existingFilename;

            input.focus();

            input.select();
        }


        function closeSaveAsPopup() {

            const currentPopup =
                document.getElementById(
                    "saveAsPopup"
                );


            if (currentPopup) {
                currentPopup.remove();
            }


            const currentStyle =
                document.getElementById(
                    "saveAsPopupStyles"
                );


            if (currentStyle) {
                currentStyle.remove();
            }
        }


        function saveFilename() {

            if (!input) {
                return;
            }


            let finalFilename =
                input.value.trim();


            if (!finalFilename) {

                showMessage(
                    "Please enter a name for the code."
                );

                input.focus();

                return;
            }


            if (
                /[\\\/:*?"<>|]/.test(
                    finalFilename
                )
            ) {

                showMessage(
                    "Please enter a valid code name."
                );

                input.focus();

                return;
            }


            finalFilename =
                finalFilename.replace(
                    /[. ]+$/,
                    ""
                );


            if (!finalFilename) {

                showMessage(
                    "Please enter a valid code name."
                );

                input.focus();

                return;
            }


            if (
                extension &&
                !/\.[A-Za-z0-9]+$/.test(
                    finalFilename
                )
            ) {

                finalFilename +=
                    extension;
            }


            currentFilename =
                finalFilename;


            localStorage.setItem(
                ANALYZE_FILENAME_KEY,
                finalFilename
            );


            sessionStorage.setItem(
                "codeLensAnalysisFilename",
                finalFilename
            );


            updateSavedNameDisplay();


            closeSaveAsPopup();


            showMessage(
                "Code saved as " +
                finalFilename
            );
        }


        if (cancelButton) {

            cancelButton.addEventListener(
                "click",
                function () {

                    closeSaveAsPopup();

                }
            );
        }


        if (confirmButton) {

            confirmButton.addEventListener(
                "click",
                function () {

                    saveFilename();

                }
            );
        }


        if (input) {

            input.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key === "Enter"
                    ) {

                        event.preventDefault();

                        saveFilename();
                    }


                    if (
                        event.key === "Escape"
                    ) {

                        event.preventDefault();

                        closeSaveAsPopup();
                    }

                }
            );
        }
    }


    /* =====================================================
       CREATE SAVE AS BUTTON
    ===================================================== */

    function createSaveAsButton(
        analyzeButton
    ) {

        if (!analyzeButton) {
            return;
        }


        if (
            document.getElementById(
                "saveAsCodeButton"
            )
        ) {
            return;
        }


        const parent =
            analyzeButton.parentElement;


        if (!parent) {
            return;
        }


        parent.style.position =
            "relative";


        const wrapper =
            document.createElement(
                "div"
            );


        wrapper.id =
            "codeLensAnalyzeActions";


        wrapper.style.cssText = `

            position:
                absolute !important;

            right:
                14px !important;

            bottom:
                -5px !important;

            z-index:
                20 !important;

            display:
                flex !important;

            flex-direction:
                row !important;

            align-items:
                center !important;

            justify-content:
                flex-end !important;

            gap:
                10px !important;

            width:
                auto !important;

            flex-wrap:
                nowrap !important;
        `;


        const saveButton =
            document.createElement(
                "button"
            );


        saveButton.type =
            "button";


        saveButton.id =
            "saveAsCodeButton";


        saveButton.className =
            analyzeButton.className;


        saveButton.innerHTML = `

            <i class="fa-solid fa-floppy-disk"></i>

            Save As
        `;


        saveButton.style.cssText = `

            display:
                inline-flex !important;

            align-items:
                center !important;

            justify-content:
                center !important;

            flex:
                0 0 175px !important;

            width:
                175px !important;

            min-width:
                175px !important;

            max-width:
                175px !important;

            height:
                40px !important;

            margin:
                0 !important;

            padding:
                0 16px !important;

            box-sizing:
                border-box !important;

            white-space:
                nowrap !important;

            border-radius:
                8px !important;
        `;


        analyzeButton.style.cssText += `

            display:
                inline-flex !important;

            align-items:
                center !important;

            justify-content:
                center !important;

            flex:
                0 0 175px !important;

            width:
                175px !important;

            min-width:
                175px !important;

            max-width:
                175px !important;

            height:
                40px !important;

            margin:
                0 !important;

            padding:
                0 16px !important;

            box-sizing:
                border-box !important;

            white-space:
                nowrap !important;

            border-radius:
                8px !important;
        `;


        saveButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();

                showSaveAsPopup();

            }
        );


        parent.insertBefore(
            wrapper,
            analyzeButton
        );


        wrapper.appendChild(
            saveButton
        );


        wrapper.appendChild(
            analyzeButton
        );
    }


    /* =====================================================
       START ANALYSIS
    ===================================================== */

    async function startAnalysis(
        button,
        source
    ) {

        let code = "";


        if (
            source === "upload"
        ) {

            code =
                uploadedCode
                    ? uploadedCode.value.trim()
                    : "";

        } else {

            code =
                codeInput
                    ? codeInput.value.trim()
                    : "";
        }


        if (!code) {

            code =
                localStorage.getItem(
                    ANALYZE_CODE_KEY
                ) || "";


            code =
                code.trim();
        }


        if (!code) {

            showMessage(
                "Please enter or upload some code before analyzing."
            );

            return;
        }


        const language =
            languageSelect
                ? String(
                    languageSelect.value ||
                    ""
                )
                    .trim()
                    .toLowerCase()
                : "";


        if (!language) {

            showMessage(
                "Please select a programming language."
            );

            return;
        }


        let filename =
            localStorage.getItem(
                ANALYZE_FILENAME_KEY
            ) ||
            currentFilename ||
            "";


        if (!filename) {

            filename =
                source === "upload"
                    ? "uploaded_code"
                    : "code";
        }


        if (button) {

            button.disabled =
                true;


            button.dataset.originalText =
                button.innerHTML;


            button.innerHTML = `

                <i class="fa-solid fa-spinner fa-spin"></i>

                Analyzing...
            `;
        }


        try {

            console.log(
                "CodeLens: Starting analysis"
            );


            const response =
                await fetch(
                    "/api/analyze",
                    {
                        method:
                            "POST",

                        headers: {

                            "Content-Type":
                                "application/json",

                            "Accept":
                                "application/json"
                        },

                        body:
                            JSON.stringify({

                                code:
                                    code,

                                language:
                                    language,

                                filename:
                                    filename,

                                source:
                                    source
                            })
                    }
                );


            const responseText =
                await response.text();


            let data = null;


            try {

                data =
                    responseText
                        ? JSON.parse(
                            responseText
                        )
                        : null;

            } catch (error) {

                throw new Error(
                    "Server returned an invalid response."
                );
            }


            if (!response.ok) {

                throw new Error(

                    (
                        data &&
                        (
                            data.message ||
                            data.error
                        )
                    ) ||

                    "Code analysis failed."
                );
            }


            const analysisId =
                data &&
                (
                    data.analysis_id ??
                    data.analysisId ??
                    data.id
                );


            if (
                analysisId === undefined ||
                analysisId === null
            ) {

                throw new Error(
                    "Analysis completed, but the server did not return an analysis ID."
                );
            }


            /* =================================================
               SAVE ANALYSIS ID
            ================================================= */

            sessionStorage.setItem(
                ANALYSIS_ID_KEY,
                String(
                    analysisId
                )
            );


            localStorage.setItem(
                ANALYSIS_ID_KEY,
                String(
                    analysisId
                )
            );


            /* =================================================
               SAVE RESULT DATA FOR RESULTS PAGE
            ================================================= */

            sessionStorage.setItem(
                "codeLensAnalysisCode",
                code
            );


            sessionStorage.setItem(
                "codeLensAnalysisLanguage",
                language
            );


            sessionStorage.setItem(
                "codeLensAnalysisFilename",
                filename
            );


            sessionStorage.setItem(
                "codeLensAnalysisSource",
                source
            );


            /* =================================================
               SAVE ANALYZE PAGE DATA
            ================================================= */

            localStorage.setItem(
                ANALYZE_CODE_KEY,
                code
            );


            localStorage.setItem(
                ANALYZE_LANGUAGE_KEY,
                language
            );


            localStorage.setItem(
                ANALYZE_FILENAME_KEY,
                filename
            );


            localStorage.setItem(
                ANALYZE_SOURCE_KEY,
                source
            );


            currentFilename =
                filename;


            updateSavedNameDisplay();


            /* =================================================
               PROFILE AUTO SAVE
               
               ON  -> Saved Code
               OFF -> Do not save
               
               Results always continue.
            ================================================= */

            await autoSaveAnalyzedCode(
                code,
                language,
                filename
            );


            /* =================================================
               GO TO RESULTS
            ================================================= */

            window.location.assign(
                "/results"
            );

        } catch (error) {

            console.error(
                "CodeLens analysis error:",
                error
            );


            showMessage(
                error.message ||
                "Something went wrong while analyzing."
            );


            if (button) {

                button.disabled =
                    false;


                button.innerHTML =
                    button.dataset.originalText ||
                    "Analyze Code";
            }
        }
    }


    /* =====================================================
       ANALYZE PASTE
    ===================================================== */

    if (analyzePasteButton) {

        analyzePasteButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                startAnalysis(
                    analyzePasteButton,
                    "paste"
                );

            }
        );
    }


    /* =====================================================
       ANALYZE UPLOAD
    ===================================================== */

    if (analyzeUploadButton) {

        analyzeUploadButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                startAnalysis(
                    analyzeUploadButton,
                    "upload"
                );

            }
        );
    }


    /* =====================================================
       SEARCH
    ===================================================== */

    if (analyzeSearch) {

        analyzeSearch.addEventListener(
            "input",
            function () {

                const value =
                    analyzeSearch.value
                        .trim()
                        .toLowerCase();


                const cards =
                    document.querySelectorAll(
                        ".source-card"
                    );


                cards.forEach(
                    function (card) {

                        const text =
                            card.textContent
                                .toLowerCase();


                        if (
                            !value ||
                            text.includes(
                                value
                            )
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
       RESTORE SAVED DATA
    ===================================================== */

    function restoreSavedData() {

        const savedCode =
            localStorage.getItem(
                ANALYZE_CODE_KEY
            );


        const savedLanguage =
            localStorage.getItem(
                ANALYZE_LANGUAGE_KEY
            );


        const savedSource =
            localStorage.getItem(
                ANALYZE_SOURCE_KEY
            );


        const savedFilename =
            localStorage.getItem(
                ANALYZE_FILENAME_KEY
            );


        if (savedFilename) {

            currentFilename =
                savedFilename;
        }


        if (savedLanguage) {

            setLanguage(
                savedLanguage
            );
        }


        if (
            savedCode &&
            codeInput
        ) {

            codeInput.value =
                savedCode;
        }


        updateLineCounter(
            codeInput,
            lineCount
        );


        if (
            savedSource === "upload" &&
            savedCode &&
            uploadedCode
        ) {

            uploadedCode.value =
                savedCode;


            updateLineCounter(
                uploadedCode,
                uploadLineCount
            );
        }


        if (
            savedSource === "upload"
        ) {

            showPanel(
                "upload"
            );

        } else {

            showPanel(
                "paste"
            );
        }
    }


    /* =====================================================
       MESSAGE
    ===================================================== */

    function showMessage(
        message
    ) {

        const old =
            document.getElementById(
                "analyzeMessagePopup"
            );


        if (old) {
            old.remove();
        }


        const popup =
            document.createElement(
                "div"
            );


        popup.id =
            "analyzeMessagePopup";


        popup.innerHTML = `

            <div
                style="
                    position:fixed;
                    inset:0;
                    z-index:999999;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    background:rgba(0,0,0,.55);
                "
            >

                <div
                    style="
                        width:350px;
                        max-width:calc(100vw - 40px);
                        padding:24px;
                        border-radius:10px;
                        text-align:center;
                        color:#fff;

                        background:
                            linear-gradient(
                                135deg,
                                #07101f,
                                #102642
                            );

                        border:1px solid
                            rgba(120,150,190,.25);

                        box-shadow:
                            0 20px 50px
                            rgba(0,0,0,.55);
                    "
                >

                    <div
                        style="
                            font-size:28px;
                            margin-bottom:10px;
                            color:#60a5fa;
                        "
                    >

                        <i
                            class="fa-solid fa-circle-info">
                        </i>

                    </div>


                    <div
                        style="
                            font-size:15px;
                            line-height:1.5;
                            margin-bottom:18px;
                        "
                    >

                        ${escapeHtml(message)}

                    </div>


                    <button
                        type="button"
                        id="analyzeMessageOK"
                        style="
                            border:0;
                            border-radius:7px;
                            padding:9px 24px;
                            color:#fff;
                            cursor:pointer;
                            font-weight:600;

                            background:
                                linear-gradient(
                                    135deg,
                                    #2563eb,
                                    #4f46e5,
                                    #9333ea
                                );
                        "
                    >

                        OK

                    </button>

                </div>

            </div>
        `;


        document.body.appendChild(
            popup
        );


        const ok =
            document.getElementById(
                "analyzeMessageOK"
            );


        if (ok) {

            ok.addEventListener(
                "click",
                function () {

                    popup.remove();

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
       INITIALIZE
    ===================================================== */

    restoreSavedData();

    createSavedNameDisplay();

    createSaveAsButton(
        analyzePasteButton
    );

    updateSavedNameDisplay();


    console.log(
        "CodeLens Analyze page initialized successfully."
    );


    console.log(
        "CodeLens Auto Save:",
        isAutoSaveEnabled()
            ? "ON"
            : "OFF"
    );

});