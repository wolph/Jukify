Ext.define('jf.model.Artist',{
    extend: 'Ext.data.Model',
    fields: [
        'name'
    ],
    hasMany: {
        model: 'Album',
        name: 'albums'
    }
});

