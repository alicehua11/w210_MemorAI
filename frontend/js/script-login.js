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
            case "sarah": 
                setTimeout(function(){document.location = "main-alex.html"},500);
                break;
            case "robert": 
                setTimeout(function(){document.location = "main-robert.html"},500);
                break;
            default:
                $("#container_form_message").text("Wrong username or password...");
        }
    });
}