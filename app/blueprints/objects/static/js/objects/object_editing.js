var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { disableInput, resources } from "../global.js";
let module = (() => __awaiter(void 0, void 0, void 0, function* () {
    const addObjectBtn = document.getElementById('add-object');
    let inputsWrapper = document.querySelector('#form-inputs-wrapper'); //для вставки перед кнопкой нового вложенного объекта
    const dataUrlObjects = resources['baseURL'] + '/objects/get_all_possible_childs/';
    const dataUrlTypes = resources['baseURL'] + '/objects/types';
    let childObjects = [];
    let types = [];
    let datalistChildObjects = ``;
    let id = null;
    const generateBrowserInputChilds = () => {
        let input = document.createElement('label');
        input.classList.add('block', 'mt-3');
        input.innerHTML = `
        <span>Child:</span>
        <div class="flex items-center">
            <input
                class="form-input  w-full mt-1.5 disabled:bg-pink-400/40 disabled:placeholder:text-slate-800 disabled:text-slate-800 rounded-lg border border-slate-300 bg-transparent px-3 py-2 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                placeholder="Attribute name"
                autocomplete="off"
                type="text"
                name="child-object-name"
                list="browser"
            />
            <div class="disable-div-x">x</div>
            <datalist id="browser">
                ${datalistChildObjects}
            </datalist>
        </div>`;
        return input;
    };
    const fetchObjects = () => __awaiter(void 0, void 0, void 0, function* () {
        const response = yield fetch(dataUrlObjects + id);
        childObjects = yield response.json();
        return childObjects;
    });
    const fetchTypes = () => __awaiter(void 0, void 0, void 0, function* () {
        const response = yield fetch(dataUrlTypes);
        types = yield response.json();
        return types;
    });
    const addListenerTypeInput = (types) => {
        debugger;
        let input = document.querySelector('#type-input');
        input.addEventListener('change', e => {
            generateAttributes(e.target.value, types);
        });
    };
    const generateAttributes = (type, types) => {
        let attributesWrapper = document.querySelector('#attrs-wrapper');
        attributesWrapper.innerHTML = '';
        if (!(types.find(el => el['type_name'] == type))) {
            return;
        }
        let attributes = types.find((el) => el['type_name'] == type)['attributes'];
        let atrtibutesInputs = document.createElement('div');
        attributes.forEach(e => {
            let attributeInput = `
            <div class="grid grid-cols-3 justify-items-start items-center">
                <span class="mr-3">
                    ${e}
                </span>
                <input
                    class="form-input w-full mt-1.5 disabled:bg-pink-400/40 disabled:placeholder:text-slate-800 disabled:text-slate-800 rounded-lg border border-slate-300 bg-transparent px-3 py-2 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent"
                    placeholder="${e} value"
                    autocomplete="off"
                    type="text"
                    name="attr-${e}"
                />
                <div class="disable-div-x">x</div>
            </div>
      `;
            atrtibutesInputs.innerHTML += attributeInput;
        });
        attributesWrapper.appendChild(atrtibutesInputs);
    };
    const generateDalatisChilds = () => {
        childObjects.forEach(e => {
            datalistChildObjects += `<option value="${e}">\n`;
        });
    };
    const generateBrowserInputTypes = (types) => {
        let listItems = ``;
        types.forEach(element => {
            listItems += `<option value="${element.type_name}">\n`;
        });
        document.querySelector('#browsers-types').innerHTML = listItems;
    };
    // init page
    id = document.querySelector('form').id;
    yield fetchObjects();
    yield fetchTypes();
    console.log(types);
    console.log(childObjects);
    generateDalatisChilds();
    generateBrowserInputTypes(types);
    addListenerTypeInput(types);
    document.querySelector("#submit-btn").classList.remove('disabled');
    document.querySelector("#form-inputs-wrapper").addEventListener('click', disableInput);
    addObjectBtn.addEventListener('click', () => {
        const input = generateBrowserInputChilds();
        inputsWrapper.appendChild(input);
    });
    return {
        fetchObjects: fetchObjects,
        fetchTypes: fetchTypes,
        generateDalatisChilds: generateDalatisChilds,
    };
}))();
