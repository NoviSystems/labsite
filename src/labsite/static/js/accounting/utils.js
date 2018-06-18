
['Arguments', 'Function', 'String', 'Number', 'Date', 'RegExp'].forEach(
    function(name) {
        window['is' + name] = function(obj) {
              return toString.call(obj) == '[object ' + name + ']';
    };
});
