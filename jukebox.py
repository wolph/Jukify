#!/usr/bin/env python
from spotify.manager import (SpotifySessionManager, SpotifyPlaylistManager,
    SpotifyContainerManager)
import app
import os
import spotify
import threading
import time
import tornado
import traceback
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB


AUDIO_HELPERS = (
    ('spotify.alsahelper', 'AlsaController'),
    ('spotify.osshelper', 'OssController'),
    ('spotify.portaudiohelper', 'portAudioController')
)


def import_audio_controller():
    for module, cls in AUDIO_HELPERS:
        try:
            module = __import__(module, fromlist=[cls])
            cls = getattr(module, cls)
        except:
            traceback.print_exc()
            continue
        return cls
    raise ImportError('was not able to import any of the audio helpers')

AudioController = import_audio_controller()


class JukeboxBaseUI(object):

    def __init__(self, jukebox):
        self.jukebox = jukebox
        self.playlist = None
        self.track = None
        self.results = False

    def get_playlists(self):
        return self.jukebox.ctr

    def do_logout(self, line):
        self.jukebox.session.logout()

    def do_quit(self, line):
        print 'Goodbye!'
        self.jukebox.terminate()
        return True

    def do_list(self, line):
        ''' List the playlists, or the contents of a playlist '''
        if not line:
            for i, p in enumerate(self.jukebox.ctr):
                if p.is_loaded():
                    print '%3d %s' % (i, p.name())
                else:
                    print '%3d %s' % (i, 'loading...')
            print '%3d Starred tracks' % (i + 1,)

        else:
            try:
                p = int(line)
            except ValueError:
                print '''that's not a number ! '''
                return
            if p < 0 or p > len(self.jukebox.ctr):
                print '''That's out of range!'''
                return
            print 'Listing playlist  #%d' % p
            if p < len(self.jukebox.ctr):
                playlist = self.jukebox.ctr[p]
            else:
                playlist = self.jukebox.starred
            for i, t in enumerate(playlist):
                if t.is_loaded():
                    print '%3d %s - %s' % (i, t.artists()[0].name(), t.name())
                else:
                    print '%3d %s' % (i, 'loading...')

    def do_play(self, playlist=None, track=None, url=None):
        if playlist and track:
            self.jukebox.load(int(playlist), int(track))
        if url:
            link = spotify.Link.from_string(url)
            if link.type() == spotify.Link.LINK_TRACK:
                track = link.as_track()
                self.jukebox.queue(track=track)

        self.jukebox.play()

    def do_browse(self, line):
        if not line or not line.startswith('spotify:'):
            print 'Invalid id provided'
            return
        l = spotify.Link.from_string(line)
        if not l.type() in [spotify.Link.LINK_ALBUM, spotify.Link.LINK_ARTIST]:
            print 'You can only browse albums and artists'
            return

        def browse_finished(browser):
            print 'Browse finished'
        self.jukebox.browse(l, browse_finished)

    def do_search(self, line):
        if not line:
            if self.results is False:
                print 'No search is in progress'
            elif self.results is None:
                print 'Searching is in progress'
            else:
                print 'Artists:'
                for a in self.results.artists():
                    print '    ', spotify.Link.from_artist(a), a.name()
                print 'Albums:'
                for a in self.results.albums():
                    print '    ', spotify.Link.from_album(a), a.name()
                print 'Tracks:'
                for a in self.results.tracks():
                    print '    ', spotify.Link.from_track(a, 0), a.name()
                print (self.results.total_tracks() -
                    len(self.results.tracks()), 'Tracks not shown')
        else:
            self.results = None

            def search_finished(results, userdata):
                print '\nSearch results received'
                self.results = results
            self.jukebox.search(line, search_finished)

    def do_queue(self, playlist=None, track=None, url=None):
        if playlist and track:
            self.jukebox.queue(int(playlist), int(track))
        elif url:
            link = spotify.Link.from_string(url)
            if link.type() == spotify.Link.LINK_TRACK:
                track = link.as_track()
                self.jukebox.queue(track=track)

        else:
            return self.jukebox._queue


    def get_current_track(self):
        return self.jukebox.get_current_track()

    def get_current_playlist(self):
        return self.jukebox.get_current_playlist()

    def do_stop(self):
        self.jukebox.stop()

    def do_next(self):
        self.jukebox.next_()

    def do_watch(self, line):
        if not line:
            print '''Usage: watch [playlist]
            You will be notified when tracks are added, moved or removed
            from the playlist.'''
        else:
            try:
                p = int(line)
            except ValueError:
                print '''That's not a number ! '''
                return
            if p < 0 or p >= len(self.jukebox.ctr):
                print '''That's out of range!'''
                return
            self.jukebox.watch(self.jukebox.ctr[p])

    def do_unwatch(self, line):
        if not line:
            print 'Usage: unwatch [playlist]'
        else:
            try:
                p = int(line)
            except ValueError:
                print '''That's not a number ! '''
                return
            if p < 0 or p >= len(self.jukebox.ctr):
                print '''That's out of range!'''
                return
            self.jukebox.watch(self.jukebox.ctr[p], True)

    def do_toplist(self, line):
        usage = ('Usage: toplist (albums|artists|tracks) (GB|FR|..|NO|all|'
            'current)')
        if not line:
            print usage
        else:
            args = line.split(' ')
            if len(args) != 2:
                print usage
            else:
                self.jukebox.toplist(*args)

    def do_add_new_playlist(self, line):
        if not line:
            print 'Usage: add_new_playlist <name>'
        else:
            self.jukebox.ctr.add_new_playlist(
                line.decode('utf-8'))

    def do_add_to_playlist(self, line):
        usage = 'Usage: add_to_playlist <playlist_index> <insert_point>' + \
                ' <search_result_indecies>'
        if not line:
            print usage
            return
        args = line.split(' ')
        if len(args) < 3:
            print usage
        else:
            if not self.results:
                print 'No search results'
            else:
                index = int(args.pop(0))
                insert = int(args.pop(0))
                #artists = self.results.artists()
                tracks = self.results.tracks()
                for i in args:
                    for a in tracks[int(i)].artists():
                        print u'{}. {} - {} '.format(
                            i, a.name(),
                            tracks[int(i)].name(),
                        )
                print u'adding them to {} '.format(
                    self.jukebox.ctr[index].name())
                self.jukebox.ctr[index].add_tracks(
                    insert,
                    [tracks[int(i)] for i in args],
                )

    do_ls = do_list
    do_EOF = do_quit


