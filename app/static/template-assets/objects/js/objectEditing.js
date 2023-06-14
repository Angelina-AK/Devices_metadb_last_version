import { resources } from "/static/template-assets/global.js"

let module =  ( async () => {
    const addObjectBtn = document.getElementById('add-object');

    const dataUrlObjects = resources['baseURL'] + '/objects/get_all_possible_childs/';
    const dataUrlTypes = resources['baseURL'] + '/types/get_all';
  
    let childObjects = [];
    let types = [];
    let datalistChildObjects = ``;
    let childInputsCount = 0;
    let id = null ;

  
  const generateBrowserInputChilds = () => {
    let childInput = `
      <div class="col-12">
        <div class="mb-1 row align-items-sm-center">
          <div class="col-sm-3 ">
            <label class="col-form-label" for="browser-obj-">Select child object </label>
          </div>
          <div class="col-sm-9 d-flex align-items-center">
            <input class="form-control" list="browsers-obj-dynamic" name="child-object-name" id="input-childs-${childInputsCount}" autocomplete="off" placeholder="Child object">
           
          </div>
          <datalist id="browsers-obj-dynamic">
           ${datalistChildObjects}
          </datalist>
        </div>
      </div>
      `
     // <div class="col-sm-1 cursor-pointer p-1 ">
     //   x
     // </div>

    document.querySelector('#top-level-wrapper').insertAdjacentHTML('beforebegin', childInput)
    const inputListener = document.querySelector(`#input-childs-${childInputsCount}`)
    // inputListener.addEventListener('change', (event) => isCorrectInputChild(event))
    childInputsCount++
  }
  
  const generateBrowserInputTypes = (types) => {
    let listItems = ``

    for (const key in types) {
      listItems += `<option value="${types[key].type_name}">\n`
    }
    document.querySelector('#browsers-types').innerHTML = listItems
  }

  
  const fetchObjects = async () => {
    const response = await fetch(dataUrlObjects + id);
    childObjects = await response.json();
    return childObjects;
  }

  const fetchTypes = async () => {
    const response = await fetch(dataUrlTypes);
    types = await response.json();
    return types;
  }
  
  const addListenerTypeInput = (types) => {
    let input = document.querySelector('#browser-types')
    input.addEventListener('change', e => {
      generateAttributes(e.target.value, types)
    })
  }
  
  
  const generateAttributes = (type, types) => {
    let attributesWrapper = document.querySelector('#attrs-wrapper')
    attributesWrapper.innerHTML = ''
    if (!(types.find(el => el['type_name'] == type))) {
      return
    }

    debugger;

    let attributes = types.find(el => el['type_name'] == type)['attributes']
    console.log(attributes, types)
    let atrtibutesInputs = document.createElement('div')
    attributes.forEach(e => {
      let attributeInput = `
      <div class="mb-1 row">
          <div class="col-sm-3">
             <label class="col-form-label" for="attr-${e}">${e}</label>
         </div>
      
         <div class="col-sm-9">
             <input class="form-control" name="attr-${e}" id="${e}" placeholder="Value">
         </div>
      </div>
      `
      atrtibutesInputs.innerHTML += attributeInput
    })
    attributesWrapper.appendChild(atrtibutesInputs)
  }
  
  const isCorrectInputChild = (event, childs) => {
    debugger
    const findedObject = childs.find(el => el['name'] === event.target.value)
    console.log(findedObject)
  }
  
  const generateDalatisChilds = () => {
    debugger
    childObjects.forEach(e => {
      datalistChildObjects += `<option value="${e}">\n`;
    });
    
  }
  

  const getObj =  () =>{
    return childObjects;
  }

  const getTypes = () =>{
    return types;
  }
   
  // init page
  id = document.querySelector('#object_id').textContent;
  id = id.slice(6, id.length - 2);

  await fetchObjects();
  await fetchTypes();
  console.log(types)
  generateDalatisChilds();
  generateBrowserInputChilds();
  generateBrowserInputTypes(types);
  addListenerTypeInput(types);

  document.querySelector("#submit-btn").classList.remove('disabled');

  addObjectBtn.addEventListener('click', () => {
    generateBrowserInputChilds(datalistChildObjects, childObjects);
  })


  return  {
    fetchObjects:  fetchObjects,
    fetchTypes: fetchTypes,
    generateDalatisChilds: generateDalatisChilds,
    
    getObj: getObj,
    getTypes:getTypes,
  }
})();






