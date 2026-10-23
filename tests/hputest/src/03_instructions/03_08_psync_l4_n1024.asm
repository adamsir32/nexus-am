dload x10, x11, p63, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dstore x10, x11, p0, 1, 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
pmul p2, p0, p1
dstore x10, x11, p2, 1, 0
pfree p0
pfree p1
pmodld 1
dload x10, x11, p0, 0, 0, 0
dstore x10, x11, p0, 1, 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
pmul p2, p0, p1
dstore x10, x11, p2, 1, 0
pfree p0
pfree p1
pmodld 2
dload x10, x11, p0, 0, 0, 0
dstore x10, x11, p0, 1, 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
pmul p2, p0, p1
dstore x10, x11, p2, 1, 0
pfree p0
pfree p1
pmodld 3
dload x10, x11, p0, 0, 0, 0
dstore x10, x11, p0, 1, 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
pmul p2, p0, p1
dstore x10, x11, p2, 1, 0
pfree p0
pfree p1
pfree p63
psync
