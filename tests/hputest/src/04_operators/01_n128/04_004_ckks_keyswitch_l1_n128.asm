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
pmul p0, p0, p9, 1
dload x10, x11, p10, 0, 0, 0
pintt p10, p1, 0, 0, 0
pintt p10, p2, 1, 0, 0
pintt p10, p3, 2, 0, 0
pintt p10, p5, 3, 0, 0
pintt p10, p6, 4, 0, 0
pintt p10, p7, 5, 0, 0
pintt p10, p8, 6, 0, 0
pmul p10, p10, p9, 1
dload x10, x11, p11, 0, 0, 0
pintt p11, p1, 0, 0, 0
pintt p11, p2, 1, 0, 0
pintt p11, p3, 2, 0, 0
pintt p11, p5, 3, 0, 0
pintt p11, p6, 4, 0, 0
pintt p11, p7, 5, 0, 0
pintt p11, p8, 6, 0, 0
pmul p11, p11, p9, 1
dload x10, x11, p12, 0, 0, 0
pmul p12, p11, p12
pmodld 1
dload x10, x11, p13, 0, 0, 0
pmul p12, p12, p13
pfree p13
dload x10, x11, p13, 0, 1, 32
pmul p12, p12, p13, 1
pfree p13
dload x10, x11, p13, 0, 1, 32
pntt p12, p13, 0, 0, 0
pfree p13
dload x10, x11, p13, 0, 1, 32
pntt p12, p13, 1, 0, 0
pfree p13
dload x10, x11, p13, 0, 1, 32
pntt p12, p13, 2, 0, 0
pfree p13
dload x10, x11, p13, 0, 1, 32
pntt p12, p13, 3, 0, 0
pfree p13
dload x10, x11, p13, 0, 1, 32
pntt p12, p13, 4, 0, 0
pfree p13
dload x10, x11, p13, 0, 1, 32
pntt p12, p13, 5, 0, 0
pfree p13
dload x10, x11, p13, 0, 1, 32
pntt p12, p13, 6, 0, 0
pfree p13
pmodld 0
dload x10, x11, p13, 0, 1, 32
pmul p11, p11, p13, 1
dload x10, x11, p14, 0, 1, 32
pntt p11, p14, 0, 0, 0
dload x10, x11, p15, 0, 1, 32
pntt p11, p15, 1, 0, 0
dload x10, x11, p16, 0, 1, 32
pntt p11, p16, 2, 0, 0
dload x10, x11, p17, 0, 1, 32
pntt p11, p17, 3, 0, 0
dload x10, x11, p18, 0, 1, 32
pntt p11, p18, 4, 0, 0
pfree p18
dload x10, x11, p19, 0, 1, 32
pntt p11, p19, 5, 0, 0
pfree p19
dload x10, x11, p18, 0, 1, 32
pntt p11, p18, 6, 0, 0
dload x10, x11, p19, 0, 0, 0
pmul p19, p11, p19
pintt p19, p1, 0, 0, 0
pintt p19, p2, 1, 0, 0
pintt p19, p3, 2, 0, 0
pintt p19, p5, 3, 0, 0
pintt p19, p6, 4, 0, 0
pintt p19, p7, 5, 0, 0
pintt p19, p8, 6, 0, 0
pmul p19, p19, p9, 1
dload x10, x11, p20, 0, 0, 0
pmul p11, p11, p20
pfree p20
pintt p11, p1, 0, 0, 0
pfree p1
pintt p11, p2, 1, 0, 0
pfree p2
pintt p11, p3, 2, 0, 0
pfree p3
pintt p11, p5, 3, 0, 0
pfree p5
pintt p11, p6, 4, 0, 0
pfree p6
pintt p11, p7, 5, 0, 0
pfree p7
pintt p11, p8, 6, 0, 0
pfree p8
pmul p11, p11, p9, 1
pfree p9
pmodld 1
dload x10, x11, p1, 0, 0, 0
pmul p1, p12, p1
dload x10, x11, p2, 0, 0, 0
pmul p12, p12, p2
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p1, p2, 0, 0, 0
pintt p12, p2, 0, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p1, p2, 1, 0, 0
pintt p12, p2, 1, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p1, p2, 2, 0, 0
pintt p12, p2, 2, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p1, p2, 3, 0, 0
pintt p12, p2, 3, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p1, p2, 4, 0, 0
pintt p12, p2, 4, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p1, p2, 5, 0, 0
pintt p12, p2, 5, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pintt p1, p2, 6, 0, 0
pintt p12, p2, 6, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pmul p1, p1, p2, 1
pmul p12, p12, p2, 1
pfree p2
pmodld 0
dload x10, x11, p2, 0, 0, 0
padd p19, p19, p2
padd p11, p11, p2
pfree p2
pmodld 1
dload x10, x11, p2, 0, 0, 0
padd p1, p1, p2
padd p12, p12, p2
pfree p2
dload x10, x11, p2, 0, 0, 0
pmul p1, p1, p2
pmul p12, p12, p2
pfree p2
pmodld 0
dload x10, x11, p2, 0, 0, 0
pmul p1, p1, p2
psub p19, p19, p1
pfree p1
pmul p12, p12, p2
pfree p2
psub p11, p11, p12
pfree p12
dload x10, x11, p1, 0, 0, 0
pmul p19, p19, p1
pmul p11, p11, p1
pfree p1
padd p19, p19, p0
pfree p0
padd p10, p10, p11
pfree p11
pmul p19, p19, p13, 1
pmul p10, p10, p13, 1
pfree p13
pntt p19, p14, 0, 0, 0
pntt p10, p14, 0, 0, 0
pfree p14
pntt p19, p15, 1, 0, 0
pntt p10, p15, 1, 0, 0
pfree p15
pntt p19, p16, 2, 0, 0
pntt p10, p16, 2, 0, 0
pfree p16
pntt p19, p17, 3, 0, 0
pntt p10, p17, 3, 0, 0
pfree p17
dload x10, x11, p0, 0, 1, 32
pntt p19, p0, 4, 0, 0
pntt p10, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p19, p0, 5, 0, 0
pntt p10, p0, 5, 0, 0
pfree p0
pntt p19, p18, 6, 0, 0
dstore x10, x11, p19, 1, 0
pntt p10, p18, 6, 0, 0
pfree p18
dstore x10, x11, p10, 1, 0
psync
