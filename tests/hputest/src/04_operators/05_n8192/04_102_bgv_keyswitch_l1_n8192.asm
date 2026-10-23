dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 0, 0, 0
dload x10, x11, p2, 0, 1, 32
pintt p0, p2, 1, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p0, p2, 2, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p0, p2, 3, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p0, p2, 4, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p0, p2, 5, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p0, p2, 6, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p0, p2, 7, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p0, p2, 8, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p0, p2, 9, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p0, p2, 10, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p0, p2, 11, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p0, p2, 12, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pmul p0, p0, p2, 1
pfree p2
pmodld 1
pmul p0, p0, 1
dload x10, x11, p2, 0, 1, 32
pmul p0, p0, p2, 1
pfree p2
pntt p0, p1, 0, 0, 0
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 1, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 2, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 3, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 4, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 5, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 6, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 7, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 8, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 9, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 10, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 11, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 12, 0, 0
pfree p2
pmodld 0
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p3, 0, 0, 0
pmul p3, p2, p3
dload x10, x11, p5, 0, 0, 0
pmul p2, p2, p5
pfree p5
pmodld 1
dload x10, x11, p5, 0, 0, 0
pmul p5, p0, p5
pintt p5, p1, 0, 0, 0
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 1, 0, 0
dload x10, x11, p7, 0, 1, 32
pintt p5, p7, 2, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p5, p8, 3, 0, 0
dload x10, x11, p9, 0, 1, 32
pintt p5, p9, 4, 0, 0
dload x10, x11, p10, 0, 1, 32
pintt p5, p10, 5, 0, 0
dload x10, x11, p11, 0, 1, 32
pintt p5, p11, 6, 0, 0
dload x10, x11, p12, 0, 1, 32
pintt p5, p12, 7, 0, 0
dload x10, x11, p13, 0, 1, 32
pintt p5, p13, 8, 0, 0
dload x10, x11, p14, 0, 1, 32
pintt p5, p14, 9, 0, 0
dload x10, x11, p15, 0, 1, 32
pintt p5, p15, 10, 0, 0
dload x10, x11, p16, 0, 1, 32
pintt p5, p16, 11, 0, 0
dload x10, x11, p17, 0, 1, 32
pintt p5, p17, 12, 0, 0
dload x10, x11, p18, 0, 1, 32
pmul p5, p5, p18, 1
pmodld 0
pmul p19, p5, 1
pmodld 1
dload x10, x11, p20, 0, 0, 0
pmul p0, p0, p20
pfree p20
pintt p0, p1, 0, 0, 0
pintt p0, p6, 1, 0, 0
pfree p6
pintt p0, p7, 2, 0, 0
pfree p7
pintt p0, p8, 3, 0, 0
pfree p8
pintt p0, p9, 4, 0, 0
pfree p9
pintt p0, p10, 5, 0, 0
pfree p10
pintt p0, p11, 6, 0, 0
pfree p11
pintt p0, p12, 7, 0, 0
pfree p12
pintt p0, p13, 8, 0, 0
pfree p13
pintt p0, p14, 9, 0, 0
pfree p14
pintt p0, p15, 10, 0, 0
pfree p15
pintt p0, p16, 11, 0, 0
pfree p16
pintt p0, p17, 12, 0, 0
pfree p17
pmul p0, p0, p18, 1
pfree p18
pmodld 0
pmul p6, p0, 1
pmodld 2
dload x10, x11, p7, 0, 0, 0
pmul p5, p5, p7
pmul p0, p0, p7
pfree p7
pmodld 0
dload x10, x11, p7, 0, 0, 0
pmul p5, p5, p7
padd p5, p5, p19
pfree p19
pmul p0, p0, p7
pfree p7
padd p0, p0, p6
pfree p6
dload x10, x11, p6, 0, 1, 32
pmul p5, p5, p6, 1
pmul p0, p0, p6, 1
pfree p6
pntt p5, p1, 0, 0, 0
pntt p0, p1, 0, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p5, p1, 1, 0, 0
pntt p0, p1, 1, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p5, p1, 2, 0, 0
pntt p0, p1, 2, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p5, p1, 3, 0, 0
pntt p0, p1, 3, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p5, p1, 4, 0, 0
pntt p0, p1, 4, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p5, p1, 5, 0, 0
pntt p0, p1, 5, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p5, p1, 6, 0, 0
pntt p0, p1, 6, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p5, p1, 7, 0, 0
pntt p0, p1, 7, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p5, p1, 8, 0, 0
pntt p0, p1, 8, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p5, p1, 9, 0, 0
pntt p0, p1, 9, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p5, p1, 10, 0, 0
pntt p0, p1, 10, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p5, p1, 11, 0, 0
pntt p0, p1, 11, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p5, p1, 12, 0, 0
psub p3, p3, p5
pfree p5
pntt p0, p1, 12, 0, 0
pfree p1
psub p2, p2, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
pmul p3, p3, p0
pmul p2, p2, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
padd p3, p3, p0
dstore x10, x11, p3, 1, 0
padd p2, p2, p0
pfree p0
dstore x10, x11, p2, 1, 0
psync
