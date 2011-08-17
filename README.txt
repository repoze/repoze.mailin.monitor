repoze.mailin.monitor README
============================

This package provides a WSGI user interface that can be used to view data
about a mailin store using repoze.mailin.  Currently only data about the
quarantined messages is available and is intended help detect and troubleshoot
problems with mailin.

repoze.mailin.monitor is implemented as a very simple Pyramid application
and as such should be pretty extensible.  This will need to be extended in
order to have much of a security story.

TODO
----

 - Is it possible/desirable to come up with some default security policies such
   that this could be useful and secure out of the box?

 - More docs!
