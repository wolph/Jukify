Ext.define('jf.view.Viewport', {
    extend: 'Ext.container.Viewport',
    layout: 'fit',
    stateful: true,
    stateId: 'viewport',
    requires: [
        'jf.view.Queue',
        'jf.view.Artists'
    ],
    initComponent: function(){
        this.items = {
            dockedItems: [{
                dock: 'top',
                xtype: 'toolbar',
                height: 160,
                id: 'logo'
            }],
            layout: {
                type: 'border'
            },
            items: [{
                xtype: 'artists',
                region: 'west',
                collapsible: true,
                width: 250,
                split: true
            }, {
                xtype: 'queue',
                region: 'center'
            }]
        };

        this.callParent();
    }
});

