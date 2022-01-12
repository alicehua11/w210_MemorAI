// configs
TYPEWRITER_SPEED = 50
TYPEWRITER_DELETE_SPEED = 25

$(document).ready(function () {
    onDocReady();
});

function onDocReady () {
    $("#button_login").click(function() { 
        var username = $("#form_login").find('input[name="username"]').val();
        switch(username.toLowerCase()) {
            default:
                $("#container_form_message").text("Wrong username or password!");
            case "alex": 
                setTimeout(function(){document.location = "p-alex.html"},500);
        }
    });
}

