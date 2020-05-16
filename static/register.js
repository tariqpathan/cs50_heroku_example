$(document).ready(function() {
    
    let r_username = $('#register_username');
    let r_password = $('#register_password');
    let r_confirmation = $('#register_confirmation');
    checkFormValid();

    r_username.keyup(function() {
        if (r_username[0].checkValidity() === false) {
            $('#error-text').text("Type in a username - minimum 4 characters");
            r_username.css('borderColor', 'red');
        }
        
        $.get('/check', { username: r_username.val() }, function(data) {
            if (data === true && r_username[0].checkValidity() === true) {
                r_username[0].setCustomValidity('');
                r_username.css('borderColor', 'green');
                $('#error-text').empty();
                checkFormValid();

            } else if (data === false) {
                r_username[0].setCustomValidity('Username taken');
                r_username.css('borderColor', 'red');
                $('#error-text').text("Username unavailable");

            }
        });
    });

    r_password.keyup(function() {
        if (r_password[0].checkValidity() === false) {
            $('#error-text').text("Type in a password - minimum 4 characters");
        } else if (r_password[0].checkValidity() === true) {
            $('#error-text').empty();
            checkFormValid();
        }
    });

    r_confirmation.keyup(function() {
        if (r_password.val() !== r_confirmation.val()) {
            r_confirmation[0].setCustomValidity('Password Mismatch');
            $('#error-text').text("Passwords do not match");
        } else if (r_password.val() === r_confirmation.val()) {
            r_confirmation[0].setCustomValidity('');
            $('#error-text').empty();
            checkFormValid();
        }
    });
    
    // called every time an element becomes valid
    function checkFormValid() {
        if ($('form')[0].checkValidity() === false) {
            $('#register_button')[0].disabled = true;
        } else if ($('form')[0].checkValidity() === true) {
            $('#register_button')[0].disabled = false;
            $('#error-text').text("All good :)");
            $('#error-text').css('color', 'green');
        }
    }
});