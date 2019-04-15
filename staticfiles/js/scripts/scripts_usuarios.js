$(document).ready(function() { 

$("#checkall").click (function () {
     var checkedStatus = this.checked;
    $("input[name='permisos']").each(function () {
        $(this).prop("checked", checkedStatus);
        $(this).change();
     });
  });

});

