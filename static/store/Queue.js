Ext.define('jf.store.Queue', {
    extend: 'Ext.data.Store',
    requires: 'jf.model.Playlist',
    model: 'jf.model.Playlist',
    autoLoad: true,
    autoSync: true,
    proxy: {
        type: 'rest',
        url: 'static/data/queue.json',
        reader: {
            type: 'json',
            root: 'results'
        },
        writer: {
            type: 'json'
        }
    }
});

