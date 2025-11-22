$(document).ready(function() {
    $('#loginForm').submit(function(e) {
        e.preventDefault();
        let formData = $(this).serialize();
        $.ajax({
            type: 'POST',
            url: '/api/admin/login',
            data: formData,
            beforeSend: function () {
                $("#loginForm button[type=submit]").prop("disabled", true);
            },
            success: function(response) {
                swal("Done!",response.message,"success")
                setTimeout(() => {
                    window.location.href = '/admin/panel/home';
                }, 1000);
            },
            error: function(xhr, status, error) {
                swal("Error!",xhr.responseJSON.error,"error")
            },
            complete:function (){
                setTimeout(function (){
                    $("#loginForm button[type=submit]").prop("disabled", false);
                },1000)
            }
        });
    });
});


