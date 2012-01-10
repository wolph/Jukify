Ext.define('jf.model.Track', {
    extend: 'Ext.data.Model',
    fields: [
        'name',
        {name: 'album', mapping: 'Album.name'},
        {name: 'artist', mapping: 'Artist.name'},
        {name: 'availability',  type: 'int'},
        {name: 'disc',  type: 'int'},
        {name: 'duration',  type: 'int'},
        {name: 'index',  type: 'int'},
        {name: 'popularity',  type: 'int'}
    ],
    belongsTo: 'Album',
    hasMany: {model: 'Artist', name: 'artists'}
});

