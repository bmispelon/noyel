$(function (){
    $('input[name=giftee]').attr('autocomplete', 'off').typeahead({
        'source': function (query, process) {
            return $.get('/api/search/giftee/', {'q': query}, function (data) {
                return process(data)
            });
        }
    });
    $('form.invite input[name=user]').attr('autocomplete', 'off').typeahead({
        'source': function (query, process) {
            return $.get('/api/search/friend/', {'q': query}, function (data) {
                return process(data)
            });
        }
    });
});
