$('document').ready(function(){
	$('a[data-toggle=modal], button[data-toggle=modal]').click(function(event) {
		var action = $(event.target).closest('form').attr('action');
		var dataModel = $(this).data('model');
		var bodyText = "";
		var buttonType = '';

		var actionState = getActionState(action);
		actionState.model = actionState.model.replace(/_/g, " ");

		if( actionState.verb == 'delete' ){
			bodyText = "Confirm deletion of " + actionState.model + " " + String(dataModel) + " and it's associated data.";
			buttonType = 'btn-danger';
		} else if ( actionState.verb == 'update' ) {
			bodyText = "Confirm update of " + String() + ".";
			buttonType = 'btn-success';
		}
		$('.modal-title').html("Confirm " + actionState.verb);
		$('.modal-footer form').attr('action', action);
		$('.modal-body-text').html(bodyText);
		$('.modal-footer button').addClass(buttonType);
		$('.modal-footer button').html(actionState.verb + " " + actionState.model);
	});

	function getActionState(action){
		var strAction = String(action);
		console.log(strAction)
		var pattern = new RegExp('/([a-z_]+)/([0-9]+)/(delete|update)/$');
		var actionArray = pattern.exec(strAction);
		return {
			'model' : actionArray[1],
			'pk' : actionArray[2],
			'verb' : actionArray[3],
		};
	}
});