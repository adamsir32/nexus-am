dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
padd p0, p0, p1
pfree p1
dstore x10, x11, p0, 0, 0
pmodld 1
dload x10, x11, p1, 0, 0, 0
dload x10, x11, p2, 0, 0, 0
padd p1, p1, p2
pfree p2
dstore x10, x11, p1, 0, 0
pmodld 2
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p3, 0, 0, 0
padd p2, p2, p3
pfree p3
dstore x10, x11, p2, 0, 0
pmodld 3
dload x10, x11, p3, 0, 0, 0
dload x10, x11, p5, 0, 0, 0
padd p3, p3, p5
pfree p5
dstore x10, x11, p3, 0, 0
pfree p3
dload x10, x11, p3, 0, 0, 0
dload x10, x11, p5, 0, 0, 0
pmul p3, p3, p5
pfree p5
dstore x10, x11, p3, 1, 0
dload x10, x11, p3, 0, 0, 0
pmodld 0
dload x10, x11, p5, 0, 0, 0
pmul p3, p3, p5
pfree p5
dstore x10, x11, p3, 0, 0
dload x10, x11, p5, 0, 0, 0
pmodld 1
dload x10, x11, p6, 0, 0, 0
pmul p5, p5, p6
pfree p6
dstore x10, x11, p5, 0, 0
dload x10, x11, p6, 0, 0, 0
pmodld 2
dload x10, x11, p7, 0, 0, 0
pmul p6, p6, p7
pfree p7
dstore x10, x11, p6, 0, 0
pfree p0
dload x10, x11, p0, 0, 0, 0
pfree p3
dload x10, x11, p3, 0, 0, 0
pmodld 0
psub p0, p0, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
pmul p0, p0, p3
pfree p3
dstore x10, x11, p0, 1, 0
pfree p1
dload x10, x11, p0, 0, 0, 0
pfree p5
dload x10, x11, p1, 0, 0, 0
pmodld 1
psub p0, p0, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmul p0, p0, p1
pfree p1
dstore x10, x11, p0, 1, 0
pfree p2
dload x10, x11, p0, 0, 0, 0
pfree p6
dload x10, x11, p1, 0, 0, 0
pmodld 2
psub p0, p0, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmul p0, p0, p1
pfree p1
dstore x10, x11, p0, 1, 0
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
padd p0, p0, p1
pfree p1
dstore x10, x11, p0, 0, 0
pmodld 1
dload x10, x11, p1, 0, 0, 0
dload x10, x11, p2, 0, 0, 0
padd p1, p1, p2
pfree p2
dstore x10, x11, p1, 0, 0
pmodld 2
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p3, 0, 0, 0
padd p2, p2, p3
pfree p3
dstore x10, x11, p2, 0, 0
pmodld 3
dload x10, x11, p3, 0, 0, 0
dload x10, x11, p5, 0, 0, 0
padd p3, p3, p5
pfree p5
dstore x10, x11, p3, 0, 0
pfree p3
dload x10, x11, p3, 0, 0, 0
dload x10, x11, p5, 0, 0, 0
pmul p3, p3, p5
pfree p5
dstore x10, x11, p3, 1, 0
dload x10, x11, p3, 0, 0, 0
pmodld 0
dload x10, x11, p5, 0, 0, 0
pmul p3, p3, p5
pfree p5
dstore x10, x11, p3, 0, 0
dload x10, x11, p5, 0, 0, 0
pmodld 1
dload x10, x11, p6, 0, 0, 0
pmul p5, p5, p6
pfree p6
dstore x10, x11, p5, 0, 0
dload x10, x11, p6, 0, 0, 0
pmodld 2
dload x10, x11, p7, 0, 0, 0
pmul p6, p6, p7
pfree p7
dstore x10, x11, p6, 0, 0
pfree p0
dload x10, x11, p0, 0, 0, 0
pfree p3
dload x10, x11, p3, 0, 0, 0
pmodld 0
psub p0, p0, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
pmul p0, p0, p3
pfree p3
dstore x10, x11, p0, 1, 0
pfree p1
dload x10, x11, p0, 0, 0, 0
pfree p5
dload x10, x11, p1, 0, 0, 0
pmodld 1
psub p0, p0, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmul p0, p0, p1
pfree p1
dstore x10, x11, p0, 1, 0
pfree p2
dload x10, x11, p0, 0, 0, 0
pfree p6
dload x10, x11, p1, 0, 0, 0
pmodld 2
psub p0, p0, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmul p0, p0, p1
pfree p1
dstore x10, x11, p0, 1, 0
psync
