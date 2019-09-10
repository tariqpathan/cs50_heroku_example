let username = document.querySelector('username');
input.onkeyup = function() {
    $.get('/check?username=' + username.value, function(data) {
    });
};

