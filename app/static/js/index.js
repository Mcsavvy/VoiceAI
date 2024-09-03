document.body.addEventListener('htmx:responseError', event => Toastify({text: event.detail.xhr.responseText}).showToast())
