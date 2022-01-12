// configs
var TYPEWRITER_SPEED = 50;
var TYPEWRITER_DELETE_SPEED = 25;
var API_MEMORAI = "https://www.alexdomain.xyz:8000/alex_gpt/";
var USERNAME = "there";
var GREETING = "Hello " + USERNAME + "! " + "I'm just a bot, but you can ask me questions that you'd like to know how Alex would respond.";
var GREETING_DELAY = 1000;

$(document).ready(function() {
    $(".grid_item").css("opacity", "0");
    onDocReady();
});

function getTypewritter() {
    // REF: https://safi.me.uk/typewriterjs/
    // initialize typewriter
    var dialogue = document.getElementById('container_dialogue');
    var typewriter = new Typewriter(dialogue, {
        loop: false,
        delay: TYPEWRITER_SPEED,
        deleteSpeed: TYPEWRITER_DELETE_SPEED
    });

    return typewriter;
}

function shuffle(array) {
    let currentIndex = array.length,  randomIndex;
  
    // While there remain elements to shuffle...
    while (currentIndex != 0) {
  
      // Pick a remaining element...
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex--;
  
      // And swap it with the current element.
      [array[currentIndex], array[randomIndex]] = [
        array[randomIndex], array[currentIndex]];
    }
  
    return array;
}

function fadeInGridItems() {
    // show images
    var gridItems = $("#container_grid").children();
    gridItems = shuffle(gridItems)

    for (i = 0; i < gridItems.length; i++) {
        var t = Math.floor(Math.random() * 1000);
        $(gridItems[i]).delay(t).fadeIn();
    }
}
  

function onDocReady() {
    // greeting
    typewriter = getTypewritter()
    typewriter.pauseFor(GREETING_DELAY).typeString(GREETING).start();

    $("#button_ask").click(function() {
        // "reload" images; hide them
        $(".grid_item").fadeOut(0);

        // instantly clear typewriter output
        typewriter = getTypewritter()
        typewriter.typeString('Thinking...').start();

        // fetch question from form
        var question = $("#input_field_question").val();
        var question_parsed = question.split(" ").join("_");
        var question_to_send = API_MEMORAI + question_parsed;
        console.log(question_to_send); // log for debugging

        // query for answer
        const req = new XMLHttpRequest();
        req.open("GET", question_to_send, true);
        console.log(question_to_send);
        req.send();
        req.onreadystatechange = () => {
            if (req.readyState === 4 && req.status === 200) {
                // answer_1 = "It caught me the wrong way. . . . I was doing some stemming moves, pushing with both hands against the sides of the groove. I pushed just a little too hard and my left shoulder bumped the wall, so that I started to fall. Adrenaline shot from my toes right up to my head. . . . I was off and headed down. But the balance and flow of all the movement that had gone on until that point carried me through, keeping me on the rock and still moving."
                // answer_2 = "<br/><br/>With his sharp intelligence, Alex inclines toward a hyperrational take on life. He actually insists, \"I don't like risk. I don't like passing over double yellow. I don't like rolling the dice.\" He distinguishes between consequences and risk. Obviously, the consequences of a fall while free soloing are ultimate ones. But that doesn't mean, he argues, that he's taking ultimate risks. As he puts it..."
                var object = JSON.parse(req.response);
                console.log(req.response); // log for debugging
                console.log(object)
        
            typewriter = getTypewritter()
            typewriter.typeString('').start();
            typewriter.typeString(object["answer"]).start();

            // show images
            fadeInGridItems();
            }
        }
    });
    

    $(".q").click(function() {
        switch ($(this).text()) {
            case "climbing":
                $("#input_field_question").val("Why do you love climbing?");
                break;
            case "adventure":
                $("#input_field_question").val("What are some of your favorite adventures?");
                break;
            case "free solo":
                $("#input_field_question").val("Why did you free solo El Capitan in Yosemite?");
                break;
            case "fear":
                $("#input_field_question").val("How do you deal with fear when free soloing?");
                break;
            case "other":
                $("#input_field_question").val("What do you care about most?");
                break;
            default:
                $("#input_field_question").val("...");

        }
    });

    // REF: https://packery.metafizzy.co/
    $('#container_grid').imagesLoaded(function() {
        $('#container_grid').packery({
            itemSelector: '.grid_item',
            gutter: 0
        });
        $(".grid_item").fadeOut(0);
        $(".grid_item").css("opacity", "1");
        fadeInGridItems();
        
    });
}