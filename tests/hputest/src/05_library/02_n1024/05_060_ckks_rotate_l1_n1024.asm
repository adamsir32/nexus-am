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
dload x10, x11, p1, 0, 1, 32
pmul p2, p13, p1, 1
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 0, 0, 0
dload x10, x11, p5, 0, 1, 32
pntt p2, p5, 1, 0, 0
dload x10, x11, p6, 0, 1, 32
pntt p2, p6, 2, 0, 0
dload x10, x11, p7, 0, 1, 32
pntt p2, p7, 3, 0, 0
dload x10, x11, p8, 0, 1, 32
pntt p2, p8, 4, 0, 0
dload x10, x11, p9, 0, 1, 32
pntt p2, p9, 5, 0, 0
dload x10, x11, p10, 0, 1, 32
pntt p2, p10, 6, 0, 0
dload x10, x11, p11, 0, 1, 32
pntt p2, p11, 7, 0, 0
dload x10, x11, p12, 0, 1, 32
pntt p2, p12, 8, 0, 0
dload x10, x11, p14, 0, 1, 32
pntt p2, p14, 9, 0, 0
dload x10, x11, p15, 0, 0, 0
pmul p13, p13, p15
pfree p15
pmodld 1
dload x10, x11, p15, 0, 0, 0
pmul p13, p13, p15
pfree p15
dload x10, x11, p15, 0, 1, 32
pmul p13, p13, p15, 1
pfree p15
dload x10, x11, p15, 0, 1, 32
pntt p13, p15, 0, 0, 0
pfree p15
dload x10, x11, p15, 0, 1, 32
pntt p13, p15, 1, 0, 0
pfree p15
dload x10, x11, p15, 0, 1, 32
pntt p13, p15, 2, 0, 0
pfree p15
dload x10, x11, p15, 0, 1, 32
pntt p13, p15, 3, 0, 0
pfree p15
dload x10, x11, p15, 0, 1, 32
pntt p13, p15, 4, 0, 0
pfree p15
dload x10, x11, p15, 0, 1, 32
pntt p13, p15, 5, 0, 0
pfree p15
dload x10, x11, p15, 0, 1, 32
pntt p13, p15, 6, 0, 0
pfree p15
dload x10, x11, p15, 0, 1, 32
pntt p13, p15, 7, 0, 0
pfree p15
dload x10, x11, p15, 0, 1, 32
pntt p13, p15, 8, 0, 0
pfree p15
dload x10, x11, p15, 0, 1, 32
pntt p13, p15, 9, 0, 0
pfree p15
pmodld 0
dload x10, x11, p15, 0, 0, 0
pmul p15, p2, p15
dload x10, x11, p16, 0, 1, 32
pintt p15, p16, 0, 0, 0
dload x10, x11, p17, 0, 1, 32
pintt p15, p17, 1, 0, 0
dload x10, x11, p18, 0, 1, 32
pintt p15, p18, 2, 0, 0
pfree p14
dload x10, x11, p19, 0, 1, 32
pintt p15, p19, 3, 0, 0
pfree p12
dload x10, x11, p14, 0, 1, 32
pintt p15, p14, 4, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pintt p15, p12, 5, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pintt p15, p11, 6, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pintt p15, p10, 7, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pintt p15, p9, 8, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pintt p15, p8, 9, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pmul p15, p15, p7, 1
dload x10, x11, p6, 0, 0, 0
pmul p2, p2, p6
pfree p6
pintt p2, p16, 0, 0, 0
pfree p16
pintt p2, p17, 1, 0, 0
pfree p17
pintt p2, p18, 2, 0, 0
pfree p18
pintt p2, p19, 3, 0, 0
pfree p19
pintt p2, p14, 4, 0, 0
pfree p14
pintt p2, p12, 5, 0, 0
pfree p12
pintt p2, p11, 6, 0, 0
pfree p11
pintt p2, p10, 7, 0, 0
pfree p10
pintt p2, p9, 8, 0, 0
pfree p9
pintt p2, p8, 9, 0, 0
pfree p8
pmul p2, p2, p7, 1
pfree p7
pmodld 1
dload x10, x11, p6, 0, 0, 0
pmul p6, p13, p6
dload x10, x11, p7, 0, 1, 32
pintt p6, p7, 0, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p6, p8, 1, 0, 0
dload x10, x11, p9, 0, 1, 32
pintt p6, p9, 2, 0, 0
dload x10, x11, p10, 0, 1, 32
pintt p6, p10, 3, 0, 0
dload x10, x11, p11, 0, 1, 32
pintt p6, p11, 4, 0, 0
dload x10, x11, p12, 0, 1, 32
pintt p6, p12, 5, 0, 0
dload x10, x11, p14, 0, 1, 32
pintt p6, p14, 6, 0, 0
dload x10, x11, p16, 0, 1, 32
pintt p6, p16, 7, 0, 0
dload x10, x11, p17, 0, 1, 32
pintt p6, p17, 8, 0, 0
dload x10, x11, p18, 0, 1, 32
pintt p6, p18, 9, 0, 0
dload x10, x11, p19, 0, 1, 32
pmul p6, p6, p19, 1
dload x10, x11, p20, 0, 0, 0
pmul p13, p13, p20
pfree p20
pintt p13, p7, 0, 0, 0
pfree p7
pintt p13, p8, 1, 0, 0
pfree p8
pintt p13, p9, 2, 0, 0
pfree p9
pintt p13, p10, 3, 0, 0
pfree p10
pintt p13, p11, 4, 0, 0
pfree p11
pintt p13, p12, 5, 0, 0
pfree p12
pintt p13, p14, 6, 0, 0
pfree p14
pintt p13, p16, 7, 0, 0
pfree p16
pintt p13, p17, 8, 0, 0
pfree p17
pintt p13, p18, 9, 0, 0
pfree p18
pmul p13, p13, p19, 1
pfree p19
pmodld 0
dload x10, x11, p7, 0, 0, 0
padd p15, p15, p7
padd p2, p2, p7
pfree p7
pmodld 1
dload x10, x11, p7, 0, 0, 0
padd p6, p6, p7
padd p13, p13, p7
pfree p7
dload x10, x11, p7, 0, 0, 0
pmul p6, p6, p7
pmul p13, p13, p7
pfree p7
pmodld 0
dload x10, x11, p7, 0, 0, 0
pmul p6, p6, p7
psub p15, p15, p6
pfree p6
pmul p13, p13, p7
pfree p7
psub p2, p2, p13
pfree p13
dload x10, x11, p6, 0, 0, 0
pmul p15, p15, p6
pmul p2, p2, p6
pfree p6
padd p15, p15, p0
pfree p0
pmul p15, p15, p1, 1
pmul p2, p2, p1, 1
pfree p1
pntt p15, p3, 0, 0, 0
pntt p2, p3, 0, 0, 0
pfree p3
pntt p15, p5, 1, 0, 0
pntt p2, p5, 1, 0, 0
pfree p5
dload x10, x11, p0, 0, 1, 32
pntt p15, p0, 2, 0, 0
pntt p2, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p15, p0, 3, 0, 0
pntt p2, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p15, p0, 4, 0, 0
pntt p2, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p15, p0, 5, 0, 0
pntt p2, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p15, p0, 6, 0, 0
pntt p2, p0, 6, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p15, p0, 7, 0, 0
pntt p2, p0, 7, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p15, p0, 8, 0, 0
pntt p2, p0, 8, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p15, p0, 9, 0, 0
dstore x10, x11, p15, 1, 0
pntt p2, p0, 9, 0, 0
pfree p0
dstore x10, x11, p2, 1, 0
psync
