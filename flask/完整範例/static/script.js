$(document).ready(function () {
    // 處理登入
    $('#loginForm').submit(function (event) {
        event.preventDefault();
        $.post('/login', $(this).serialize(), function (data) {
            $('#loginMessage').text(data.message);
            if (data.success) {
                setTimeout(() => location.reload(), 1000);
            }
        });
    });

    // 處理註冊
    $('#registerForm').submit(function (event) {
        event.preventDefault();
        $.post('/register', $(this).serialize(), function (data) {
            $('#registerMessage').text(data.message);
        });
    });

    

    // 處理圖片上傳
    $('#uploadForm').submit(function (event) {
        event.preventDefault();
        var formData = new FormData(this);
        
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (data) {
                $('#uploadMessage').text(data.message);
                if (data.success) {
                    $('body').append('<p>上傳成功: ' + data.filename + '</p>');
                }
            }
        });
    });
});
