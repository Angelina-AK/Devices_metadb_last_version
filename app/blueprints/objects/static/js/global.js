export const resources = {
    'baseURL': window.location.origin,
};
export const disableInput = (e) => {
    const disableBtn = e.target;
    if (disableBtn.innerText != 'x') {
        return;
    }
    const input = disableBtn.previousSibling.previousSibling;
    input.disabled === true ? input.disabled = false : input.disabled = true;
    if (input.placeholder === 'Type name') {
        //^ - mean name start with = attr-*
        const attrsInputs = document.querySelectorAll('input[name^="attr"]');
        if (input.disabled) {
            attrsInputs === null || attrsInputs === void 0 ? void 0 : attrsInputs.forEach(e => {
                e.disabled = true;
            });
        }
        else {
            attrsInputs === null || attrsInputs === void 0 ? void 0 : attrsInputs.forEach(e => {
                e.disabled = false;
            });
        }
    }
    return;
};