class JukeboxWebUI(JukeboxBaseUI, threading.Thread):

    def __init__(self, jukebox):
        threading.Thread.__init__(self)
        JukeboxBaseUI.__init__(self, jukebox)
        app.jukebox_ui = self
        threading.Thread.__init__(self)

    def run(self):
        from app import Application
        app = Application()
        app.listen(8888, '0.0.0.0')
        tornado.ioloop.IOLoop.instance().start()

## playlist callbacks  ##


class JukeboxPlaylistManager(SpotifyPlaylistManager):

    def tracks_added(self, p, t, i, u):
        print 'Tracks added to playlist %s' % p.name()

    def tracks_moved(self, p, t, i, u):
        print 'Tracks moved in playlist %s' % p.name()

    def tracks_removed(self, p, t, u):
        print 'Tracks removed from playlist %s' % p.name()

## container calllbacks  ##


class JukeboxContainerManager(SpotifyContainerManager):

    def container_loaded(self, c, u):
        print 'Container loaded !'

    def playlist_added(self, c, p, i, u):
        print 'Container: playlist %s added.' % p.name()

    def playlist_moved(self, c, p, oi, ni, u):
        print 'Container: playlist %s moved.' % p.name()

    def playlist_removed(self, c, p, i, u):
        print 'Container: playlist %s removed.' % p.name()


class Database(object):
    def __init__(self):
        self.storage = FileStorage('db.fs')
        self.db = DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root()

