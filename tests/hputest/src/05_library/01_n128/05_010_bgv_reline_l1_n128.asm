dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
pmul p1, p0, p1
dload x10, x11, p2, 0, 0, 0
pmul p2, p0, p2
dload x10, x11, p3, 0, 1, 32
pintt p0, p3, 0, 0, 0
dload x10, x11, p5, 0, 1, 32
pintt p0, p5, 1, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p0, p5, 2, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p0, p5, 3, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p0, p5, 4, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p0, p5, 5, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p0, p5, 6, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pmul p0, p0, p5, 1
pfree p5
pmodld 1
pmul p0, p0, 1
dload x10, x11, p5, 0, 1, 32
pmul p0, p0, p5, 1
pfree p5
pntt p0, p3, 0, 0, 0
dload x10, x11, p5, 0, 1, 32
pntt p0, p5, 1, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p0, p5, 2, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p0, p5, 3, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p0, p5, 4, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p0, p5, 5, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p0, p5, 6, 0, 0
pfree p5
dload x10, x11, p5, 0, 0, 0
pmul p5, p0, p5
pintt p5, p3, 0, 0, 0
dload x10, x11, p6, 0, 0, 0
pmul p0, p0, p6
pfree p6
pintt p0, p3, 0, 0, 0
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 1, 0, 0
pintt p0, p6, 1, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 2, 0, 0
pintt p0, p6, 2, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 3, 0, 0
pintt p0, p6, 3, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 4, 0, 0
pintt p0, p6, 4, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 5, 0, 0
pintt p0, p6, 5, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 6, 0, 0
pintt p0, p6, 6, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pmul p5, p5, p6, 1
pmul p0, p0, p6, 1
pfree p6
pmodld 0
pmul p6, p5, 1
pmul p7, p0, 1
pmodld 2
dload x10, x11, p8, 0, 0, 0
pmul p5, p5, p8
pmul p0, p0, p8
pfree p8
pmodld 0
dload x10, x11, p8, 0, 0, 0
pmul p5, p5, p8
padd p5, p5, p6
pfree p6
pmul p0, p0, p8
pfree p8
padd p0, p0, p7
pfree p7
dload x10, x11, p6, 0, 1, 32
pmul p5, p5, p6, 1
pmul p0, p0, p6, 1
pfree p6
pntt p5, p3, 0, 0, 0
pntt p0, p3, 0, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p5, p3, 1, 0, 0
pntt p0, p3, 1, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p5, p3, 2, 0, 0
pntt p0, p3, 2, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p5, p3, 3, 0, 0
pntt p0, p3, 3, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p5, p3, 4, 0, 0
pntt p0, p3, 4, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p5, p3, 5, 0, 0
pntt p0, p3, 5, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p5, p3, 6, 0, 0
psub p1, p1, p5
pfree p5
pntt p0, p3, 6, 0, 0
pfree p3
psub p2, p2, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
pmul p1, p1, p0
pmul p2, p2, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
padd p1, p1, p0
pfree p0
dstore x10, x11, p1, 1, 0
dload x10, x11, p0, 0, 0, 0
padd p2, p2, p0
pfree p0
dstore x10, x11, p2, 1, 0
psync
