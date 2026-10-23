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
pmul p1, p2, p1
pmodld 1
dload x10, x11, p3, 0, 0, 0
pmul p1, p1, p3
pfree p3
dload x10, x11, p3, 0, 1, 32
pmul p1, p1, p3, 1
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p1, p3, 0, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p1, p3, 1, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p1, p3, 2, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p1, p3, 3, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p1, p3, 4, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p1, p3, 5, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p1, p3, 6, 0, 0
pfree p3
pmodld 0
dload x10, x11, p3, 0, 1, 32
pmul p2, p2, p3, 1
dload x10, x11, p5, 0, 1, 32
pntt p2, p5, 0, 0, 0
dload x10, x11, p6, 0, 1, 32
pntt p2, p6, 1, 0, 0
dload x10, x11, p7, 0, 1, 32
pntt p2, p7, 2, 0, 0
dload x10, x11, p8, 0, 1, 32
pntt p2, p8, 3, 0, 0
dload x10, x11, p9, 0, 1, 32
pntt p2, p9, 4, 0, 0
dload x10, x11, p10, 0, 1, 32
pntt p2, p10, 5, 0, 0
dload x10, x11, p11, 0, 1, 32
pntt p2, p11, 6, 0, 0
dload x10, x11, p12, 0, 0, 0
pmul p12, p2, p12
dload x10, x11, p13, 0, 0, 0
pmul p2, p2, p13
pfree p13
pmodld 1
dload x10, x11, p13, 0, 0, 0
pmul p13, p1, p13
dload x10, x11, p14, 0, 0, 0
pmul p1, p1, p14
pfree p14
pmodld 0
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 0, 0, 0
pintt p2, p14, 0, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 1, 0, 0
pintt p2, p14, 1, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 2, 0, 0
pintt p2, p14, 2, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 3, 0, 0
pintt p2, p14, 3, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 4, 0, 0
pintt p2, p14, 4, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 5, 0, 0
pintt p2, p14, 5, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 6, 0, 0
pintt p2, p14, 6, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pmul p12, p12, p14, 1
pmul p2, p2, p14, 1
pfree p14
pmodld 1
dload x10, x11, p14, 0, 1, 32
pintt p13, p14, 0, 0, 0
pintt p1, p14, 0, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p13, p14, 1, 0, 0
pintt p1, p14, 1, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p13, p14, 2, 0, 0
pintt p1, p14, 2, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p13, p14, 3, 0, 0
pintt p1, p14, 3, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p13, p14, 4, 0, 0
pintt p1, p14, 4, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p13, p14, 5, 0, 0
pintt p1, p14, 5, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p13, p14, 6, 0, 0
pintt p1, p14, 6, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pmul p13, p13, p14, 1
pmul p1, p1, p14, 1
pfree p14
pmodld 0
dload x10, x11, p14, 0, 0, 0
padd p12, p12, p14
padd p2, p2, p14
pfree p14
pmodld 1
dload x10, x11, p14, 0, 0, 0
padd p13, p13, p14
padd p1, p1, p14
pfree p14
dload x10, x11, p14, 0, 0, 0
pmul p13, p13, p14
pmul p1, p1, p14
pfree p14
pmodld 0
dload x10, x11, p14, 0, 0, 0
pmul p13, p13, p14
psub p12, p12, p13
pfree p13
pmul p1, p1, p14
pfree p14
psub p2, p2, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmul p12, p12, p1
pmul p2, p2, p1
pfree p1
padd p12, p12, p0
pfree p0
pmul p12, p12, p3, 1
pmul p2, p2, p3, 1
pfree p3
pntt p12, p5, 0, 0, 0
pntt p2, p5, 0, 0, 0
pfree p5
pntt p12, p6, 1, 0, 0
pntt p2, p6, 1, 0, 0
pfree p6
pntt p12, p7, 2, 0, 0
pntt p2, p7, 2, 0, 0
pfree p7
pntt p12, p8, 3, 0, 0
pntt p2, p8, 3, 0, 0
pfree p8
pntt p12, p9, 4, 0, 0
pntt p2, p9, 4, 0, 0
pfree p9
pntt p12, p10, 5, 0, 0
pntt p2, p10, 5, 0, 0
pfree p10
pntt p12, p11, 6, 0, 0
dstore x10, x11, p12, 1, 0
pntt p2, p11, 6, 0, 0
pfree p11
dstore x10, x11, p2, 1, 0
psync
