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


$("input:checkbox").on('click', function() {
    var $box = $(this);
    if ($box.is(":checked")) {
      var group = "input:checkbox[name='" + $box.attr("name") + "']";
      $(group).prop("checked", false);
      $box.prop("checked", true);
    } else {
      $box.prop("checked", false);
    }
});
