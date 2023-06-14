import { resources } from "../global.js"

const deleteUrl = resources.baseURL + '/objects/attribute_delete/'

const initPage = async () => {
    addListeners()
} 

const deleteAttribute = async (url, id) => {
    await fetch(url + id, {
        method: 'DELETE',
      })
      location.reload()
}

const addListeners =  () => {
    const deleteButtons = document.querySelectorAll('.detele-attribute-btn')
        deleteButtons.forEach(e => {
        e.addEventListener('click', () => {
            deleteAttribute(deleteUrl, e.id)
        })
    })
}

initPage()