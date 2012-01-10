Ext.define('QueueDragZone', {
    extend: 'Ext.view.DragZone',
    dragTemplate: new Ext.Template(
        '<b>{0} song{1}</b>',
        '<table>{2}</table>'),
    dragSongTemplate: new Ext.Template(
        '<tr>',
        '<td>{title:ellipsis(25)}</td>',
        '<td>{artist:ellipsis(25)}</td>',
        '<td>{album:ellipsis(25)}</td>',
        '</tr>',
        {compile: true}
    ),
    getDragText: function() {
        var records = this.dragData.records;
        var count = records.length;
        var songs = [];
        for(var i=0; i<count; i++){
            songs.push(this.dragSongTemplate.apply(records[i].data));
        }
        return this.dragTemplate.apply([
            count,
            count == 1 ? '' : 's',
            songs.join('')
        ]);
    }
});

Ext.define('QueueDragDropPlugin', {
    extend: 'Ext.grid.plugin.DragDrop',
    alias: 'plugin.queuedragdrop',
    onViewRender: function(view) {
        var me = this;

        if (me.enableDrag) {
            me.dragZone = Ext.create('QueueDragZone', {
                view: view,
                ddGroup: me.dragGroup || me.ddGroup,
                dragText: me.dragText
            });
        }

        if (me.enableDrop) {
            me.dropZone = Ext.create('Ext.grid.ViewDropZone', {
                view: view,
                ddGroup: me.dropGroup || me.ddGroup
            });
        }
    }
});

Ext.define('jf.view.Queue', {
    extend: 'jf.view.GridPanel',
    alias: 'widget.queue',
    title: 'Queue',
    store: 'Queue',
    stateId: 'widget.queue',
    multiSelect: true,
    viewConfig: {
        plugins: {
            ddGroup: 'queue',
            ptype: 'queuedragdrop'
        },
        listeners: {
            drop: function(node, data, dropRec, dropPosition){
                console.log('drop', arguments);
            }
        }
    },
    columns: [{
        dataIndex: 'title',
        header: 'Title',
        flex: true
    }, {
        dataIndex: 'artist',
        header: 'Artist',
        flex: true
    }, {
        dataIndex: 'album',
        header: 'Album',
        flex: true
    }],
    dockedItems: [{
        xtype: 'toolbar',
        items: [{
            iconCls: 'icon-add',
            text: 'Add'
        }, {
            iconCls: 'icon-delete',
            text: 'Delete',
            disabled: true,
            itemId: 'queue-item-delete'
        }]
    }],
    listeners: {
        selectionchange: function(selModel, selections){
            this.down('#queue-item-delete').setDisabled(selections.length === 0);
        }
    }
});

