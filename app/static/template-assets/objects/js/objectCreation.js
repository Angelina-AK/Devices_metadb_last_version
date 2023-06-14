import { resources } from "/static/template-assets/global.js"

const addObjectBtn = document.getElementById('add-object')

// const dataUrlAttributes = resources['baseURL'] + '/attributes/get_all'
const dataUrlObjects = resources['baseURL'] + '/objects/get_all'
const dataUrlTypes = resources['baseURL'] + '/types/get_all'


const btnWrapperTopLevel  = document.getElementById('top-level-wrapper') //для вставки перед кнопкой ногово объекта ребенка

let childObjects = []
let types = []
let datalistChildObjects = ``
let childInputsCount = 0


const initPage = async (childObjects, types, datalistChildObjects) => {

  childObjects = await fetchObjects()
  types = await fetchTypes(dataUrlTypes)
  datalistChildObjects = generateDalatisChilds(childObjects)

  generateBrowserInputTypes(types)
  addListenerTypeInput(types)

  generateBrowserInputChilds(datalistChildObjects, childObjects )

  addObjectBtn.addEventListener('click', () => {
    generateBrowserInputChilds(datalistChildObjects, childObjects)
  })

  document.querySelector("#submit-btn").classList.remove('disabled')
}


const generateBrowserInputChilds = (datalistChildObjects, childs) => {

  return () => {
    let childInput = `
    <div class="col-12">
      <div class="mb-1 row">
        <div class="col-sm-3 ">
          <label class="col-form-label" for="browser-obj">Select child object </label>
        </div>
        <div class="col-sm-9">
          <input class="form-control" list="browsers-obj" name="child-object-name" id="input-childs-${childInputsCount}" autocomplete="off" placeholder="Child object">
        </div>
        <datalist id="browsers-obj">
        ${datalistChildObjects}
        </datalist>
      </div>
    </div>
    `
    debugger
    document.querySelector('#top-level-wrapper').insertAdjacentHTML('beforebegin', childInput)
    const inputListener = document.querySelector(`#input-childs-${childInputsCount}`)
    inputListener.addEventListener('change', (event) => isCorrectInputChild(event, childs))
    childInputsCount++
  }
}

const generateBrowserInputTypes = (types)=>{
  let listItems = ``
  for (const key in types){
    listItems += `<option value="${types[key].type_name}">\n`
  }
  document.querySelector('#browsers-types').innerHTML = listItems
}


const fetchObjects = async () => {
  return ( await fetch(dataUrlObjects) ).json()
}


const fetchTypes = async (dataUrlTypes) => {
  return ( await fetch(dataUrlTypes) ).json()
}


const addListenerTypeInput = (types) => {
  let input = document.querySelector('#browser-types')
  input.addEventListener('change', e =>{
    generateAttributes(e.target.value, types)
  })
}


const generateAttributes = (type, types) => {
  let attributesWrapper = document.querySelector('#attrs-wrapper')
  attributesWrapper.innerHTML = ''
  debugger
  if ( ! (types.find(el => el['type_name'] == type) ) ){
    return
  }

  let attributes = types.find(el => el['type_name'] == type)['attributes']
  console.log(attributes, types)
  debugger
  let atrtibutesInputs = document.createElement('div')
  attributes.forEach(e => {
    let attributeInput = `
    <div class="mb-1 row">
        <div class="col-sm-3 ">
           <label class="col-form-label" for="${e}">${e}</label>
       </div>
    
       <div class="col-sm-9">
           <input class="form-control" name="attr-${e}" placeholder="Value">
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
  // console.log(event.target.value, childs)
  
}

const generateDalatisChilds = (childObjects) => {
  // debugger
  let datalist = ''
  for (const key in childObjects){
    datalist += `<option value="${childObjects[key].name}">\n`
  }
  return datalist
}

initPage(childObjects, types, datalistChildObjects)