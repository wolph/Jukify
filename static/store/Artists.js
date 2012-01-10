Ext.define('jf.store.Artists', {
    extend: 'Ext.data.Store',
    requires: 'jf.model.Artist',    
    model: 'jf.model.Artist',
    autoLoad: true,
    pageSize: 100,
    buffered: true,
    proxy: {
        type: 'rest',
        url: 'static/data/artists.json',
        reader: {
            type: 'json',
            root: 'results'
        }
    }
});

