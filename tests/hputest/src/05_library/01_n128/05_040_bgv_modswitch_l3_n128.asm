dload x10, x11, p4, 1, 0, 32
pmodld 2
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 0, 0, 0
dload x10, x11, p2, 0, 1, 32
pintt p0, p2, 1, 0, 0
dload x10, x11, p3, 0, 1, 32
pintt p0, p3, 2, 0, 0
dload x10, x11, p5, 0, 1, 32
pintt p0, p5, 3, 0, 0
dload x10, x11, p6, 0, 1, 32
pintt p0, p6, 4, 0, 0
dload x10, x11, p7, 0, 1, 32
pintt p0, p7, 5, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p0, p8, 6, 0, 0
dload x10, x11, p9, 0, 1, 32
pmul p0, p0, p9, 1
pmodld 0
pmul p10, p0, 1
pmodld 1
pmul p11, p0, 1
pmodld 4
dload x10, x11, p12, 0, 0, 0
pmul p0, p0, p12
pmodld 2
dload x10, x11, p13, 0, 0, 0
pintt p13, p1, 0, 0, 0
pintt p13, p2, 1, 0, 0
pfree p2
pintt p13, p3, 2, 0, 0
pfree p3
pintt p13, p5, 3, 0, 0
pfree p5
pintt p13, p6, 4, 0, 0
pfree p6
pintt p13, p7, 5, 0, 0
pfree p7
pintt p13, p8, 6, 0, 0
pfree p8
pmul p13, p13, p9, 1
pfree p9
pmodld 4
pmul p12, p13, p12
pmodld 0
pmul p2, p13, 1
pmodld 1
pmul p13, p13, 1
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p5, p0, p3
padd p5, p5, p10
pfree p10
pmodld 1
pmul p0, p0, p3
padd p0, p0, p11
pfree p11
pmodld 0
pmul p6, p12, p3
padd p6, p6, p2
pfree p2
pmodld 1
pmul p12, p12, p3
pfree p3
padd p12, p12, p13
pfree p13
pmodld 0
dload x10, x11, p2, 0, 1, 32
pmul p5, p5, p2, 1
pmul p6, p6, p2, 1
pfree p2
pntt p5, p1, 0, 0, 0
pntt p6, p1, 0, 0, 0
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 1, 0, 0
pntt p6, p2, 1, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 2, 0, 0
pntt p6, p2, 2, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 3, 0, 0
pntt p6, p2, 3, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 4, 0, 0
pntt p6, p2, 4, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 5, 0, 0
pntt p6, p2, 5, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 6, 0, 0
pntt p6, p2, 6, 0, 0
pfree p2
dload x10, x11, p2, 0, 0, 0
psub p2, p2, p5
pfree p5
dload x10, x11, p3, 0, 0, 0
psub p3, p3, p6
pfree p6
dload x10, x11, p5, 0, 0, 0
pmul p2, p2, p5
dstore x10, x11, p2, 1, 0
pmul p3, p3, p5
pfree p5
dstore x10, x11, p3, 1, 0
pmodld 1
dload x10, x11, p2, 0, 1, 32
pmul p0, p0, p2, 1
pmul p12, p12, p2, 1
pfree p2
pntt p0, p1, 0, 0, 0
pntt p12, p1, 0, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 1, 0, 0
pntt p12, p1, 1, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 2, 0, 0
pntt p12, p1, 2, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 3, 0, 0
pntt p12, p1, 3, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 4, 0, 0
pntt p12, p1, 4, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 5, 0, 0
pntt p12, p1, 5, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 6, 0, 0
pntt p12, p1, 6, 0, 0
pfree p1
dload x10, x11, p1, 0, 0, 0
psub p1, p1, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
psub p0, p0, p12
pfree p12
dload x10, x11, p2, 0, 0, 0
pmul p1, p1, p2
dstore x10, x11, p1, 1, 0
pmul p0, p0, p2
pfree p2
dstore x10, x11, p0, 1, 0
psync
