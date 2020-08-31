window.addEventListener("load", function() {
  (function($) {
    // Replace the file link (that doesn't go anywhere), with some text
    fileName = $('.field-upload a').text();
    $('.field-upload a').replaceWith("<span>" + fileName + "</span>");

    // Url copy button functionality
    $('#copy-url-button').click(function() {
      $urlElement = $('#hitchcock-url');
      copyToClipboard($urlElement);
      $urlElement.animate({
        opacity: 0.1,
      }, 100, function() {
        $urlElement.animate({
          opacity: 1,
        }, 100)
      });
      return false;
    });

    function copyToClipboard(element) {
      var $temp = $("<input>");
      $("body").append($temp);
      $temp.val($(element).text()).select();
      document.execCommand("copy");
      $temp.remove();
    }

  })(django.jQuery);
});
