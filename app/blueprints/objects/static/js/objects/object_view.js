var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { resources } from "../global.js";
const dataUrlObjectsInHierarchy = resources['baseURL'] + '/objects/get_json_all_objects';
const spinnerWrapper = document.querySelector('.spiner-wrapper');
let rootUlElem = document.querySelector('#objects-root');
let objects = null;
const initPage = (objects) => __awaiter(void 0, void 0, void 0, function* () {
    var p = { placement: "bottom-end", modifiers: [{ name: "offset", options: { offset: [0, 4] } }] };
    const initObjects = (objects, parentUI) => {
        for (const obj_name in objects) {
            let li = document.createElement('li');
            let record = makeObjectRecord(objects[obj_name]);
            li.appendChild(record);
            li.classList.add('relative', 'w-fit', 'object-record');
            if ('childs' in objects[obj_name]) {
                let ul = document.createElement('ul');
                ul.classList.add('hidden');
                ul.setAttribute('id', `childs-for-${objects[obj_name]['id']}`);
                li.appendChild(ul);
                if (parentUI.id !== 'objects-root') {
                    li.classList.add('left-3');
                }
                parentUI.appendChild(li);
                console.log(li.tagName);
                new Popper(`#cardMenu${objects[obj_name]['id']}`, ".popper-ref", ".popper-root", p, li);
                initObjects(objects[obj_name].childs, ul);
            }
            else {
                if (parentUI.nodeName === 'UL' && parentUI.id !== 'objects-root') {
                    li.classList.add('left-3');
                }
                parentUI.appendChild(li);
                new Popper(`#cardMenu${objects[obj_name]['id']}`, ".popper-ref", ".popper-root", p, li);
            }
        }
    };
    objects = yield getObjects();
    console.log(objects);
    initObjects(objects, rootUlElem);
    spinnerWrapper.classList.add('hidden');
    addListenerForChildsField();
});
const makeObjectRecord = (object) => {
    const deleteURL = `delete_object/${object['id']}`;
    const editURL = `object_edit/${object['id']}`;
    const deleteRelURL = object['relation_id'] === '#' ? '#' : `delete_relation/${object['relation_id']}`;
    let elem = document.createElement('div');
    elem.classList.add('card', 'w-80', 'mt-2', 'p-4');
    let devices = object['devices'].map(dev => {
        let devName = dev['device_name'];
        let devUrl = '/devices/' + dev['id'];
        let devUrlDel = '/objects/' + object['id'] + '/delete_device/' + dev['id'];
        if (devName !== 'Have not devices') {
            return `
            <div class="tag rounded-full bg-warning/10 text-warning hover:bg-warning/20 focus:bg-warning/20 active:bg-warning/25 d-flex justify-content-between">
                <a class="pr-2" href=${devUrl}>${devName}</a>
                <span>|</span> 
                <a class="pl-2" href=${devUrlDel}>x</a>
            </div>`;
        }
    }).join('');
    let childs = ``;
    if (object.childs) {
        childs = `
        <div class="mt-3 grid grid-cols-1 gap-2">
            <button  id="childs-for-${object.id}" class="btn ptn-primary childs-field px-2 space-x-2 bg-primary font-medium text-white hover:bg-primary-focus focus:bg-primary-focus active:bg-primary-focus/90 dark:bg-accent dark:hover:bg-accent-focus dark:focus:bg-accent-focus dark:active:bg-accent/90">
                Childs
            </button>
        </div>`;
    }
    let objectHTML = `
        <div class="flex justify-between items-center">
            <h3 class=" text-lg font-medium text-slate-700 dark:text-navy-100">
                <a href="/objects/object_info/${object['id']}" class="flex h-8 items-center px-3 pr-8 font-medium tracking-wide outline-none transition-all  hover:text-slate-800 dark:focus:bg-navy-600 focus:text-slate-800  dark:hover:text-navy-100  dark:focus:text-navy-100">${object.name}  </a>
            </h3>

            <div id="cardMenu${object.id}">
                <button class="popper-ref btn h-8 w-8 rounded-full p-0 hover:bg-slate-300/20 focus:bg-slate-300/20 active:bg-slate-300/25 dark:hover:bg-navy-300/20 dark:focus:bg-navy-300/20 dark:active:bg-navy-300/25">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z"></path>
                </svg>
                </button>

                <div class="popper-root" data-popper-placement="bottom-end" style="position: absolute; inset: 0px 0px auto auto; margin: 0px; transform: translate3d(-8px, 44px, 0px);">
                    <div class="popper-box rounded-md border border-slate-150 bg-white py-1.5 font-inter dark:border-navy-500 dark:bg-navy-700">
                        <ul>
                            <li>
                                <a href="${editURL}" class="flex h-8 items-center px-3 pr-8 font-medium tracking-wide outline-none transition-all hover:bg-slate-100 hover:text-slate-800 focus:bg-slate-100 focus:text-slate-800 dark:hover:bg-navy-600 dark:hover:text-navy-100 dark:focus:bg-navy-600 dark:focus:text-navy-100">Edit</a>
                            </li>
                            <li>
                                <a href="${deleteURL}" class="flex h-8 items-center px-3 pr-8 font-medium tracking-wide outline-none transition-all hover:bg-slate-100 hover:text-slate-800 focus:bg-slate-100 focus:text-slate-800 dark:hover:bg-navy-600 dark:hover:text-navy-100 dark:focus:bg-navy-600 dark:focus:text-navy-100">Delete</a>
                            </li>
                            <li>
                                <a href="add_device/${object.id}" class="flex h-8 items-center px-3 pr-8 font-medium tracking-wide outline-none transition-all hover:bg-slate-100 hover:text-slate-800 focus:bg-slate-100 focus:text-slate-800 dark:hover:bg-navy-600 dark:hover:text-navy-100 dark:focus:bg-navy-600 dark:focus:text-navy-100">Add device</a>
                            </li>
                            <li>
                                <a href="${deleteRelURL}" class="flex h-8 items-center px-3 pr-8 font-medium tracking-wide outline-none transition-all hover:bg-slate-100 hover:text-slate-800 focus:bg-slate-100 focus:text-slate-800 dark:hover:bg-navy-600 dark:hover:text-navy-100 dark:focus:bg-navy-600 dark:focus:text-navy-100">Delete from reletaion</a>
                            </li>
                        </ul>
                    </div>
                </div>
                
            </div>
        </div>

        <div class="flex grow flex-col items-center  sm:px-5">

            <div class="inline-space mt-3 flex grow flex-wrap ">
                ${devices}
            </div>

            <div class="flex justify-between">
                ${childs}
            </div>
            
        </div>`;
    elem.insertAdjacentHTML('beforeend', objectHTML);
    return elem;
};
const getObjects = () => __awaiter(void 0, void 0, void 0, function* () {
    let response = null;
    try {
        response = yield fetch(dataUrlObjectsInHierarchy);
        if (!response.ok) {
            const message = `An error has occured: ${response.status}\n ${yield response.text()}`;
            throw new Error(message);
        }
        return response.json();
    }
    catch (error) {
        alert(error);
    }
    return null;
});
const addListenerForChildsField = () => {
    let childsFileds = document.querySelectorAll('.object-record');
    childsFileds.forEach(el => {
        el.addEventListener('click', toggleChildsField);
    });
};
const toggleChildsField = (event) => {
    event.stopPropagation();
    const currentTarget = event.currentTarget;
    const target = event.target;
    if (target.innerText !== 'Childs') {
        return;
    }
    const childsUl = currentTarget.querySelector(`ul[id='${target.id}']`);
    childsUl === null || childsUl === void 0 ? void 0 : childsUl.classList.toggle('hidden');
};
initPage(objects);
