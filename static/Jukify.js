function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    remote = "/remote/";
    $("#stop").click(function(){
        jQuery.ajax({
          type: 'POST',
          url: remote,
          data: {'command': 'stop'},
          success: update_on_air,
          dataType: "json"});
    });
    $("#next").click(function(){
        jQuery.ajax({
          type: 'POST',
          url: remote,
          data: {'command': 'next'},
          success: update_on_air,
          dataType: "json"});
    });
    $("#play").click(function(){
        var data = {'command': 'play'};
        jQuery.ajax({
          type: 'POST',
          url: remote,
          data: data,
          success: update_on_air,
          dataType: "json"});
    });
    $(".song_link").click(function(){
        var data = {'command': 'queue'};
        data["playlist"] = $(this).attr('id').split(":")[0];
        data["track"] = $(this).attr('id').split(":")[1];
        jQuery.ajax({
          type: 'POST',
          url: remote,
          data: data,
          success: update_on_air,
          dataType: "json"});
    });
    update_on_air = function(data){
        console.log(data);
    }
});
