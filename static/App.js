Ext.Loader.setConfig({enabled: true});
Ext.state.Manager.setProvider(
    new Ext.state.LocalStorageProvider());

Ext.History.init();

Ext.application({
    name: 'jf',
    autoCreateViewport: true,
    controllers: [
        'Queue',
        'Artist'
    ],
    appFolder: 'static'
});

