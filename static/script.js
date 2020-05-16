$(document).ready(function() {
    
    let input = document.querySelector('input.form-control[name="username"]');
    input.onkeyup = function() {
    $.get('/check', { username: input.value }, function(data) {
            if (data === true) {
                input.style.borderColor = "green";
            }
            else if (data === false) {
                input.style.borderColor = "red";
                document.querySelector('form').onsubmit = function() {
                    return false;
                };
            }
        });
    };
});

