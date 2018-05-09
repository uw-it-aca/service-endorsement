// javascript handling clipboard copying

var copy_clipboard = function ($node) {
    var url = $node.attr('data-clipboard'),
        msg = $node.attr('data-clipboard-msg'),
        $txt;

    $txt = $('<input>')
        .css('position', 'absolute')
        .css('left', '-2000px')
        .val(url)
        .appendTo(document.body);
    $txt.select();
    document.execCommand('copy');
    $txt.remove();
    notify(msg);
};
