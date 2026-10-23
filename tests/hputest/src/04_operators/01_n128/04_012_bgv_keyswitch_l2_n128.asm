dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
pmul p1, p0, p1
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p3, 0, 1, 32
pintt p2, p3, 0, 0, 0
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 1, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 2, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 3, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 4, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 5, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 6, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pmul p2, p2, p5, 1
pfree p5
pmodld 1
pmul p5, p2, 1
pmodld 2
pmul p2, p2, 1
pmodld 0
dload x10, x11, p6, 0, 0, 0
pmul p0, p0, p6
pmodld 1
dload x10, x11, p7, 0, 1, 32
pmul p5, p5, p7, 1
pntt p5, p3, 0, 0, 0
dload x10, x11, p8, 0, 1, 32
pntt p5, p8, 1, 0, 0
dload x10, x11, p9, 0, 1, 32
pntt p5, p9, 2, 0, 0
dload x10, x11, p10, 0, 1, 32
pntt p5, p10, 3, 0, 0
dload x10, x11, p11, 0, 1, 32
pntt p5, p11, 4, 0, 0
dload x10, x11, p12, 0, 1, 32
pntt p5, p12, 5, 0, 0
dload x10, x11, p13, 0, 1, 32
pntt p5, p13, 6, 0, 0
dload x10, x11, p14, 0, 0, 0
pmul p14, p5, p14
dload x10, x11, p15, 0, 0, 0
pmul p5, p5, p15
dload x10, x11, p16, 0, 0, 0
pmac p5, p16, p15
pfree p15
dload x10, x11, p15, 0, 0, 0
pintt p15, p3, 0, 0, 0
dload x10, x11, p17, 0, 0, 0
pmac p14, p16, p17
pfree p16
pfree p17
dload x10, x11, p16, 0, 1, 32
pintt p15, p16, 1, 0, 0
pfree p16
dload x10, x11, p16, 0, 1, 32
pintt p15, p16, 2, 0, 0
pfree p16
dload x10, x11, p16, 0, 1, 32
pintt p15, p16, 3, 0, 0
pfree p16
dload x10, x11, p16, 0, 1, 32
pintt p15, p16, 4, 0, 0
pfree p16
dload x10, x11, p16, 0, 1, 32
pintt p15, p16, 5, 0, 0
pfree p16
dload x10, x11, p16, 0, 1, 32
pintt p15, p16, 6, 0, 0
pfree p16
dload x10, x11, p16, 0, 1, 32
pmul p15, p15, p16, 1
pfree p16
pmodld 0
pmul p16, p15, 1
pmodld 2
pmul p15, p15, 1
dload x10, x11, p17, 0, 1, 32
pmul p2, p2, p17, 1
pmul p15, p15, p17, 1
pfree p17
pntt p2, p3, 0, 0, 0
pntt p15, p3, 0, 0, 0
dload x10, x11, p17, 0, 1, 32
pntt p2, p17, 1, 0, 0
pntt p15, p17, 1, 0, 0
pfree p17
dload x10, x11, p17, 0, 1, 32
pntt p2, p17, 2, 0, 0
pntt p15, p17, 2, 0, 0
pfree p17
dload x10, x11, p17, 0, 1, 32
pntt p2, p17, 3, 0, 0
pntt p15, p17, 3, 0, 0
pfree p17
dload x10, x11, p17, 0, 1, 32
pntt p2, p17, 4, 0, 0
pntt p15, p17, 4, 0, 0
pfree p17
dload x10, x11, p17, 0, 1, 32
pntt p2, p17, 5, 0, 0
pntt p15, p17, 5, 0, 0
pfree p17
dload x10, x11, p17, 0, 1, 32
pntt p2, p17, 6, 0, 0
pntt p15, p17, 6, 0, 0
pfree p17
pmodld 0
dload x10, x11, p17, 0, 1, 32
pmul p16, p16, p17, 1
pntt p16, p3, 0, 0, 0
dload x10, x11, p18, 0, 1, 32
pntt p16, p18, 1, 0, 0
dload x10, x11, p19, 0, 1, 32
pntt p16, p19, 2, 0, 0
dload x10, x11, p20, 0, 1, 32
pntt p16, p20, 3, 0, 0
dload x10, x11, p21, 0, 1, 32
pntt p16, p21, 4, 0, 0
dload x10, x11, p22, 0, 1, 32
pntt p16, p22, 5, 0, 0
pfree p13
dload x10, x11, p23, 0, 1, 32
pntt p16, p23, 6, 0, 0
pmac p0, p16, p6
pfree p6
dload x10, x11, p6, 0, 0, 0
pmac p1, p16, p6
pfree p16
pfree p6
pmodld 2
dload x10, x11, p6, 0, 0, 0
pmul p13, p2, p6
pmac p13, p15, p6
pfree p6
pintt p13, p3, 0, 0, 0
dload x10, x11, p6, 0, 0, 0
pmul p2, p2, p6
pmac p2, p15, p6
pfree p15
pfree p6
pintt p2, p3, 0, 0, 0
pfree p12
dload x10, x11, p6, 0, 1, 32
pintt p13, p6, 1, 0, 0
pintt p2, p6, 1, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p13, p6, 2, 0, 0
pintt p2, p6, 2, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p13, p6, 3, 0, 0
pintt p2, p6, 3, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p13, p6, 4, 0, 0
pintt p2, p6, 4, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p13, p6, 5, 0, 0
pintt p2, p6, 5, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p13, p6, 6, 0, 0
pintt p2, p6, 6, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pmul p13, p13, p6, 1
pmul p2, p2, p6, 1
pfree p6
pmodld 0
pmul p6, p13, 1
pmodld 1
pmul p12, p13, 1
pmodld 0
pmul p15, p2, 1
pmodld 1
pmul p16, p2, 1
pmodld 3
dload x10, x11, p24, 0, 0, 0
pmul p13, p13, p24
pmul p2, p2, p24
pfree p24
pmodld 0
dload x10, x11, p24, 0, 0, 0
pmul p25, p13, p24
padd p25, p25, p6
pfree p6
pmul p25, p25, p17, 1
pntt p25, p3, 0, 0, 0
pntt p25, p18, 1, 0, 0
pntt p25, p19, 2, 0, 0
pntt p25, p20, 3, 0, 0
pntt p25, p21, 4, 0, 0
pntt p25, p22, 5, 0, 0
pntt p25, p23, 6, 0, 0
psub p1, p1, p25
pfree p25
pmodld 1
pmul p13, p13, p24
padd p13, p13, p12
pfree p12
pmul p13, p13, p7, 1
pntt p13, p3, 0, 0, 0
pntt p13, p8, 1, 0, 0
pntt p13, p9, 2, 0, 0
pntt p13, p10, 3, 0, 0
pntt p13, p11, 4, 0, 0
dload x10, x11, p6, 0, 1, 32
pntt p13, p6, 5, 0, 0
pfree p6
dload x10, x11, p12, 0, 1, 32
pntt p13, p12, 6, 0, 0
psub p14, p14, p13
pfree p13
pmodld 0
pmul p6, p2, p24
padd p6, p6, p15
pfree p15
pmul p6, p6, p17, 1
pfree p17
pmodld 1
pmul p2, p2, p24
pfree p24
padd p2, p2, p16
pfree p16
pmul p2, p2, p7, 1
pfree p7
pmodld 0
pntt p6, p3, 0, 0, 0
pntt p6, p18, 1, 0, 0
pfree p18
pntt p6, p19, 2, 0, 0
pfree p19
pntt p6, p20, 3, 0, 0
pfree p20
pntt p6, p21, 4, 0, 0
pfree p21
pntt p6, p22, 5, 0, 0
pfree p22
pntt p6, p23, 6, 0, 0
pfree p23
psub p0, p0, p6
pfree p6
pmodld 1
pntt p2, p3, 0, 0, 0
pfree p3
pntt p2, p8, 1, 0, 0
pfree p8
pntt p2, p9, 2, 0, 0
pfree p9
pntt p2, p10, 3, 0, 0
pfree p10
pntt p2, p11, 4, 0, 0
pfree p11
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 5, 0, 0
pfree p3
pntt p2, p12, 6, 0, 0
pfree p12
psub p5, p5, p2
pfree p2
pmodld 0
dload x10, x11, p2, 0, 0, 0
pmul p1, p1, p2
pmul p0, p0, p2
pfree p2
dload x10, x11, p2, 0, 0, 0
padd p1, p1, p2
dstore x10, x11, p1, 1, 0
padd p0, p0, p2
dstore x10, x11, p0, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p14, p14, p0
pmul p5, p5, p0
pfree p0
padd p14, p14, p2
dstore x10, x11, p14, 1, 0
padd p5, p5, p2
pfree p2
dstore x10, x11, p5, 1, 0
psync
