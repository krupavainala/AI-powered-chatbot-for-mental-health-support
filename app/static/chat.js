$('#userInput').keypress(function(e) {
    if (e.which === 13) {
        $('#sendButton').click();
    }
});
