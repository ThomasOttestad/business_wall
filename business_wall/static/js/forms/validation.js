function insertErrors(formId, errors) {
  for (const [key, errorList] of Object.entries(errors)) {
    if (key !== "__all__") {
      $(`${formId} #id_${key}`).addClass("is-invalid");
    }
    errorList.forEach((errorText) => {
      if (key !== "__all__") {
        $(`${formId} #id_${key}-errors`).append($(`<li>${errorText}</li>`));
      } else {
        $(`${formId} #__all__`).append($(`<li>${errorText}</li>`));
      }
    });
  }
}

function removeErrors(formId) {
  $(`${formId} .invalid-feedback > ul`).empty();
  $(`${formId} #__all__`).empty();
  $(`${formId} .is-invalid`).removeClass("is-invalid");
}

function resetForm(formId) {
  $(formId)[0].reset();
  removeErrors(formId);
}

function setAlert(alertWrapperId, message, type) {
  const $alert = $(`
    <div class="alert alert-${type} fade show" role="alert" style="position: absolute; bottom: 0; left: 40%; z-index: 5;">
      ${message}
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  `);

  $(alertWrapperId).append($alert);
  setTimeout(() => $alert.alert('close'), 2000);
}
