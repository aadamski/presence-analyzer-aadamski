function parseInterval(value) {
    var result = new Date(1,1,1);
    result.setMilliseconds(value*1000);
    return result;
}

(function($) {
    $(document).ready(function(){
        $('#user_id').change(function(){
            var avatar = $("#avatar");
            avatar.attr('src', $("#user_id option:selected").attr('data-avatar'))
        });
        var loading = $('#loading');
        $.getJSON("/api/v1/users", function(result) {
            var dropdown = $("#user_id");
            $.each(result, function(item) {
                dropdown.append($("<option />")
                    .val(this.user_id)
                    .text(this.info.name)
                    .attr('data-avatar', this.info.avatar));
            });
            dropdown.show();
            loading.hide();
        });
    });
})(jQuery);
