Ext.define('jf.controller.Queue', {
    extend: 'Ext.app.Controller',
    stores: [
        'Queue'
    ],
    refs: [{
        ref: 'queue',
        selector: 'queue'
    }]
});

