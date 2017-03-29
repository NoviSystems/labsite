$('document').ready(function() {
    var modal = $('#action-modal');

    modal.on('show.bs.modal', function actionModalListener(event) {
        // Button that triggered the modal
        var trigger = $(event.relatedTarget);

        var form = trigger.closest('form');
        var button = modal.find('.modal-footer button');

        // Display text setup
        var title = trigger.data('title');
        var body = trigger.data('body');
        var buttonClass = trigger.data('btn-class');
        var buttonText = trigger.data('btn-text');

        modal.find('.modal-title').html(title);
        modal.find('.modal-body-text').html(body);
        button.addClass(buttonClass);
        button.html(buttonText);

        // form copy
        var action = form.attr('action');

        modal.find('.modal-footer form').attr('action', action);

        // submit value copy
        var name = trigger.attr('name');
        var value = trigger.attr('value');

        button.attr('name', name);
        button.attr('value', value);
    });
});
