Ext.define('jf.view.StatefulPanelMixin', {
    stateful: true,
    getState: function(){
        return {
            collapsed: this.collapsed
        };
    },
    stateEvents: ['collapse', 'expand']
});

