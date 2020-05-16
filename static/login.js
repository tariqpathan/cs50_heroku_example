$(document).ready(function() {
    
    let username = $('#username');
    let password = $('#password');
    checkFormValid();

    username.keyup(function() {
        if (username[0].checkValidity() === false) {
            $('#error-text').text("Type in your username");
        } else if (username[0].checkValidity() === true) {
            $('#error-text').empty();
            checkFormValid();
        }
    });

    password.keyup(function() {
        if (password[0].checkValidity() === false) {
            $('#error-text').text("Type in your password");
        } else if (password[0].checkValidity() === true) {
            $('#error-text').empty();
            checkFormValid();
        }
    });

    $('form').submit(function(e) {
        e.preventDefault();
        $.post('/login', { username: username.val(), password: password.val() }, function(data) {
            console.log(data);
            if (data === false) {
                $('form')[0].reset();
                $('#error-text').text("Username/Password incorrect");
                username[0].focus();
                checkFormValid();
                return false;
            } else if (data === true) {
                location.href=("/");
            }
        });
    });
    
    function checkFormValid() {
        if ($('form')[0].checkValidity() === false) {
            $('#login_button')[0].disabled = true;
        } else if ($('form')[0].checkValidity() === true) {
            $('#login_button')[0].disabled = false;
            $('#error-text').empty();
        }
    }
});