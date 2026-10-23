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
pmodld 3
dload x10, x11, p6, 0, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p6, p8, 0, 0, 0
dload x10, x11, p9, 0, 0, 0
pintt p9, p8, 0, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p6, p8, 1, 0, 0
pintt p9, p8, 1, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p6, p8, 2, 0, 0
pintt p9, p8, 2, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p6, p8, 3, 0, 0
pintt p9, p8, 3, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p6, p8, 4, 0, 0
pintt p9, p8, 4, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p6, p8, 5, 0, 0
pintt p9, p8, 5, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p6, p8, 6, 0, 0
pintt p9, p8, 6, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pmul p6, p6, p8, 1
pmul p9, p9, p8, 1
pfree p8
dload x10, x11, p8, 0, 0, 0
padd p6, p6, p8
padd p9, p9, p8
pfree p8
dload x10, x11, p8, 0, 0, 0
pmul p6, p6, p8
pmul p9, p9, p8
pfree p8
pmodld 0
dload x10, x11, p8, 0, 0, 0
pmul p10, p6, p8
psub p0, p0, p10
pfree p10
pmul p8, p9, p8
psub p2, p2, p8
pfree p8
dload x10, x11, p8, 0, 0, 0
pmul p0, p0, p8
pmul p2, p2, p8
pfree p8
dload x10, x11, p8, 0, 1, 32
pmul p0, p0, p8, 1
pmul p2, p2, p8, 1
pfree p8
dload x10, x11, p8, 0, 1, 32
pntt p0, p8, 0, 0, 0
pntt p2, p8, 0, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pntt p0, p8, 1, 0, 0
pntt p2, p8, 1, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pntt p0, p8, 2, 0, 0
pntt p2, p8, 2, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pntt p0, p8, 3, 0, 0
pntt p2, p8, 3, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pntt p0, p8, 4, 0, 0
pntt p2, p8, 4, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pntt p0, p8, 5, 0, 0
pntt p2, p8, 5, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pntt p0, p8, 6, 0, 0
dstore x10, x11, p0, 1, 0
pntt p2, p8, 6, 0, 0
pfree p8
dstore x10, x11, p2, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p2, p6, p0
psub p1, p1, p2
pfree p2
pmul p0, p9, p0
psub p5, p5, p0
pfree p0
pmodld 2
dload x10, x11, p0, 0, 0, 0
pmul p6, p6, p0
psub p3, p3, p6
pfree p6
pmul p9, p9, p0
pfree p0
psub p7, p7, p9
pfree p9
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p1, p1, p0
pmul p5, p5, p0
pfree p0
pmodld 2
dload x10, x11, p0, 0, 0, 0
pmul p3, p3, p0
pmul p7, p7, p0
pfree p0
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
pmodld 2
dload x10, x11, p0, 0, 1, 32
pmul p3, p3, p0, 1
pmul p7, p7, p0, 1
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p3, p0, 0, 0, 0
pntt p7, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p3, p0, 1, 0, 0
pntt p7, p0, 1, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p3, p0, 2, 0, 0
pntt p7, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p3, p0, 3, 0, 0
pntt p7, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p3, p0, 4, 0, 0
pntt p7, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p3, p0, 5, 0, 0
pntt p7, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p3, p0, 6, 0, 0
dstore x10, x11, p3, 1, 0
pntt p7, p0, 6, 0, 0
pfree p0
dstore x10, x11, p7, 1, 0
psync
