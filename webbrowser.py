#!/usr/bin/env python3

# Copyright (c) 2016 Akuli

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Simple web browser.

TODO: Add support for multiple tabs and a statusbar to indicate when
      something is being loaded.
"""

import gi
gi.require_version('Gtk', '3.0')           # NOQA
gi.require_version('WebKit', '3.0')        # NOQA
from gi.repository import Gtk
from gi.repository import WebKit


class Tab(Gtk.ScrolledWindow):
    """A tab.

    Currently this is just a thin wrapper around Gtk.ScrolledWindow and
    WebKit.WebView, but support for multiple tabs can be added later.
    """

    def __init__(self, browser):
        """Initialize the tab."""
        Gtk.ScrolledWindow.__init__(self)
        self.view = WebKit.WebView()
        self.view.load_uri('http://www.google.com/')
        self.view.connect('notify::uri', browser.update)
        self.add(self.view)


class WebBrowser(Gtk.Box):
    """A web browser.

    Add this into a Gtk.Window.
    """

    def __init__(self):
        """Initialize the browser."""
        Gtk.Window.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.create_toolbar()
        self.create_addressbar()
        self.new_tab()
        self.update()

    def create_toolbar(self):
        """Create a toolbar and pack it to self."""
        toolbar = self.toolbar = Gtk.Toolbar()
        data = [
            (Gtk.STOCK_UNDO, "Previous", self.back),
            (Gtk.STOCK_REDO, "Next", self.forward),
            (Gtk.STOCK_REFRESH, "Refresh", self.refresh),
            (Gtk.STOCK_ZOOM_IN, "Zoom in", self.zoom_in),
            (Gtk.STOCK_ZOOM_OUT, "Zoom out", self.zoom_out),
        ]

        self._toolbuttons = {}
        for index, (stock, text, command) in enumerate(data):
            button = self._toolbuttons[stock] = Gtk.ToolButton()
            button.set_icon_name(stock)
            button.set_label(text)
            button.set_tooltip_text(text)
            button.connect('clicked', command)
            toolbar.insert(button, index)

        self.pack_start(toolbar, False, False, 0)

    def create_addressbar(self):
        """Create an address bar and pack it to self."""
        addressbar = self.addressbar = Gtk.Entry()
        addressbar.connect('activate', self.load_uri_from_addressbar)
        self.pack_start(addressbar, False, False, 0)

    def load_uri_from_addressbar(self, widget=None):
        """Get the URI from the address bar and go there."""
        uri = self.addressbar.get_text()

        # Assume the URL points to a HTTP address if nothing else is
        # defined.
        if '://' not in uri:
            uri = 'http://' + uri

        self.get_current_tab().view.load_uri(uri)
        self.update()

    def get_current_tab(self):
        """Return the currently selected tab."""
        return self._current_tab

    def new_tab(self, widget=None):
        """Open a new tab.

        With only one tab, it only makes sense to call this once.
        """
        self._current_tab = Tab(self)
        self.pack_start(self._current_tab, True, True, 0)

    def back(self, widget=None):
        """Go to the previous page."""
        self.get_current_tab().view.go_back()
        self.update()

    def forward(self, widget=None):
        """Go to the next page."""
        self.get_current_tab().view.go_forward()
        self.update()

    def refresh(self, widget=None):
        """Reload the current page."""
        view = self.get_current_tab().view
        view.load_uri(view.get_uri())

    def update(self, *ign):
        """Change toolbar and addressbar.

        Set previous and next buttons' sensitivity and the addressbar's
        text.
        """
        tab = self.get_current_tab()

        backb = self._toolbuttons[Gtk.STOCK_UNDO]
        forwardb = self._toolbuttons[Gtk.STOCK_REDO]
        backb.set_sensitive(tab.view.can_go_back())
        forwardb.set_sensitive(tab.view.can_go_forward())

        self.addressbar.set_text(tab.view.get_uri() or '')

    def zoom_in(self, widget=None):
        """Zoom in."""
        self.get_current_tab().view.zoom_in()

    def zoom_out(self, widget=None):
        """Zoom out."""
        self.get_current_tab().view.zoom_out()


def main():
    """Run the web browser."""
    window = Gtk.Window()
    window.add(WebBrowser())
    window.set_title("Web browser")
    window.set_default_size(900, 600)
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
