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
pintt p0, p9, 7, 0, 0
dload x10, x11, p10, 0, 1, 32
pintt p0, p10, 8, 0, 0
dload x10, x11, p11, 0, 1, 32
pintt p0, p11, 9, 0, 0
dload x10, x11, p12, 0, 1, 32
pintt p0, p12, 10, 0, 0
dload x10, x11, p13, 0, 1, 32
pintt p0, p13, 11, 0, 0
dload x10, x11, p14, 0, 1, 32
pmul p0, p0, p14, 1
pmodld 0
pmul p15, p0, 1
pmodld 1
pmul p16, p0, 1
pmodld 4
dload x10, x11, p17, 0, 0, 0
pmul p0, p0, p17
pmodld 2
dload x10, x11, p18, 0, 0, 0
pintt p18, p1, 0, 0, 0
pintt p18, p2, 1, 0, 0
pfree p2
pintt p18, p3, 2, 0, 0
pfree p3
pintt p18, p5, 3, 0, 0
pfree p5
pintt p18, p6, 4, 0, 0
pfree p6
pintt p18, p7, 5, 0, 0
pfree p7
pintt p18, p8, 6, 0, 0
pfree p8
pintt p18, p9, 7, 0, 0
pfree p9
pintt p18, p10, 8, 0, 0
pfree p10
pintt p18, p11, 9, 0, 0
pfree p11
pintt p18, p12, 10, 0, 0
pfree p12
pintt p18, p13, 11, 0, 0
pfree p13
pmul p18, p18, p14, 1
pfree p14
pmodld 4
pmul p17, p18, p17
pmodld 0
pmul p2, p18, 1
pmodld 1
pmul p18, p18, 1
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p5, p0, p3
padd p5, p5, p15
pfree p15
pmodld 1
pmul p0, p0, p3
padd p0, p0, p16
pfree p16
pmodld 0
pmul p6, p17, p3
padd p6, p6, p2
pfree p2
pmodld 1
pmul p17, p17, p3
pfree p3
padd p17, p17, p18
pfree p18
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
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 7, 0, 0
pntt p6, p2, 7, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 8, 0, 0
pntt p6, p2, 8, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 9, 0, 0
pntt p6, p2, 9, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 10, 0, 0
pntt p6, p2, 10, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 11, 0, 0
pntt p6, p2, 11, 0, 0
pfree p2
pmodld 1
dload x10, x11, p2, 0, 1, 32
pmul p0, p0, p2, 1
pmul p17, p17, p2, 1
pfree p2
pntt p0, p1, 0, 0, 0
pntt p17, p1, 0, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 1, 0, 0
pntt p17, p1, 1, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 2, 0, 0
pntt p17, p1, 2, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 3, 0, 0
pntt p17, p1, 3, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 4, 0, 0
pntt p17, p1, 4, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 5, 0, 0
pntt p17, p1, 5, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 6, 0, 0
pntt p17, p1, 6, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 7, 0, 0
pntt p17, p1, 7, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 8, 0, 0
pntt p17, p1, 8, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 9, 0, 0
pntt p17, p1, 9, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 10, 0, 0
pntt p17, p1, 10, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 11, 0, 0
pntt p17, p1, 11, 0, 0
pfree p1
pmodld 0
dload x10, x11, p1, 0, 0, 0
psub p1, p1, p5
pfree p5
pmodld 1
dload x10, x11, p2, 0, 0, 0
psub p2, p2, p0
pfree p0
pmodld 0
dload x10, x11, p0, 0, 0, 0
psub p0, p0, p6
pfree p6
pmodld 1
dload x10, x11, p3, 0, 0, 0
psub p3, p3, p17
pfree p17
pmodld 0
dload x10, x11, p5, 0, 0, 0
pmul p1, p1, p5
dstore x10, x11, p1, 1, 0
pmul p0, p0, p5
pfree p5
dstore x10, x11, p0, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p2, p2, p0
dstore x10, x11, p2, 1, 0
pmul p3, p3, p0
pfree p0
dstore x10, x11, p3, 1, 0
psync
