$(document).ready(function(){
	console.log('delete initialized');

	var url = window.location.href;

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
				console.log('success');
			},
			failure: function(data){
				console.log('failure to delete');
			},
		});
		
		window.location.href = url;
	});
});