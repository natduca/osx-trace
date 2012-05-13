Kernel Tracing for OSX
================================================================================

OSX's kernel comes with built in kernel tracing. Reading these traces can be
incredibly helpful when dealing with mysterious performance problems. However,
the trace utility does not ship with OSX, and even when you have it, its not
very obvious how to use it.

This project downloads and compiles the OSX trace utility for you and wraps it
so that it is obvious what to do. Just type:
   ./osx-trace ---help

