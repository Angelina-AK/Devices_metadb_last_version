import { disableInput } from "../global.js";
const init = (() => {
    var _a;
    (_a = document.querySelector('form')) === null || _a === void 0 ? void 0 : _a.addEventListener('click', disableInput);
})();
