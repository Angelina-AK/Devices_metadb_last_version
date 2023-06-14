var _a;
import { resources, disableInput } from "../global.js";
const addAttrBtn = document.querySelector('#add-attribute');
const dataUrl = new URL('objects/attributes_names', resources['baseURL']);
const inputsWrapper = document.querySelector('#form-inputs-wrapper'); //для вставки перед кнопкой ногово атрибута
let attributes = null;
(_a = document.querySelector('form')) === null || _a === void 0 ? void 0 : _a.addEventListener('click', disableInput);
const generateBrowserInput = () => {
    let listItems = ``;
    for (const atr of attributes) {
        listItems += `<option value="${atr.name}">\n`;
    }
    let divInput = document.createElement('div');
    divInput.innerHTML = `
  <div class="mt-3">
    <label class="block">
        <span>Attribute name:</span>
        <div class="flex items-center">
            <input
                class="form-input  w-full mt-1.5 disabled:bg-pink-400/40 disabled:placeholder:text-slate-800 disabled:text-slate-800 rounded-lg border border-slate-300 bg-transparent px-3 py-2 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                placeholder="Attribute name"
                autocomplete="off"
                type="text"
                name="attribute"
                list="browser"
            />
            <div class="px-2 py-3 cursor-pointer">x</div>
            <datalist id="browser">
                ${listItems}
            </datalist>
        </div>
    </label>
  </div>`;
    return divInput;
};
fetch(dataUrl)
    .then(data => {
    return data.json();
}).then(data => {
    attributes = data;
    return attributes;
});
addAttrBtn === null || addAttrBtn === void 0 ? void 0 : addAttrBtn.addEventListener('click', (event) => {
    const input = generateBrowserInput();
    inputsWrapper === null || inputsWrapper === void 0 ? void 0 : inputsWrapper.appendChild(input);
});
