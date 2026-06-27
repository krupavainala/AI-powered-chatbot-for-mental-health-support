$(document).ready(function () {
    $('#sendButton').click(function (event) {
        event.preventDefault();

        var userMessage = $('#userInput').val();
        if (userMessage.trim() === "") {
            alert("Please type a message!");
            return;
        }

        $('#chatBox').append('<div class="message user-message">' + userMessage + '</div>');
        $('#userInput').val('');

        $.ajax({
            url: '/send',  // ✅ This should match your Flask route
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: userMessage }),
            success: function (response) {
                $('#chatBox').append('<div class="message bot-message">' + response.reply + '</div>');
                $('#chatBox').scrollTop($('#chatBox')[0].scrollHeight);
            },
            error: function () {
                alert("Error sending message.");
            }
        });
    });
});
