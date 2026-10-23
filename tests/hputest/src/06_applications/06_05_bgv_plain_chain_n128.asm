dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
padd p0, p0, p1
pmodld 1
dload x10, x11, p2, 0, 0, 0
padd p2, p2, p1
pmodld 2
dload x10, x11, p3, 0, 0, 0
padd p3, p3, p1
pfree p1
pmodld 0
dload x10, x11, p1, 0, 0, 0
pmul p0, p0, p1
dload x10, x11, p5, 0, 0, 0
pmul p5, p5, p1
pfree p1
pmodld 1
dload x10, x11, p1, 0, 0, 0
pmul p2, p2, p1
dload x10, x11, p6, 0, 0, 0
pmul p6, p6, p1
pfree p1
pmodld 2
dload x10, x11, p1, 0, 0, 0
pmul p3, p3, p1
dload x10, x11, p7, 0, 0, 0
pmul p7, p7, p1
pfree p1
pmodld 0
dload x10, x11, p1, 0, 0, 0
psub p0, p0, p1
dstore x10, x11, p0, 1, 0
dstore x10, x11, p5, 1, 0
pmodld 1
psub p2, p2, p1
dstore x10, x11, p2, 1, 0
dstore x10, x11, p6, 1, 0
pmodld 2
psub p3, p3, p1
pfree p1
dstore x10, x11, p3, 1, 0
dstore x10, x11, p7, 1, 0
psync
