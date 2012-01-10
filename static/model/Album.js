Ext.define('jf.model.Album',{
    extend: 'Ext.data.Model',
    fields: [
        'name',
        'artist',
        'cover',
        'type',
        {name: 'year',  type: 'int'}
    ],
    belongsTo: 'Artist',
    hasMany: {model: 'Track', name: 'tracks'}
});

