$(document).ready(function() {
    var socket = io.connect('http://127.0.0.1:5000/home');
    socket.on('connect',function(){
            console.log("user has connected");
    });

    $('a[href="/logout"]').on('click',function(){
    socket.emit('on_disconnect')
    console.log("user has disconnected");
    socket.disconnect()
    });

    $("button[id^='send']").on('click', function(){
    message = $('#message'+id).val();
    if (message !=''){
    socket.emit('private_message', id, message);
    $('#message'+id).val('');
    }
    });

    $("button[id^='get_history']").on('click', function(){
    socket.emit('get_history', id);
    });

    var list_height = 0;

    socket.on('new_private_message', function(time, my_id, msg){
    $('#messages'+my_id).append('<li id="r_message">'+time+" - "+my_id+'</li>'+'<li id="r_message_text">'+msg+'</li>');
    console.log("Recipient received message from "+my_id+"messsage: "+msg);
    list_height = (list_height + 90);
    $("#messages" + id).animate({scrollTop: $('#r_message').offset().top + list_height},500);
    });

    socket.on('append_on_list', function(time, my_id,r_id, msg){
    $('#messages'+r_id).append('<li id="my_message">'+my_id+' - '+time+'</li>'+'<li id="my_message_text">'+msg+'</li>');
    console.log("appended");
    list_height = (list_height + 90);
    $("#messages" + id).animate({scrollTop: $('#my_message').offset().top + list_height},500);
    });

    socket.on('history_display', function(history){
    $('#messages'+id).empty();
    for (i=0; i<history.length;i++){
    var json =  history[i];
    var val = Object.values(json);
    var my_id = val[0];
    var r_id = val[1];
    var msg = val[2];
    var time = val[3];
    if (r_id == id){
        $('#messages'+r_id).append('<li id="my_message">'+my_id+' - '+time+'</li>'+'<li id="my_message_text">'+msg+'</li>');
        list_height = (list_height + 90);
        $("#messages" + id).animate({scrollTop: $('#my_message').offset().top + list_height}, 10);
        }
    else{
        console.log("wszedłem do elsa")
        $('#messages'+my_id).append('<li id="r_message">'+time+" - "+my_id+'</li>'+'<li id="r_message_text">'+msg+'</li>');
        list_height = (list_height + 90);
        $("#messages" + id).animate({scrollTop: $('#r_message').offset().top + list_height}, 10);
        }
    }
    });
    active_users = socket.on('update_active_users', function(active_users_){
         active_users= active_users_;
         console.log("update active users socket");
         return active_users
    });

    active_users = socket.on('update_users', function(active_users_){
         active_users= active_users_;
         console.log("update active users socket - disconnect");
         return active_users
    });

});

var dropdown = document.getElementsByClassName("dropdown-btn");
var i;

for (i = 0; i < dropdown.length; i++) {
  dropdown[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var dropdownContent = this.nextElementSibling;
    if (dropdownContent.style.display === "block") {
      dropdownContent.style.display = "none";
    } else {
      dropdownContent.style.display = "block";
    }
  });
}
var active_users = [];
function uptd_users(){
    for (i=0; i<users.length; i++){
        $('#'+users[i]).css("color", "#6c757d");
    }
    for (j=0; j<active_users.length;j++){
        $('#'+active_users[j]).css("color", "green");
    }
}




