dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
pmul p1, p0, p0
dload x10, x11, p2, 0, 0, 0
pmul p2, p1, p2
dload x10, x11, p3, 0, 0, 0
pmul p5, p3, p0
dload x10, x11, p6, 0, 0, 0
pmac p5, p0, p6
pfree p0
pmul p3, p3, p6
pfree p6
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p6, p0, p0
dload x10, x11, p7, 0, 0, 0
pmul p8, p7, p0
dload x10, x11, p9, 0, 0, 0
pmac p8, p0, p9
pfree p0
pmul p7, p7, p9
pfree p9
pmodld 0
dstore x10, x11, p1, 0, 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p9, 0, 1, 32
pintt p0, p9, 0, 0, 0
pmodld 1
dstore x10, x11, p6, 0, 0
dload x10, x11, p10, 0, 0, 0
pintt p10, p9, 0, 0, 0
pmodld 0
dload x10, x11, p11, 0, 1, 32
pintt p0, p11, 1, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p0, p11, 2, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p0, p11, 3, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p0, p11, 4, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p0, p11, 5, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p0, p11, 6, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pmul p0, p0, p11, 1
pfree p11
pmodld 1
pmul p11, p0, 1
pmodld 2
pmul p0, p0, 1
pmodld 1
dload x10, x11, p12, 0, 1, 32
pintt p10, p12, 1, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p10, p12, 2, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p10, p12, 3, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p10, p12, 4, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p10, p12, 5, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p10, p12, 6, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pmul p10, p10, p12, 1
pfree p12
pmodld 0
pmul p12, p10, 1
pmodld 2
pmul p10, p10, 1
pmodld 0
dload x10, x11, p13, 0, 0, 0
pmul p1, p1, p13
pmodld 1
dload x10, x11, p14, 0, 1, 32
pmul p11, p11, p14, 1
pntt p11, p9, 0, 0, 0
dload x10, x11, p15, 0, 1, 32
pntt p11, p15, 1, 0, 0
dload x10, x11, p16, 0, 1, 32
pntt p11, p16, 2, 0, 0
dload x10, x11, p17, 0, 1, 32
pntt p11, p17, 3, 0, 0
dload x10, x11, p18, 0, 1, 32
pntt p11, p18, 4, 0, 0
dload x10, x11, p19, 0, 1, 32
pntt p11, p19, 5, 0, 0
dload x10, x11, p20, 0, 1, 32
pntt p11, p20, 6, 0, 0
dload x10, x11, p21, 0, 0, 0
pmul p21, p11, p21
dload x10, x11, p22, 0, 0, 0
pmac p21, p6, p22
pfree p22
dload x10, x11, p22, 0, 0, 0
pmul p11, p11, p22
pmac p11, p6, p22
pfree p6
pfree p22
pmodld 2
dload x10, x11, p6, 0, 1, 32
pmul p0, p0, p6, 1
pmul p10, p10, p6, 1
pfree p6
pntt p0, p9, 0, 0, 0
pntt p10, p9, 0, 0, 0
dload x10, x11, p6, 0, 1, 32
pntt p0, p6, 1, 0, 0
pntt p10, p6, 1, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p0, p6, 2, 0, 0
pntt p10, p6, 2, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p0, p6, 3, 0, 0
pntt p10, p6, 3, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p0, p6, 4, 0, 0
pntt p10, p6, 4, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p0, p6, 5, 0, 0
pntt p10, p6, 5, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p0, p6, 6, 0, 0
pntt p10, p6, 6, 0, 0
pfree p6
pmodld 0
dload x10, x11, p6, 0, 1, 32
pmul p12, p12, p6, 1
pntt p12, p9, 0, 0, 0
dload x10, x11, p22, 0, 1, 32
pntt p12, p22, 1, 0, 0
dload x10, x11, p23, 0, 1, 32
pntt p12, p23, 2, 0, 0
dload x10, x11, p24, 0, 1, 32
pntt p12, p24, 3, 0, 0
dload x10, x11, p25, 0, 1, 32
pntt p12, p25, 4, 0, 0
dload x10, x11, p26, 0, 1, 32
pntt p12, p26, 5, 0, 0
pfree p20
dload x10, x11, p27, 0, 1, 32
pntt p12, p27, 6, 0, 0
pmac p1, p12, p13
pfree p13
dload x10, x11, p13, 0, 0, 0
pmac p2, p12, p13
pfree p12
pfree p13
pmodld 2
dload x10, x11, p12, 0, 0, 0
pmul p13, p0, p12
pmac p13, p10, p12
pfree p12
pintt p13, p9, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmul p0, p0, p12
pmac p0, p10, p12
pfree p10
pfree p12
pintt p0, p9, 0, 0, 0
pfree p19
dload x10, x11, p10, 0, 1, 32
pintt p13, p10, 1, 0, 0
pintt p0, p10, 1, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pintt p13, p10, 2, 0, 0
pintt p0, p10, 2, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pintt p13, p10, 3, 0, 0
pintt p0, p10, 3, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pintt p13, p10, 4, 0, 0
pintt p0, p10, 4, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pintt p13, p10, 5, 0, 0
pintt p0, p10, 5, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pintt p13, p10, 6, 0, 0
pintt p0, p10, 6, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pmul p13, p13, p10, 1
pmul p0, p0, p10, 1
pfree p10
pmodld 0
pmul p10, p13, 1
pmodld 1
pmul p12, p13, 1
pmodld 0
pmul p19, p0, 1
pmodld 1
pmul p20, p0, 1
pmodld 3
dload x10, x11, p28, 0, 0, 0
pmul p13, p13, p28
pmul p0, p0, p28
pfree p28
pmodld 0
dload x10, x11, p28, 0, 0, 0
pmul p29, p13, p28
padd p29, p29, p10
pfree p10
pmul p29, p29, p6, 1
pntt p29, p9, 0, 0, 0
pntt p29, p22, 1, 0, 0
pntt p29, p23, 2, 0, 0
pntt p29, p24, 3, 0, 0
pntt p29, p25, 4, 0, 0
pntt p29, p26, 5, 0, 0
pntt p29, p27, 6, 0, 0
psub p2, p2, p29
pfree p29
pmodld 1
pmul p13, p13, p28
padd p13, p13, p12
pfree p12
pmul p13, p13, p14, 1
pntt p13, p9, 0, 0, 0
pntt p13, p15, 1, 0, 0
pntt p13, p16, 2, 0, 0
pntt p13, p17, 3, 0, 0
pntt p13, p18, 4, 0, 0
dload x10, x11, p10, 0, 1, 32
pntt p13, p10, 5, 0, 0
pfree p10
dload x10, x11, p12, 0, 1, 32
pntt p13, p12, 6, 0, 0
psub p21, p21, p13
pfree p13
pmodld 0
pmul p10, p0, p28
padd p10, p10, p19
pfree p19
pmul p10, p10, p6, 1
pfree p6
pmodld 1
pmul p0, p0, p28
pfree p28
padd p0, p0, p20
pfree p20
pmul p0, p0, p14, 1
pfree p14
pmodld 0
pntt p10, p9, 0, 0, 0
pntt p10, p22, 1, 0, 0
pfree p22
pntt p10, p23, 2, 0, 0
pfree p23
pntt p10, p24, 3, 0, 0
pfree p24
pntt p10, p25, 4, 0, 0
pfree p25
pntt p10, p26, 5, 0, 0
pfree p26
pntt p10, p27, 6, 0, 0
pfree p27
psub p1, p1, p10
pfree p10
pmodld 1
pntt p0, p9, 0, 0, 0
pfree p9
pntt p0, p15, 1, 0, 0
pfree p15
pntt p0, p16, 2, 0, 0
pfree p16
pntt p0, p17, 3, 0, 0
pfree p17
pntt p0, p18, 4, 0, 0
pfree p18
dload x10, x11, p6, 0, 1, 32
pntt p0, p6, 5, 0, 0
pfree p6
pntt p0, p12, 6, 0, 0
pfree p12
psub p11, p11, p0
pfree p0
pmodld 0
dload x10, x11, p0, 0, 0, 0
pmul p2, p2, p0
padd p2, p2, p3
pfree p3
dstore x10, x11, p2, 1, 0
pmul p1, p1, p0
pfree p0
padd p1, p1, p5
pfree p5
dstore x10, x11, p1, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p21, p21, p0
padd p21, p21, p7
pfree p7
dstore x10, x11, p21, 1, 0
pmul p11, p11, p0
pfree p0
padd p11, p11, p8
pfree p8
dstore x10, x11, p11, 1, 0
psync
