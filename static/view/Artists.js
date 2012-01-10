Ext.define('jf.view.Artists', {
    extend: 'jf.view.GridPanel',
    alias: 'widget.artists',
    title: 'Artists',
    store: 'Artists',
    stateId: 'widget.artists',
    hideHeaders: true,
    verticalScroller: {
        xtype: 'paginggridscroller'
    },
    columns: [{
        xtype: 'rownumberer'
    }, {
        dataIndex: 'name',
        flex: true
    }],
    dockedItems: [{
        xtype: 'toolbar',
        dock: 'top',
        items: [{
            xtype: 'textfield',
            name: 'artistFilter',
            hideLabel: true,
            displayField: 'name',
            width: 220
        }, {
            xtype: 'button',
            name: 'artistFilterButton',
            iconCls:'icon-zoom'
        }]
    }],
    onSearch: function(){
        console.log(this);
    }
});


