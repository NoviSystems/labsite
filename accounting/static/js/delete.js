$(document).ready(function(){

	function getCookie(name) {
	    var cookieValue = null;
	    if (document.cookie && document.cookie !== '') {
	        var cookies = document.cookie.split(';');
	        for (var i = 0; i < cookies.length; i++) {
	            var cookie = jQuery.trim(cookies[i]);
	            // Does this cookie string begin with the name we want?
	            if (cookie.substring(0, name.length + 1) === (name + '=')) {
	                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                break;
	            }
	        }
	    }
	    return cookieValue;
	}
	var csrftoken = getCookie('csrftoken');

	$(".btn-delete").click(function(event) {
		event.preventDefault();

		console.log('delete clicked: ' + this.href);

		$.ajax({
			type: 'POST',
			url: this.href,
			dataType: 'json',
			data: {
				csrfmiddlewaretoken: csrftoken,
			},
			success: function(data){
				window.location.reload();			
			},
			failure: function(data){
				console.log('shit broke');
			},
		});
		window.location.reload();
	});
});