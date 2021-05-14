document.getElementById('select-age-all').onclick = function() {
    var inputs = document.getElementsByTagName('input');
    for (var input of inputs) {
        if(input.name.startsWith('vek_')) {
            input.checked = this.checked;
        }
    }
}


document.getElementById('select-psc-all').onclick = function() {
    var inputs = document.getElementsByTagName('input');
    for (var input of inputs) {
        if(input.name.startsWith('psc_')) {
            input.checked = this.checked;
        }
    }
}
