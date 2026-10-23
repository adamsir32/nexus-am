dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
pmul p1, p0, p0
dload x10, x11, p2, 0, 0, 0
pmul p2, p1, p2
dload x10, x11, p3, 0, 0, 0
pmul p3, p1, p3
dload x10, x11, p5, 0, 1, 32
pintt p1, p5, 0, 0, 0
dload x10, x11, p6, 0, 1, 32
pintt p1, p6, 1, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p1, p6, 2, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p1, p6, 3, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p1, p6, 4, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p1, p6, 5, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p1, p6, 6, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pmul p1, p1, p6, 1
pfree p6
pmodld 1
pmul p1, p1, 1
dload x10, x11, p6, 0, 1, 32
pmul p1, p1, p6, 1
pfree p6
pntt p1, p5, 0, 0, 0
dload x10, x11, p6, 0, 1, 32
pntt p1, p6, 1, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p1, p6, 2, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p1, p6, 3, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p1, p6, 4, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p1, p6, 5, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p1, p6, 6, 0, 0
pfree p6
dload x10, x11, p6, 0, 0, 0
pmul p6, p1, p6
pintt p6, p5, 0, 0, 0
dload x10, x11, p7, 0, 0, 0
pmul p1, p1, p7
pfree p7
pintt p1, p5, 0, 0, 0
dload x10, x11, p7, 0, 1, 32
pintt p6, p7, 1, 0, 0
pintt p1, p7, 1, 0, 0
pfree p7
dload x10, x11, p7, 0, 1, 32
pintt p6, p7, 2, 0, 0
pintt p1, p7, 2, 0, 0
pfree p7
dload x10, x11, p7, 0, 1, 32
pintt p6, p7, 3, 0, 0
pintt p1, p7, 3, 0, 0
pfree p7
dload x10, x11, p7, 0, 1, 32
pintt p6, p7, 4, 0, 0
pintt p1, p7, 4, 0, 0
pfree p7
dload x10, x11, p7, 0, 1, 32
pintt p6, p7, 5, 0, 0
pintt p1, p7, 5, 0, 0
pfree p7
dload x10, x11, p7, 0, 1, 32
pintt p6, p7, 6, 0, 0
pintt p1, p7, 6, 0, 0
pfree p7
dload x10, x11, p7, 0, 1, 32
pmul p6, p6, p7, 1
pmul p1, p1, p7, 1
pfree p7
pmodld 0
pmul p7, p6, 1
pmul p8, p1, 1
pmodld 2
dload x10, x11, p9, 0, 0, 0
pmul p6, p6, p9
pmul p1, p1, p9
pfree p9
pmodld 0
dload x10, x11, p9, 0, 0, 0
pmul p6, p6, p9
padd p6, p6, p7
pfree p7
pmul p1, p1, p9
pfree p9
padd p1, p1, p8
pfree p8
dload x10, x11, p7, 0, 1, 32
pmul p6, p6, p7, 1
pmul p1, p1, p7, 1
pfree p7
pntt p6, p5, 0, 0, 0
pntt p1, p5, 0, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p6, p5, 1, 0, 0
pntt p1, p5, 1, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p6, p5, 2, 0, 0
pntt p1, p5, 2, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p6, p5, 3, 0, 0
pntt p1, p5, 3, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p6, p5, 4, 0, 0
pntt p1, p5, 4, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p6, p5, 5, 0, 0
pntt p1, p5, 5, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p6, p5, 6, 0, 0
psub p2, p2, p6
pfree p6
pntt p1, p5, 6, 0, 0
pfree p5
psub p3, p3, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmul p2, p2, p1
pmul p3, p3, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmul p5, p1, p0
dload x10, x11, p6, 0, 0, 0
pmac p5, p0, p6
pfree p0
pmul p1, p1, p6
pfree p6
padd p2, p2, p1
pfree p1
dstore x10, x11, p2, 1, 0
padd p3, p3, p5
pfree p5
dstore x10, x11, p3, 1, 0
psync
