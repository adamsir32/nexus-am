dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
pmul p0, p0, p1
pfree p1
pmodld 1
dload x10, x11, p1, 0, 0, 0
pmul p1, p0, p1
dstore x10, x11, p1, 1, 0
pmodld 2
dload x10, x11, p1, 0, 0, 0
pmul p1, p0, p1
dstore x10, x11, p1, 1, 0
pmodld 3
dload x10, x11, p1, 0, 0, 0
pmul p0, p0, p1
pfree p1
dstore x10, x11, p0, 1, 0
psync
