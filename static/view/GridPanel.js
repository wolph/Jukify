
Ext.define('jf.view.GridPanel', {
    extend: 'Ext.grid.Panel',
    iconCls: 'icon-grid',
    mixins: {
        stateful: 'jf.view.StatefulPanelMixin'
    }
});

