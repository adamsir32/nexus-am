dload x10, x11, p4, 1, 0, 32
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 1, 32
dload x10, x11, p2, 0, 1, 32
dload x10, x11, p3, 0, 1, 32
dload x10, x11, p5, 0, 1, 32
dload x10, x11, p6, 0, 1, 32
dload x10, x11, p7, 0, 1, 32
dload x10, x11, p8, 0, 1, 32
dload x10, x11, p9, 0, 1, 32
dload x10, x11, p10, 0, 1, 32
dload x10, x11, p11, 0, 1, 32
dload x10, x11, p12, 0, 1, 32
dload x10, x11, p13, 0, 0, 0
dload x10, x11, p14, 0, 0, 0
dload x10, x11, p15, 0, 0, 0
dload x10, x11, p16, 0, 1, 32
dload x10, x11, p17, 0, 0, 0
dload x10, x11, p18, 0, 0, 0
dload x10, x11, p19, 0, 0, 0
dload x10, x11, p20, 0, 0, 0
dload x10, x11, p21, 0, 0, 0
dload x10, x11, p22, 0, 0, 0
dload x10, x11, p23, 0, 0, 0
dload x10, x11, p24, 0, 0, 0
pmodld 3
psync
pintt p0, p1, 0, 0, 0
pintt p0, p2, 1, 0, 0
pintt p0, p3, 2, 0, 0
pintt p0, p5, 3, 0, 0
pintt p0, p6, 4, 0, 0
pintt p0, p7, 5, 0, 0
pintt p0, p8, 6, 0, 0
pintt p0, p9, 7, 0, 0
pintt p0, p10, 8, 0, 0
pintt p0, p11, 9, 0, 0
pmul p0, p0, p12, 1
pmodld 0
pmul p25, p0, 1
pmodld 1
pmul p26, p0, 1
pmodld 2
pmul p27, p0, 1
pmodld 5
pmul p0, p0, p13
pmodld 3
pintt p14, p1, 0, 0, 0
pintt p14, p2, 1, 0, 0
pfree p2
pintt p14, p3, 2, 0, 0
pfree p3
pintt p14, p5, 3, 0, 0
pfree p5
pintt p14, p6, 4, 0, 0
pfree p6
pintt p14, p7, 5, 0, 0
pfree p7
pintt p14, p8, 6, 0, 0
pfree p8
pintt p14, p9, 7, 0, 0
pfree p9
pintt p14, p10, 8, 0, 0
pfree p10
pintt p14, p11, 9, 0, 0
pfree p11
pmul p14, p14, p12, 1
pfree p12
pmodld 5
pmul p13, p14, p13
pmodld 0
pmul p2, p14, 1
pmodld 1
pmul p3, p14, 1
pmodld 2
pmul p14, p14, 1
pmodld 0
pmul p5, p0, p15
padd p5, p5, p25
pfree p25
pmul p15, p13, p15
padd p15, p15, p2
pfree p2
pmul p5, p5, p16, 1
pmul p15, p15, p16, 1
pfree p16
pntt p5, p1, 0, 0, 0
pntt p15, p1, 0, 0, 0
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 1, 0, 0
pntt p15, p2, 1, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 2, 0, 0
pntt p15, p2, 2, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 3, 0, 0
pntt p15, p2, 3, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 4, 0, 0
pntt p15, p2, 4, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 5, 0, 0
pntt p15, p2, 5, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 6, 0, 0
pntt p15, p2, 6, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 7, 0, 0
pntt p15, p2, 7, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 8, 0, 0
pntt p15, p2, 8, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p5, p2, 9, 0, 0
pntt p15, p2, 9, 0, 0
pfree p2
psub p17, p17, p5
pfree p5
psub p18, p18, p15
pfree p15
pmul p17, p17, p19
dstore x10, x11, p17, 1, 0
pmul p18, p18, p19
pfree p19
dstore x10, x11, p18, 1, 0
pmodld 1
pmul p2, p0, p20
padd p2, p2, p26
pfree p26
pmul p20, p13, p20
padd p20, p20, p3
pfree p3
dload x10, x11, p3, 0, 1, 32
pmul p2, p2, p3, 1
pmul p20, p20, p3, 1
pfree p3
pntt p2, p1, 0, 0, 0
pntt p20, p1, 0, 0, 0
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 1, 0, 0
pntt p20, p3, 1, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 2, 0, 0
pntt p20, p3, 2, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 3, 0, 0
pntt p20, p3, 3, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 4, 0, 0
pntt p20, p3, 4, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 5, 0, 0
pntt p20, p3, 5, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 6, 0, 0
pntt p20, p3, 6, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 7, 0, 0
pntt p20, p3, 7, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 8, 0, 0
pntt p20, p3, 8, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 9, 0, 0
pntt p20, p3, 9, 0, 0
pfree p3
psub p21, p21, p2
pfree p2
psub p22, p22, p20
pfree p20
pmul p21, p21, p23
dstore x10, x11, p21, 1, 0
pmul p22, p22, p23
pfree p23
dstore x10, x11, p22, 1, 0
pmodld 2
pmul p0, p0, p24
padd p0, p0, p27
pfree p27
pmul p13, p13, p24
pfree p24
padd p13, p13, p14
pfree p14
dload x10, x11, p2, 0, 1, 32
pmul p0, p0, p2, 1
pmul p13, p13, p2, 1
pfree p2
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
pntt p13, p1, 9, 0, 0
pfree p1
dload x10, x11, p1, 0, 0, 0
psub p1, p1, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
psub p0, p0, p13
pfree p13
dload x10, x11, p2, 0, 0, 0
pmul p1, p1, p2
dstore x10, x11, p1, 1, 0
pmul p0, p0, p2
psync
pfree p2
dstore x10, x11, p0, 1, 0
psync
