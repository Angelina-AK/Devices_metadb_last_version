import { resources } from "/static/template-assets/global.js"

const addObjectBtn = document.getElementById('add-object')
let objectsWrapper = document.getElementById('objects-wrapper')
const dataUrlObjectsInHierarchy = resources['baseURL'] + '/objects/get_json_all_objects'
const spinnerWrapper = document.querySelector('.spiner-wrapper')
let rootUlElem = document.querySelector('#objects-root')
let objects = {}


const initPage = async (objects) =>{
    objects = await getObjects(objects)
    console.log(objects)
    // initObjects(objects, objectsWrapper)
    initObjects(objects, rootUlElem)
    spinnerWrapper.classList.add('d-none')
    addListenerForChildsField()
    //draw feather icons
    feather.replace()
}

const makeObjectRecord = (object) =>{
    const deleteURL = 'delete_object/'
    const editURL = 'edit_object/'
    const viewObject = 'view_object/'

    let elem = document.createElement('div')
    elem.classList.add('card', 'col-xl-6', 'col-lg-8', 'col-md-8', 'col-sm-8', 'col-12', 'text-break') 
    // elem.classList.add('card', 'w-50', 'text-break') 
    debugger
    let attributes = object['attributes'].map( atr =>{
        const key = Object.keys(atr)
        return `
        <div class="d-flex  justify-content-between">
            <div class="alert-body">
                ${key}
            </div>

            <div class="alert-body">
                ${atr[key]}
            </div>
        </div>
        `
    }).join('')
    
    let devices = object['devices'].map( dev =>{

        const key = Object.keys(dev);
        let devName = dev['device_name'];
        let devUrl = '/devices/'+dev['id'];
        let devUrlDel = '/objects/'+object['id']+'/delete_device/'+dev['id'];
        return `
            <div class="alert-body d-flex justify-content-between">
                ${ devName === 'Have not devices' ? 
                `<span> ${devName} </span>` :
                `<a href=${devUrl}> ${devName}  </a>`}

                ${ devName === 'Have not devices' ? 
                ``:
                `<a href=${devUrlDel}> Delete </a>`}
            </div>
        `
    }).join('')

    debugger
    let objectHTML = `
        <div class="card-header">
            <a class="card-title text-primary" href="#"> ${object['name']}</a>

            <div class="dropdown">
                  <button type="button" class="btn btn-sm dropdown-toggle hide-arrow py-0 waves-effect waves-float waves-light" data-bs-toggle="dropdown">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-more-vertical"><circle cx="12" cy="12" r="1"></circle><circle cx="12" cy="5" r="1"></circle><circle cx="12" cy="19" r="1"></circle></svg>
                  </button>
                  <div class="dropdown-menu dropdown-menu-end">
                        <a class="dropdown-item" href="${editURL + object['id']}">
                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-edit-2 me-50"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path></svg>
                            <span>Edit</span>
                        </a>
                        <a class="dropdown-item" href="${deleteURL + object['id']}">
                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-trash me-50"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            <span>Delete</span>
                        </a>
                  </div>
                </div>
            </div>
        </div>

        <div class="card-body ">
            
            <div class="demo-spacing-0">
                
                <div class="alert alert-info" role="alert">
                    <h4 class="alert-heading">Type</h4>
                    <div class="alert-body">
                        ${object['object_type']}
                    </div>
                </div>

                <div class="alert alert-info" role="alert">
                    <h4 class="alert-heading">Attributes</h4>
                        ${attributes}
                </div>

                <div class="alert alert-info" role="alert">
                    <h4 class="alert-heading">Devices</h4>
                        ${devices}
                </div>


                <div class="d-flex mb-1 justify-center">
                    <a class="mx-auto btn btn-warning waves-effect waves-float waves-light" href="add_device/${object['id']}">Add device</a>

                    <a class="mx-auto btn btn-secondary waves-effect waves-float waves-light" 
                    href="${object['relation_id'] === '#' ? '#' : 'delete_relation/' + object['relation_id']}">Delete relation</a>
                </div>

            </div>
        </div>
    `
    elem.insertAdjacentHTML('beforeend', objectHTML)
    return elem
}

const makeChildsFild = (record, id) =>{
    let childsField = document.createElement('div')
    childsField.classList.add('alert', 'alert-info', 'cursor-pointer', 'childs-field')
    childsField.setAttribute('id', id)

    const childHTML =  `
        <div class="alert-body d-flex justify-content-between align-items-center ">
            <span class="menu-item text-truncate">Childs</span>
            <div class="feather-icon"> 
                <i data-feather="arrow-right"></i>
            </div>
        </div>
    `
    childsField.insertAdjacentHTML('beforeend', childHTML)
    let objectAtrWrapper = record.querySelector('.demo-spacing-0')
    objectAtrWrapper.appendChild(childsField)
}

const getObjects = async () =>{
    return ( await fetch(dataUrlObjectsInHierarchy) ).json()
}


const initObjects = (object, parentUI) => {
    for (const key in object){
        if ('childs' in object[key]) {
            let li = document.createElement('li')
            let ul = document.createElement('ul')
            let record = makeObjectRecord(object[key])

            makeChildsFild(record, `childs-for-${object[key]['id']}`)
            li.appendChild(record)

            ul.classList.add('list-unstyled', 'd-none')
            ul.setAttribute('id', `childs-for-${object[key]['id']}`)
            li.classList.add('position-relative')

            li.appendChild(ul)
            if (parentUI.id !== 'objects-root'){
                li.classList.add('margin-for-element-card')
            }

            parentUI.appendChild(li)
            initObjects(object[key]['childs'], ul)
        }
        else {
            let li = document.createElement('li')
            if (parentUI.nodeName === 'UL' && parentUI.id !== 'objects-root'){
                li.classList.add('margin-for-element-card')
            }
            li.classList.add()
            li.classList.add('position-relative')
            let record = makeObjectRecord(object[key])
            li.appendChild(record)
            parentUI.appendChild(li)
        }       
    }
}


const addListenerForChildsField = () =>{
    let childsFileds = document.querySelectorAll('.childs-field')
    childsFileds.forEach(el => {
        el.addEventListener('click', toggleChildsField)
    })
    
}

const toggleChildsField = (event) =>{
    let arrow = event.currentTarget.querySelector('.feather-icon')
    let childsId = event.currentTarget.id
    let childsUl = document.querySelector(`ul[id=${childsId}]`)
    arrow.classList.toggle('rotate-90')
    childsUl.classList.toggle('d-none')
}

initPage(objects)