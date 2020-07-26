function updateToggleDelayed(toggleId, visibilityId, parent = true) {
    setTimeout(function(){ updateToggle(toggleId, visibilityId, parent); }, 500);
}

function updateToggle(toggleId, visibilityId, parent = true) {
    if (document.querySelector(`#${toggleId}`).checked) {
        if (parent) {
            document.querySelector(`#${visibilityId}`).parentElement.style.display = "flex";
        } else {
            document.querySelector(`#${visibilityId}`).style.display = "flex";

        }
    } else{
        if (parent) {
            document.querySelector(`#${visibilityId}`).parentElement.style.display = "none";
        } else {
            document.querySelector(`#${visibilityId}`).style.display = "none";
        }
    }
}