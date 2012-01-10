var config;

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    function update_on_air(data){
        console.log(data);
    }

    config = {
        type: 'POST',
        url: '/remote/',
        success: update_on_air,
        dataType: "json"
    };

    var command_map = {
        'next': 'next_'
    };

    $('button.command').click(function() {
        jQuery.ajax($.extend(config, {
            data: {
                'command': command_map[this.value] || this.value
            }
        }));
    });

    $(".track_link").click(function(){
        jQuery.ajax($.extend(config, {
            data: {
                command: 'queue',
                playlist: $(this).attr('id').split(':')[0],
                track: $(this).attr('id').split(":")[1]
            },
        }));
    });
});
