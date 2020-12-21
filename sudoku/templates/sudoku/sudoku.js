/* sudoku.js 1.0 */
"use strict";

(function (Sudoku) {

    const sudoku_prefix = 'Sudoku-ng-';

    const sudoku_rows = [
        [0,   1,  2,  3,  4,  5,  6,  7,  8 ],
        [9,  10, 11, 12, 13, 14, 15, 16, 17 ],
        [18, 19, 20, 21, 22, 23, 24, 25, 26 ],
        [27, 28, 29, 30, 31, 32, 33, 34, 35 ],
        [36, 37, 38, 39, 40, 41, 42, 43, 44 ],
        [45, 46, 47, 48, 49, 50, 51, 52, 53 ],
        [54, 55, 56, 57, 58, 59, 60, 61, 62 ],
        [63, 64, 65, 66, 67, 68, 69, 70, 71 ],
        [72, 73, 74, 75, 76, 77, 78, 79, 80 ]
    ];

    const sudoku_blocks = [
        [0, 1, 2,
         9, 10, 11,
         18, 19, 20],
        [3, 4, 5,
         12, 13, 14,
         21, 22, 23],
        [6, 7, 8,
         15, 16, 17,
         24, 25, 26],
        [27, 28, 29,
         36, 37, 38,
         45, 46, 47],
        [30, 31, 32,
         39, 40, 41,
         48, 49, 50],
        [33, 34, 35,
         42, 43, 44,
         51, 52, 53],
        [54, 55, 56,
         63, 64, 65,
         72, 73, 74],
        [57, 58, 59,
         66, 67, 68,
         75, 76, 77],
        [60, 61, 62,
         69, 70, 71,
         78, 79, 80]
    ];

    const sudoku_cols = [
        [0, 9, 18, 27, 36, 45, 54, 63, 72],
        [1, 10, 19, 28, 37, 46, 55, 64, 73],
        [2, 11, 20, 29, 38, 47, 56, 65, 74],
        [3, 12, 21, 30, 39, 48, 57, 66, 75],
        [4, 13, 22, 31, 40, 49, 58, 67, 76],
        [5, 14, 23, 32, 41, 50, 59, 68, 77],
        [6, 15, 24, 33, 42, 51, 60, 69, 78],
        [7, 16, 25, 34, 43, 52, 61, 70, 79],
        [8, 17, 26, 35, 44, 53, 62, 71, 80]
    ];

    const sudoku_lookup = [
        [0, 0, 0], [0, 0, 1], [0, 0, 2], [0, 1, 3], [0, 1, 4], [0, 1, 5],
        [0, 2, 6], [0, 2, 7], [0, 2, 8], [1, 0, 0], [1, 0, 1], [1, 0, 2],
        [1, 1, 3], [1, 1, 4], [1, 1, 5], [1, 2, 6], [1, 2, 7], [1, 2, 8],
        [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 1, 3], [2, 1, 4], [2, 1, 5],
        [2, 2, 6], [2, 2, 7], [2, 2, 8], [3, 3, 0], [3, 3, 1], [3, 3, 2],
        [3, 4, 3], [3, 4, 4], [3, 4, 5], [3, 5, 6], [3, 5, 7], [3, 5, 8],
        [4, 3, 0], [4, 3, 1], [4, 3, 2], [4, 4, 3], [4, 4, 4], [4, 4, 5],
        [4, 5, 6], [4, 5, 7], [4, 5, 8], [5, 3, 0], [5, 3, 1], [5, 3, 2],
        [5, 4, 3], [5, 4, 4], [5, 4, 5], [5, 5, 6], [5, 5, 7], [5, 5, 8],
        [6, 6, 0], [6, 6, 1], [6, 6, 2], [6, 7, 3], [6, 7, 4], [6, 7, 5],
        [6, 8, 6], [6, 8, 7], [6, 8, 8], [7, 6, 0], [7, 6, 1], [7, 6, 2],
        [7, 7, 3], [7, 7, 4], [7, 7, 5], [7, 8, 6], [7, 8, 7], [7, 8, 8],
        [8, 6, 0], [8, 6, 1], [8, 6, 2], [8, 7, 3], [8, 7, 4], [8, 7, 5],
        [8, 8, 6], [8, 8, 7], [8, 8, 8]
    ];


    const DUPLICATE = {
        no: 0,
        many_to_many: 1,
        many_to_one: 2,
        one_to_many: 3,
        one_to_one: 4,
    }

    let active_block = null;

    ///////////////////////////

    // Functions with no side effects

    const getMobileOS = () => {
        var userAgent = navigator.userAgent || navigator.vendor || window.opera;

        // Windows Phone must come first because its UA also contains "Android"
        if (/windows phone/i.test(userAgent)) {
            return "Windows Phone";
        }

        if (/android/i.test(userAgent)) {
            return "Android";
        }

        // iOS detection from: http://stackoverflow.com/a/9039885/177710
        if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
            return "iOS";
        }
        return "unknown";
    }

    const convertPuzzleStr = (str) => {
        let arr = []
        for (let i = 0; i < str.length; i++) {
            if (str[i] === "0") {
                arr.push(["&nbsp;", false]);
            } else {
                arr.push([str[i], true]);
            }
        }
        return arr;
    }

    const filterDigits = (value) => {
        let new_val = "";
        for (let i = 0; i < value.length; i++) {
            if ("123456789".includes(value[i]) &&
                !new_val.includes(value[i])) {
                new_val = new_val + value[i];
            }
        }
        return new_val;
    }

    const sortStr = (s) => {
        let arr = s.split("");
        let arr_sorted = arr.sort();
        return arr_sorted.join("");
    }

    const getBlocksByTable = (sudoku_table) => {
        return sudoku_table.getElementsByTagName('td');
    }

    const getBlocksByDiv = (sudoku_div) => {
        return getBlocksByTable(sudoku_div.getElementsByTagName('table')[0]);
    }

    const getBlocksByDivId = (sudoku_div_id) => {
        return getBlocksByDiv(document.getElementById(sudoku_div_id));
    }

    const getBlockIndex = (block) => {
        const class_prefix = "sudoku-td-"
        for (const name of block.classList) {
            if (name.includes(class_prefix)) {
                return parseInt(name.substr(class_prefix.length));
            }
        }
    }

    const getBlockValue = (block) => {
        const value = block.textContent;
        if (value.trim().length > 0) {
            return value;
        } else {
            return "0";
        }
    }

    const isSet = (block) => {
        if (getBlockValue(block) != "0") {
            return true;
        } else {
            return false;
        }
    }

    const digitIn = (block, digit) => {
        if (block.textContent.includes(digit)) {
            return true;
        } else {
            return false;
        }
    }

    const isDuplicateGroup = (blocks, index, group) => {
        let one_to_many = false;
        let many_to_many = false;

        const val_1 = getBlockValue(blocks[index]);
        if (val_1 == "0") return DUPLICATE.no;

        for (const i of group) {
            const val_2 = getBlockValue(blocks[i]);
            if (index === i || val_2 === "0") continue; // same block or cf. space
            if (val_1.length === 1) { // Check for one_to_one or one_to_many
                if (val_1 === val_2) {
                    return DUPLICATE.one_to_one;
                } else if (val_2.includes(val_1)) {
                    one_to_many = true;
                }
            } else { // Check for many_to_one or many_to_many
                if (val_2.length === 1 && val_1.includes(val_2)) {
                    return DUPLICATE.many_to_one;
                } else if (val_1 === val_2) {
                    many_to_many = true;
                }
            }
        }

        if (one_to_many) return DUPLICATE.one_to_many;
        if (many_to_many) return DUPLICATE.many_to_many;
        return DUPLICATE.no;
    }

    const isDuplicateBlock = (blocks, block) => {
        let result_rows = DUPLICATE.no;
        let result_blocks = DUPLICATE.no;
        let result_cols = DUPLICATE.no;
        const index = getBlockIndex(block);
        const lookup = sudoku_lookup[index];
        if (isSet(block)) {
            result_rows = isDuplicateGroup(blocks, index, sudoku_rows[lookup[0]]);
            result_blocks = isDuplicateGroup(blocks, index,
                                             sudoku_blocks[lookup[1]]);
            result_cols = (isDuplicateGroup(blocks, index, sudoku_cols[lookup[2]]));
        }
        return Math.max(result_rows, result_blocks, result_cols);
    }

    const checkCompleted = (sudoku_div_id) => {
        const blocks = getBlocksByDivId(sudoku_div_id);
        for (const block of blocks) {
            const val = getBlockValue(block);
            if (val.length != 1  || val === "0" ||
                isDuplicateBlock(blocks, block)) {
                return false;
            }
        }
        return true;
    }

    const isProtectedBlock = (block) => {
        return block.classList.contains('sudoku-protected');
    }

    const getPuzzleString = (sudoku_div_id) => {
        let str = "";
        const blocks = getBlocksByDivId(sudoku_div_id);
        for (const block of blocks) {
            if (isProtectedBlock(block)) {
                str += getBlockValue(block);
            } else {
                str += "0";
            }
        }
        return str;
    }



    // Functions with side effects

    // From https://stackoverflow.com/questions/1181700/set-cursor-position-on-contenteditable-div
    const placeCursorAtEnd = function(el) {
        var selection = window.getSelection();
        var range = document.createRange();
        selection.removeAllRanges();
        range.selectNodeContents(el);
        range.collapse(false);
        selection.addRange(range);
        el.focus();
    }

    const suppressAndroidKeyboard = () => {
        //this set timeout needed for case when hideKeyborad
        //is called inside of 'onfocus' event handler
        setTimeout(function() {

            //creating temp field
            var field = document.createElement('input');
            field.setAttribute('type', 'text');
            //hiding temp field from peoples eyes
            //-webkit-user-modify is nessesary for Android 4.x
            field.setAttribute('style', 'position:absolute; top: 0px; opacity: 0; -webkit-user-modify: read-write-plaintext-only; left:0px;');
            document.body.appendChild(field);
            //adding onfocus event handler for out temp field
            field.onfocus = function(){
                //this timeout of 200ms is nessasary for Android 2.3.x
                setTimeout(function() {

                    field.setAttribute('style', 'display:none;');
                    setTimeout(function() {
                        document.body.removeChild(field);
                        document.body.focus();
                    }, 14);
                }, 200);
            };
            //focusing it
            field.focus();
        }, 50);
    }

    const setBlockValue = (block, value) => {
        if (value === (" ") || value === "0" || value === "&nbsp;") {
            block.innerHTML = "&nbsp;";
        } else {
            const v = sortStr(filterDigits(value));
            if (v.length > 0) {
                block.textContent = v;
            } else {
                block.innerHTML = "&nbsp;";
            }
        }
    }

    const removeBlockDigit = (block, digit) => {
        let value = block.textContent;
        let new_value = "";
        for (let i = 0; i < value.length; i++) {
            if (value[i] != digit) {
                new_value += value[i];
            }
        }
        setBlockValue(block, new_value);
    }

    const markDuplicateBlock = (block, result) => {
        unmarkDuplicateBlock(block);
        if (result === DUPLICATE.many_to_many) {
            block.classList.add('sudoku-many-to-many');
        } else if (result === DUPLICATE.many_to_one) {
            block.classList.add('sudoku-many-to-one');
        } else if (result === DUPLICATE.one_to_many) {
            block.classList.add('sudoku-one-to-many');
        } else if (result === DUPLICATE.one_to_one) {
            block.classList.add('sudoku-one-to-one');
        }
    }

    const unmarkDuplicateBlock = (block) => {
        block.classList.remove('sudoku-many-to-many');
        block.classList.remove('sudoku-many-to-one');
        block.classList.remove('sudoku-one-to-many');
        block.classList.remove('sudoku-one-to-one');
    }

    const markAllDuplicateBlocks = (sudoku_div_id) => {
        const blocks = getBlocksByDivId(sudoku_div_id);
        for (let block of blocks) {
            let result = isDuplicateBlock(blocks, block);
            if (result) {
                markDuplicateBlock(block, result)
            } else {
                unmarkDuplicateBlock(block);
            }
        }
    }

    const unmarkAllDuplicateBlocks = (sudoku_div_id) => {
        const blocks = getBlocksByDivId(sudoku_div_id);
        for (let block of blocks) {
            unmarkDuplicateBlock(block);
        }
    }

    const markCompleted = (sudoku_div_id) => {
        let elem = document.getElementById(sudoku_div_id);
        let tbl = elem.getElementsByTagName('table')[0];
        tbl.classList.add('sudoku-table-completed');
        let paras = elem.getElementsByClassName('sudoku-incomplete');
        for (let p of paras) {
            p.classList.remove('sudoku-incomplete');
            p.classList.add('sudoku-complete');
        }
    }

    const unmarkCompleted = (sudoku_div_id) => {
        let elem = document.getElementById(sudoku_div_id);
        let tbl = elem.getElementsByTagName('table')[0];
        tbl.classList.remove('sudoku-table-completed');
        let paras = elem.getElementsByClassName('sudoku-complete');
        for (let p of paras) {
            p.classList.add('sudoku-incomplete');
            p.classList.remove('sudoku-complete');
        }
    }

    const showIfCompleted = (sudoku_div_id) => {
        if (checkCompleted(sudoku_div_id)) {
            markCompleted(sudoku_div_id);
        } else {
            unmarkCompleted(sudoku_div_id);
        }
    }

    const saveGrid = (sudoku_div_id) => {
        const key = getPuzzleString(sudoku_div_id);
        const blocks = getBlocksByDivId(sudoku_div_id);
        let block_array = [];
        for (const block of blocks) {
            if (isProtectedBlock(block)) {
                block_array.push([block.textContent, true])
            } else {
                block_array.push([block.textContent, false])
            }
        }
        localStorage.setItem(sudoku_prefix + key,
                             JSON.stringify(block_array));
    }

    const setBlock = (block, value, protect = false) => {
        setBlockValue(block, value);
        if (protect) {
            block.classList.add('sudoku-protected');
            block.contentEditable = false;
        } else {
            block.classList.remove('sudoku-protected');
            block.contentEditable = true;
        }
    }

    const setGrid = (sudoku_div_id, grid) => {
        let blocks = getBlocksByDivId(sudoku_div_id);
        for (let i = 0; i < blocks.length; i++) {
            setBlock(blocks[i], grid[i][0], grid[i][1]);
            setFontSize(blocks[i]);
        }
    }

    const loadGrid = (sudoku_div_id_from, sudoku_div_id_to) => {
        const key = getPuzzleString(sudoku_div_id_from);
        const grid = JSON.parse(localStorage.getItem(sudoku_prefix + key));
        if (grid) {
            setGrid(sudoku_div_id_to, grid);
        } else {
            return false;
        }
        markAllDuplicateBlocks(sudoku_div_id_to);
        return true;
    }

    const setActiveBlock = (block) => {
        if (active_block) {
            active_block.classList.remove('sudoku-td-in-focus');
        }
        active_block = block;
        active_block.focus();
        block.classList.add('sudoku-td-in-focus');
    }

    const setFontSize = (block) => {
        block.classList.remove('sudoku-font-1', 'sudoku-font-2',
                               'sudoku-font-3', 'sudoku-font-4',
                               'sudoku-font-5', 'sudoku-font-6',
                               'sudoku-font-7', 'sudoku-font-8',
                               'sudoku-font-9');
        const l = block.textContent.length;
        const className = 'sudoku-font-' + l.toString();
        block.classList.add(className);
    }

    const processBlock = (sudoku_div_id, block) => {
        markAllDuplicateBlocks(sudoku_div_id);
        saveGrid(sudoku_div_id);
        showIfCompleted(sudoku_div_id);
        setFontSize(block);
    }

    const processInput = (sudoku_div_id, block, value) => {
        if (value === '\xa0' || value === " " || value === "0") {
            setBlockValue(block, "0");
        } else if (digitIn(block, value)) {
            removeBlockDigit(block, value);
        } else {
            setBlockValue(block, block.textContent + value);
        }
        block.focus();
        placeCursorAtEnd(block);
    }

    const setupTable = (sudoku_div_id, sudoku_table) => {
        let blocks = sudoku_table.getElementsByTagName('td');
        let android = false;
        if (getMobileOS() === "Android") android = true;
        for (let block of blocks) {
            if (android) {
                block.addEventListener("focus", function(e) {
                    block.blur();
                });
            }
            block.addEventListener("focus", function(e) {
                setActiveBlock(e.target);
            });
            block.addEventListener('keydown', function(e) {
                const c = String.fromCharCode(e.keyCode);
                if (' 0123456789'.includes(c)) {
                    processInput(sudoku_div_id, e.target, c);
                    e.preventDefault();
                } else if (![8, 9, 17, 35, 36, 37, 39, 46].includes(e.keyCode)) {
                    e.preventDefault();
                }
            });
            block.addEventListener('keyup', function() {
                processBlock(sudoku_div_id, block);
            });
        }
    }

    const setupDigits = (sudoku_div_id) => {
        let sudoku_div = document.getElementById(sudoku_div_id);
        let digits =  sudoku_div.getElementsByClassName('sudoku-btn');
        for (const digit of digits) {
            digit.addEventListener("click", function(e) {
                e.preventDefault();
                if (active_block && sudoku_div.contains(active_block)) {
                    processInput(sudoku_div_id, active_block, e.target.textContent);
                    processBlock(sudoku_div_id, active_block);
                }
            });
        }
    }

    const clearBlockText = (block) => {
        block.innerHTML = "&nbsp;";
    }

    const toggleClues = (sudoku_div_id, btn) => {
        let div = document.getElementById(sudoku_div_id);
        if (div.classList.contains('sudoku-no-clues')) {
            div.classList.remove('sudoku-no-clues');
            markAllDuplicateBlocks(sudoku_div_id);
            if (btn) {
                btn.textContent = 'Clues off';
            }
        } else {
            div.classList.add('sudoku-no-clues');
            unmarkAllDuplicateBlocks(sudoku_div_id);
            if (btn) {
                btn.textContent = 'Clues on';
            }
        }
    }

    const clearGrid = (sudoku_div) => {
        let blocks = getBlocksByDiv(sudoku_div);
        for (let block of blocks) {
            if (!isProtectedBlock(block)) {
                clearBlockText(block);
            }
            unmarkDuplicateBlock(block);
        }
    };

    const findAndSetActiveBlock = (sudoku_div_id) => {
        if (!active_block) {
            let blocks = getBlocksByDivId(sudoku_div_id);
            for (const block of blocks) {
                if (block.classList.contains('sudoku-protected')) {
                    continue;
                } else {
                    setActiveBlock(block);
                    processBlock(sudoku_div_id, block);
                    //placeCursorAtEnd(block);
                    return;
                }
            }
        }
    }

    const init = (sudoku_div_id, puzzle_str, options) => {
        let sudoku_div = document.getElementById(sudoku_div_id);
        let sudoku_table = sudoku_div.getElementsByTagName('table')[0];
        setupTable(sudoku_div_id, sudoku_table);
        setupDigits(sudoku_div_id);
        const grid = convertPuzzleStr(puzzle_str);
        setGrid(sudoku_div_id, grid);
        if (options.try_load) {
            loadGrid(sudoku_div_id, sudoku_div_id);
        }
        findAndSetActiveBlock(sudoku_div_id);
        let restart_btn = sudoku_div.getElementsByClassName('sudoku-restart')[0];
        if (restart_btn) {
            restart_btn.addEventListener('click', function() {
                if (confirm('Are you sure you wish to restart')) {
                    clearGrid(sudoku_div);
                    saveGrid(sudoku_div_id);
                }
            });
        }
        let clues_btn = sudoku_div.getElementsByClassName('sudoku-clues')[0];
        if (clues_btn) {
            clues_btn.addEventListener('click', function(e) {
                toggleClues(sudoku_div_id, e.target);
            });
        }
        if (options.clues_on == false) {
            toggleClues(sudoku_div_id, clues_btn);
        }
    }

    const insertTable = (sudoku_div) => {
        const innerhtml = '<p class="sudoku-incomplete">Puzzle completed</p> ' +
              '<table class="sudoku-table"> '+
              '<tr id="sudoku-tr-0"> '+
              '<td class="sudoku-td-0" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-1" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-2" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-3" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-4" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-5" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-6" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-7" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-8" contenteditable=true>&nbsp;</td> '+
              '</tr> '+
              '<tr class="sudoku-tr-1"> '+
              '<td class="sudoku-td-9" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-10" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-11" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-12" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-13" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-14" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-15" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-16" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-17" contenteditable=true>&nbsp;</td> '+
              '</tr> '+
              '<tr class="sudoku-tr-2"> '+
              '<td class="sudoku-td-18" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-19" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-20" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-21" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-22" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-23" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-24" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-25" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-26" contenteditable=true>&nbsp;</td> '+
              '</tr> '+
              '<tr class="sudoku-tr-3"> '+
              '<td class="sudoku-td-27" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-28" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-29" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-30" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-31" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-32" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-33" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-34" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-35" contenteditable=true>&nbsp;</td> '+
              '</tr> '+
              '<tr class="sudoku-tr-4"> '+
              '<td class="sudoku-td-36" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-37" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-38" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-39" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-40" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-41" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-42" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-43" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-44" contenteditable=true>&nbsp;</td> '+
              '</tr> '+
              '<tr class="sudoku-tr-5"> '+
              '<td class="sudoku-td-45" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-46" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-47" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-48" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-49" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-50" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-51" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-52" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-53" contenteditable=true>&nbsp;</td> '+
              '</tr> '+
              '<tr class="sudoku-tr-6"> '+
              '<td class="sudoku-td-54" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-55" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-56" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-57" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-58" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-59" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-60" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-61" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-62" contenteditable=true>&nbsp;</td> '+
              '</tr> '+
              '<tr class="sudoku-tr-7"> '+
              '<td class="sudoku-td-63" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-64" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-65" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-66" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-67" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-68" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-69" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-70" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-71" contenteditable=true>&nbsp;</td> '+
              '</tr> '+
              '<tr class="sudoku-tr-8"> '+
              '<td class="sudoku-td-72" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-73" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-74" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-75" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-76" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-77" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-78" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-79" contenteditable=true>&nbsp;</td> '+
              '<td class="sudoku-td-80" contenteditable=true>&nbsp;</td> '+
              '</tr> '+
              '</table> ';
        sudoku_div.innerHTML += innerhtml;
    }


    const insertDigitButtons = (sudoku_div) => {
        const innerhtml =
              '<p class="sudoku-buttons"> '+
              '<button class="sudoku-btn sudoku-btn-0">&nbsp;</button> '+
              '<button class="sudoku-btn sudoku-btn-1">1</button> '+
              '<button class="sudoku-btn sudoku-btn-2">2</button> '+
              '<button class="sudoku-btn sudoku-btn-3">3</button> '+
              '<button class="sudoku-btn sudoku-btn-4">4</button> '+
              '<button class="sudoku-btn sudoku-btn-5">5</button> '+
              '<button class="sudoku-btn sudoku-btn-6">6</button> '+
              '<button class="sudoku-btn sudoku-btn-7">7</button> '+
              '<button class="sudoku-btn sudoku-btn-8">8</button> '+
              '<button class="sudoku-btn sudoku-btn-9">9</button> '+
              '</p> ';
        sudoku_div.innerHTML += innerhtml;
    }

    const restartButtonHTML = () => {
        return '<button class="sudoku-restart">Restart</button>';
    }

    const cluesButtonHTML = () => {
        return '<button class="sudoku-clues">Clues off</button>';
    }

    const insertControlButtons = (sudoku_div, options) => {
        let innerhtml = '<p class="sudoku-control">';
        if (options.restart_button == true) {
            innerhtml += restartButtonHTML();
        }
        if (options.clues_button == true) {
            innerhtml += cluesButtonHTML();
        }
        innerhtml += '</p>';
        sudoku_div.innerHTML += innerhtml;
    }

    const insertHTML = (sudoku_div, options) => {
        insertTable(sudoku_div);
        if (options.digit_buttons == true) {
            insertDigitButtons(sudoku_div);
        }
        insertControlButtons(sudoku_div, options);
    }

    Sudoku.create = (sudoku_div_id, puzzle_str, options = {}) => {
        let default_options = {
            try_load: true,
            clues_on: true,
            digit_buttons: true,
            restart_button: true,
            clues_button: true
        };
        for (let [key, value] of Object.entries(options)) {
            if (key in default_options) {
                default_options[key] = value;
            } else {
                console.log('Unknown option:', key)
            }
        }
        let div = document.getElementById(sudoku_div_id);
        div.classList.add('sudoku-div');
        insertHTML(div, default_options);
        init(sudoku_div_id, puzzle_str, default_options);
    }
}(window.Sudoku = window.Sudoku || {}));
