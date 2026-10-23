dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 0, 0, 0
dload x10, x11, p2, 0, 0, 0
pintt p2, p1, 0, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 1, 0, 0
pintt p2, p1, 1, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 2, 0, 0
pintt p2, p1, 2, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 3, 0, 0
pintt p2, p1, 3, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 4, 0, 0
pintt p2, p1, 4, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 5, 0, 0
pintt p2, p1, 5, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 6, 0, 0
pintt p2, p1, 6, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pmul p0, p0, p1, 1
pmul p2, p2, p1, 1
pfree p1
dload x10, x11, p1, 0, 0, 0
padd p0, p0, p1
padd p2, p2, p1
pfree p1
pmodld 1
dload x10, x11, p1, 0, 0, 0
dload x10, x11, p3, 0, 1, 32
pintt p1, p3, 0, 0, 0
dload x10, x11, p5, 0, 0, 0
pintt p5, p3, 0, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p1, p3, 1, 0, 0
pintt p5, p3, 1, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p1, p3, 2, 0, 0
pintt p5, p3, 2, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p1, p3, 3, 0, 0
pintt p5, p3, 3, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p1, p3, 4, 0, 0
pintt p5, p3, 4, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p1, p3, 5, 0, 0
pintt p5, p3, 5, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p1, p3, 6, 0, 0
pintt p5, p3, 6, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pmul p1, p1, p3, 1
pmul p5, p5, p3, 1
pfree p3
dload x10, x11, p3, 0, 0, 0
padd p1, p1, p3
padd p5, p5, p3
pfree p3
pmodld 2
dload x10, x11, p3, 0, 0, 0
dload x10, x11, p6, 0, 1, 32
pintt p3, p6, 0, 0, 0
dload x10, x11, p7, 0, 0, 0
pintt p7, p6, 0, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p3, p6, 1, 0, 0
pintt p7, p6, 1, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p3, p6, 2, 0, 0
pintt p7, p6, 2, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p3, p6, 3, 0, 0
pintt p7, p6, 3, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p3, p6, 4, 0, 0
pintt p7, p6, 4, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p3, p6, 5, 0, 0
pintt p7, p6, 5, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p3, p6, 6, 0, 0
pintt p7, p6, 6, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pmul p3, p3, p6, 1
pmul p7, p7, p6, 1
pfree p6
dload x10, x11, p6, 0, 0, 0
padd p3, p3, p6
padd p7, p7, p6
pfree p6
dload x10, x11, p6, 0, 0, 0
pmul p3, p3, p6
pmul p7, p7, p6
pfree p6
pmodld 0
dload x10, x11, p6, 0, 0, 0
pmul p8, p3, p6
psub p0, p0, p8
pfree p8
pmul p6, p7, p6
psub p2, p2, p6
pfree p6
pmodld 1
dload x10, x11, p6, 0, 0, 0
pmul p3, p3, p6
psub p1, p1, p3
pfree p3
pmul p7, p7, p6
pfree p6
psub p5, p5, p7
pfree p7
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p0, p0, p3
pmul p2, p2, p3
pfree p3
pmodld 1
dload x10, x11, p3, 0, 0, 0
pmul p1, p1, p3
pmul p5, p5, p3
pfree p3
pmodld 0
dload x10, x11, p3, 0, 1, 32
pmul p0, p0, p3, 1
pmul p2, p2, p3, 1
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 0, 0, 0
pntt p2, p3, 0, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 1, 0, 0
pntt p2, p3, 1, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 2, 0, 0
pntt p2, p3, 2, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 3, 0, 0
pntt p2, p3, 3, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 4, 0, 0
pntt p2, p3, 4, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 5, 0, 0
pntt p2, p3, 5, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 6, 0, 0
dstore x10, x11, p0, 1, 0
pntt p2, p3, 6, 0, 0
pfree p3
dstore x10, x11, p2, 1, 0
pmodld 1
dload x10, x11, p0, 0, 1, 32
pmul p1, p1, p0, 1
pmul p5, p5, p0, 1
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 0, 0, 0
pntt p5, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 1, 0, 0
pntt p5, p0, 1, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 2, 0, 0
pntt p5, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 3, 0, 0
pntt p5, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 4, 0, 0
pntt p5, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 5, 0, 0
pntt p5, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 6, 0, 0
dstore x10, x11, p1, 1, 0
pntt p5, p0, 6, 0, 0
pfree p0
dstore x10, x11, p5, 1, 0
psync
