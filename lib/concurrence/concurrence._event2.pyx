#
# event.pyx
#
# libevent Python bindings
#
# Copyright (c) 2004 Dug Song <dugsong@monkey.org>
# Copyright (c) 2003 Martin Murray <murrayma@citi.umich.edu>
#
# $Id: event.pyx,v 1.12 2005/09/12 03:16:15 dugsong Exp $

"""event library

This module provides a mechanism to execute a function when a
specific event on a file handle, file descriptor, or signal occurs,
or after a given time has passed.
"""

__author__ = ( 'Dug Song <dugsong@monkey.org>',
               'Martin Murray <mmurray@monkey.org>' )
__copyright__ = ( 'Copyright (c) 2004 Dug Song',
                  'Copyright (c) 2003 Martin Murray' )
__license__ = 'BSD'
__url__ = 'http://monkey.org/~dugsong/pyevent/'
__version__ = '0.3'

import collections

ctypedef void (*event_handler)(int fd, short event, void *arg)

cdef extern from "string.h":
    char *strerror(int errno)

cdef extern from "errno.h":
    int errno

cdef extern from "event.h":
    struct timeval:
        unsigned int tv_sec
        unsigned int tv_usec
    
    struct event_t "event":
        int   ev_fd
        int   ev_flags
        void *ev_arg

    void event_init()
    char *event_get_version()
    char *event_get_method()
    void event_set(event_t *ev, int fd, short event,
                   event_handler handler, void *arg)
    int  event_add(event_t *ev, timeval *tv)
    int  event_del(event_t *ev)
    int  event_loop(int flags)
    int  event_pending(event_t *ev, short, timeval *tv)

    void evtimer_set(event_t *ev, event_handler handler, void *arg)

    int EVLOOP_ONCE
    int EVLOOP_NONBLOCK
    int EV_TIMEOUT
    int EV_READ
    int EV_WRITE
    int EV_SIGNAL
    int EV_PERSIST

triggered = collections.deque()

cdef void __event_handler(int fd, short event, void *arg):
    triggered.append(((<object>arg), event, fd))

class EventError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg + ": " + strerror(errno))

cdef class event:
    cdef event_t ev
    cdef object data

    def __init__(self, object data):
        self.data = data
        
    def set(self, int fd, short event): 
        event_set(&self.ev, fd, event, __event_handler, <void *>self)

    def add(self, float timeout = -1):
        """Add event to be executed after an optional timeout."""
        cdef timeval tv
        if timeout >= 0.0:
            tv.tv_sec = <long>timeout
            tv.tv_usec = <long>((timeout - <float>tv.tv_sec) * 1000000.0)
            if event_add(&self.ev, &tv) == -1:
                raise EventError("could not add event")
        else:
            if event_add(&self.ev, NULL) == -1:
                raise EventError("could not add event")

    def pending(self, int event):
        """Return 1 if the event is scheduled to run, or else 0."""
        return event_pending(&self.ev, event, NULL)
    
    def delete(self):
        if event_del(&self.ev) == -1:
            raise EventError("could not delete event")
    
    def __repr__(self):
        return '<ev flags=0x%x, data=%s' % (self.ev.ev_flags, self.data)

def version():
    return event_get_version()

def method():
    return event_get_method()

def loop(int flags):
    if event_loop(flags) ==  -1:
        raise EventError("error in event_loop")
    return triggered

# XXX - make sure event queue is always initialized.
event_init()
