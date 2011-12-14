import logging
import os
import tornado.httpserver
import tornado.ioloop
import tornado.web

jukebox_ui = None

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/remote/", RemoteControlHandler),
        ]
        settings = dict(
            cookie_secret="cadabd610f8a59509545fc925a52cd36c40a2b4b",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False, #TODO stop being a lazy guy
            debug=True,
            autoescape=None,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class MessageMixin(object):
    waiters = set()
    cache = []
    cache_size = 200

    def wait_for_messages(self, callback, cursor=None):
        cls = MessageMixin
        if cursor:
            index = 0
            for i in xrange(len(cls.cache)):
                index = len(cls.cache) - i - 1
                if cls.cache[index]["id"] == cursor: break
            recent = cls.cache[index + 1:]
            if recent:
                callback(recent)
                return
        cls.waiters.add(callback)

    def cancel_wait(self, callback):
        cls = MessageMixin
        cls.waiters.remove(callback)

    def new_messages(self, messages):
        cls = MessageMixin
        logging.info("Sending new message to %r listeners", len(cls.waiters))
        for callback in cls.waiters:
            try:
                callback(messages)
            except:
                logging.error("Error in waiter callback", exc_info=True)
        cls.waiters = set()
        cls.cache.extend(messages)
        if len(cls.cache) > self.cache_size:
            cls.cache = cls.cache[-self.cache_size:]

class MainHandler(tornado.web.RequestHandler):
    _playlists = {}

    def playlists(self):
        if self._playlists:
            return self._playlists
        def r(track):
            artists = [t.name() for t in track.artists()]
            return [track.name(), artists, track.album().name()]
        for i, playlist in enumerate(jukebox_ui.get_playlists()):
            tracks = [r(t) for t in playlist]
            self._playlists[playlist.name()] = {'index': i, 'tracks': tracks}
        return self._playlists

    def rendered_playlists(self):
        return self.render_string("_playlists.html", playlists=self.playlists())

    def playing(self):
        return jukebox_ui.do_queue()

    def get(self):
        context = {
            'on_air': self.playing(),
            'playlists': self.rendered_playlists()
        }
        self.render("jukebox.html", context=context)

class RemoteControlHandler(tornado.web.RequestHandler):
    def play(self):
        track = self.get_argument("track", None)
        playlist = self.get_argument("playlist", None)
        jukebox_ui.do_play(track=track, playlist=playlist)
    play.remotecontrol = True

    def stop(self):
        jukebox_ui.do_stop()
    stop.remotecontrol = True

    def next(self):
        jukebox_ui.do_next()
    stop.remotecontrol = True

    def queue(self):
        track = self.get_argument("track", None)
        playlist = self.get_argument("playlist", None)
        jukebox_ui.do_queue(track=track, playlist=playlist)
    queue.remotecontrol = True

    def post(self):
        command = self.get_argument("command", None)
        if command and hasattr(self, command):
            fn = getattr(self, command)
            if getattr(fn, 'remotecontrol', False):
                fn()