class JukeboxSessionManager(SpotifySessionManager):

    queued = False
    playlist = 2
    track = 0
    appkey_file = os.path.join(os.path.dirname(__file__), 'spotify_appkey.key')

    def get_current_track(self):
        return self.track

    def get_current_playlist(self):
        return self.playlist

    def message_to_user(self, session, message):
        print 'Message: ', message

    def log_message(self, session, message):
        print 'Message: ', message

    def notify_main_thread(self, session):
        self.session.process_events()

    def __init__(self, *a, **kw):
        SpotifySessionManager.__init__(self, *a, **kw)
        self.db = Database()
        self.audio = AudioController()
        self.ui = JukeboxWebUI(self)
        self.ctr = None
        self.playing = False
        self._queue = []
        self.playlist_manager = JukeboxPlaylistManager()
        self.container_manager = JukeboxContainerManager()
        self.playlist = None
        self.track = None

    def logged_in(self, session, error):
        if error:
            print error
            return
        session.set_preferred_bitrate(1)  # prefer 320kbps
        self.session = session
        try:
            self.ctr = session.playlist_container()
            self.container_manager.watch(self.ctr)
            self.starred = session.starred()
            self.ui.start()
        except:
            traceback.print_exc()

    def logged_out(self, session):
        self.ui.cmdqueue.append('quit')

    def load_track(self, track):
        if self.playing:
            self.stop()
        self.load(0, track)

    def get_playlist(self, playlist):
        if 0 <= playlist < len(self.ctr):
            playlist = self.ctr[playlist]
        elif playlist == len(self.ctr):
            playlist = self.starred
        return playlist

    def get_track(self, playlist, track):
        return playlist[track]

    def load(self, track):
        if self.playing:
            self.stop()

        self.track = track
        self.session.load(track)
        print 'Loading %s' % (track.name())

    def queue(self, playlist=None, track=None):
        if playlist:
            playlist = self.get_playlist(playlist)
            self._queue.append(self.get_track(playlist, track))
        elif track:
            self._queue.append(track)

        if not self.playing:
            self.next_()

    def play(self, track=None):
        if track:
            self.load(track)
        self.session.play(1)
        self.playing = True

    def stop(self):
        self.session.play(0)
        self.playing = False

    def music_delivery(self, *a, **kw):
        return self.audio.music_delivery(*a, **kw)

    def next_(self):
        self.stop()
        if self._queue:
            self.play(self._queue.pop(0))
        else:
            self.stop()

    def end_of_track(self, sess):
        self.next_()

    def search(self, *args, **kwargs):
        self.session.search(*args, **kwargs)

    def browse(self, link, callback):
        if link.type() == link.LINK_ALBUM:
            browser = self.session.browse_album(link.as_album(), callback)
            while not browser.is_loaded():
                time.sleep(0.1)
            for track in browser:
                print track
        if link.type() == link.LINK_ARTIST:
            browser = self.session.browse_artist(link.as_artist(), callback)
            while not browser.is_loaded():
                time.sleep(0.1)
            for album in browser:
                print album.name()
        callback(browser)

    def watch(self, p, unwatch=False):
        if not unwatch:
            print 'Watching playlist: %s' % p.name()
            self.playlist_manager.watch(p)
        else:
            print 'Unatching playlist: %s' % p.name()
            self.playlist_manager.unwatch(p)

    def toplist(self, tl_type, tl_region):
        print repr(tl_type)
        print repr(tl_region)

        def callback(tb, ud):
            for i in xrange(len(tb)):
                print '%3d: %s' % (i + 1, tb[i].name())

        spotify.ToplistBrowser(tl_type, tl_region, callback)


if __name__ == '__main__':
    import ConfigParser
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read('config.ini')

    import optparse
    option_parser = optparse.OptionParser(version='%prog 0.1')
    option_parser.add_option('-u', '--username', help='spotify username')
    option_parser.add_option('-p', '--password', help='spotify password')
    options, args = option_parser.parse_args()

    username = options.username or config_parser.get('auth', 'username')
    password = options.password or config_parser.get('auth', 'password')

    jukebox = JukeboxSessionManager(username, password, True)
    jukebox.connect()

