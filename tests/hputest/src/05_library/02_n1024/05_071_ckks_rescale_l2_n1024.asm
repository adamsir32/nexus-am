dload x10, x11, p4, 1, 0, 32
pmodld 0
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
pintt p0, p9, 7, 0, 0
dload x10, x11, p10, 0, 1, 32
pintt p0, p10, 8, 0, 0
dload x10, x11, p11, 0, 1, 32
pintt p0, p11, 9, 0, 0
dload x10, x11, p12, 0, 1, 32
pmul p0, p0, p12, 1
dload x10, x11, p13, 0, 0, 0
pintt p13, p1, 0, 0, 0
pfree p1
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
pintt p13, p9, 7, 0, 0
pfree p9
pintt p13, p10, 8, 0, 0
pfree p10
pintt p13, p11, 9, 0, 0
pfree p11
pmul p13, p13, p12, 1
pfree p12
dload x10, x11, p1, 0, 0, 0
padd p0, p0, p1
padd p13, p13, p1
pfree p1
pmodld 1
dload x10, x11, p1, 0, 0, 0
dload x10, x11, p2, 0, 1, 32
pintt p1, p2, 0, 0, 0
dload x10, x11, p3, 0, 1, 32
pintt p1, p3, 1, 0, 0
dload x10, x11, p5, 0, 1, 32
pintt p1, p5, 2, 0, 0
dload x10, x11, p6, 0, 1, 32
pintt p1, p6, 3, 0, 0
dload x10, x11, p7, 0, 1, 32
pintt p1, p7, 4, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p1, p8, 5, 0, 0
dload x10, x11, p9, 0, 1, 32
pintt p1, p9, 6, 0, 0
dload x10, x11, p10, 0, 1, 32
pintt p1, p10, 7, 0, 0
dload x10, x11, p11, 0, 1, 32
pintt p1, p11, 8, 0, 0
dload x10, x11, p12, 0, 1, 32
pintt p1, p12, 9, 0, 0
dload x10, x11, p14, 0, 1, 32
pmul p1, p1, p14, 1
dload x10, x11, p15, 0, 0, 0
pintt p15, p2, 0, 0, 0
pfree p2
pintt p15, p3, 1, 0, 0
pfree p3
pintt p15, p5, 2, 0, 0
pfree p5
pintt p15, p6, 3, 0, 0
pfree p6
pintt p15, p7, 4, 0, 0
pfree p7
pintt p15, p8, 5, 0, 0
pfree p8
pintt p15, p9, 6, 0, 0
pfree p9
pintt p15, p10, 7, 0, 0
pfree p10
pintt p15, p11, 8, 0, 0
pfree p11
pintt p15, p12, 9, 0, 0
pfree p12
pmul p15, p15, p14, 1
pfree p14
dload x10, x11, p2, 0, 0, 0
padd p1, p1, p2
padd p15, p15, p2
pfree p2
dload x10, x11, p2, 0, 0, 0
pmul p1, p1, p2
pmul p15, p15, p2
pfree p2
pmodld 0
dload x10, x11, p2, 0, 0, 0
pmul p1, p1, p2
psub p0, p0, p1
pfree p1
pmul p15, p15, p2
pfree p2
psub p13, p13, p15
pfree p15
dload x10, x11, p1, 0, 0, 0
pmul p0, p0, p1
pmul p13, p13, p1
pfree p1
dload x10, x11, p1, 0, 1, 32
pmul p0, p0, p1, 1
pmul p13, p13, p1, 1
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 0, 0, 0
pntt p13, p1, 0, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 1, 0, 0
pntt p13, p1, 1, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 2, 0, 0
pntt p13, p1, 2, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 3, 0, 0
pntt p13, p1, 3, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 4, 0, 0
pntt p13, p1, 4, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 5, 0, 0
pntt p13, p1, 5, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 6, 0, 0
pntt p13, p1, 6, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 7, 0, 0
pntt p13, p1, 7, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 8, 0, 0
pntt p13, p1, 8, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 9, 0, 0
dstore x10, x11, p0, 1, 0
pntt p13, p1, 9, 0, 0
pfree p1
dstore x10, x11, p13, 1, 0
psync
