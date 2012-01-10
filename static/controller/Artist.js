Ext.define('jf.controller.Artist', {
    extend: 'Ext.app.Controller',
    stores: ['Artists'],

    refs: [{
        ref: 'artists',
        selector: 'artists'
    }, {
        ref: 'recentlyPlayedScroller',
        selector: 'recentlyplayedscroller'
    }],

    init: function() {
        this.control({
            'textfield[name=artistFilter]': {
                specialkey: {
                    fn: this.onSearch,
                    buffer: 100
                },
                change: {
                    fn: this.onSearch,
                    buffer: 100
                }
            },
            'button[name=artistFilterButton]': {
                click: {
                    fn: this.onSearch,
                    type: Ext.Button
                }
            },
            'recentlyplayedscroller': {
                selectionchange: this.onArtistSelect
            }
        });

        // Listen for an application wide event
        this.application.on({
            playliststart: this.onPlaylistStart,
            scope: this
        });
    },

    onSearch: function(field, event, options){
        if((field.xtype == 'textfield' && event.getKey && event.getKey() == event.ENTER) || field.xtype == 'button'){
            console.log('real search');
        }else{
            store = this.getArtists().getStore();
            store.clearFilter();
            store.filter('name', Ext.query('input[name=artistFilter]')[0].value);
        }
    },
    
    onPlaylistStart: function(playlist) {
        var store = this.getRecentArtistsStore();

        store.load({
            callback: this.onRecentArtistsLoad,
            params: {
                playlist: playlist.get('id')
            },            
            scope: this
        });
    },
    
    onRecentArtistsLoad: function(artists, request) {
        var store = this.getRecentArtistsStore(),
            selModel = this.getRecentlyPlayedScroller().getSelectionModel();

        // The data should already be filtered on the serverside but since we
        // are loading static data we need to do this after we loaded all the data
        store.clearFilter();
        store.filter('playlist', request.params.playlist);
        store.sort('played_date', 'ASC');        

        selModel.select(store.last());
    },
    
    onArtistSelect: function(selModel, selection) {
        this.getArtistInfo().update(selection[0]);
    }
});

