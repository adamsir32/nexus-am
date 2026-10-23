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
pintt p0, p12, 10, 0, 0
dload x10, x11, p13, 0, 1, 32
pintt p0, p13, 11, 0, 0
dload x10, x11, p14, 0, 1, 32
pmul p0, p0, p14, 1
dload x10, x11, p15, 0, 0, 0
pintt p15, p1, 0, 0, 0
pfree p1
pintt p15, p2, 1, 0, 0
pfree p2
pintt p15, p3, 2, 0, 0
pfree p3
pintt p15, p5, 3, 0, 0
pfree p5
pintt p15, p6, 4, 0, 0
pfree p6
pintt p15, p7, 5, 0, 0
pfree p7
pintt p15, p8, 6, 0, 0
pfree p8
pintt p15, p9, 7, 0, 0
pfree p9
pintt p15, p10, 8, 0, 0
pfree p10
pintt p15, p11, 9, 0, 0
pfree p11
pintt p15, p12, 10, 0, 0
pfree p12
pintt p15, p13, 11, 0, 0
pfree p13
pmul p15, p15, p14, 1
pfree p14
dload x10, x11, p1, 0, 1, 32
pmul p2, p15, p1, 1
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
dload x10, x11, p13, 0, 1, 32
pntt p2, p13, 9, 0, 0
dload x10, x11, p14, 0, 1, 32
pntt p2, p14, 10, 0, 0
dload x10, x11, p16, 0, 1, 32
pntt p2, p16, 11, 0, 0
dload x10, x11, p17, 0, 0, 0
pmul p15, p15, p17
pfree p17
pmodld 1
dload x10, x11, p17, 0, 0, 0
pmul p17, p15, p17
dload x10, x11, p18, 0, 1, 32
pmul p17, p17, p18, 1
pfree p16
dload x10, x11, p19, 0, 1, 32
pntt p17, p19, 0, 0, 0
pfree p14
dload x10, x11, p16, 0, 1, 32
pntt p17, p16, 1, 0, 0
pfree p13
dload x10, x11, p14, 0, 1, 32
pntt p17, p14, 2, 0, 0
pfree p12
dload x10, x11, p13, 0, 1, 32
pntt p17, p13, 3, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pntt p17, p12, 4, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pntt p17, p11, 5, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pntt p17, p10, 6, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pntt p17, p9, 7, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pntt p17, p8, 8, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pntt p17, p7, 9, 0, 0
pfree p5
dload x10, x11, p6, 0, 1, 32
pntt p17, p6, 10, 0, 0
pfree p3
dload x10, x11, p5, 0, 1, 32
pntt p17, p5, 11, 0, 0
pmodld 2
dload x10, x11, p3, 0, 0, 0
pmul p15, p15, p3
pfree p3
pfree p1
dload x10, x11, p3, 0, 1, 32
pmul p15, p15, p3, 1
pfree p3
dload x10, x11, p1, 0, 1, 32
pntt p15, p1, 0, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p15, p3, 1, 0, 0
pfree p3
dload x10, x11, p1, 0, 1, 32
pntt p15, p1, 2, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p15, p3, 3, 0, 0
pfree p3
dload x10, x11, p1, 0, 1, 32
pntt p15, p1, 4, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p15, p3, 5, 0, 0
pfree p3
dload x10, x11, p1, 0, 1, 32
pntt p15, p1, 6, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p15, p3, 7, 0, 0
pfree p3
dload x10, x11, p1, 0, 1, 32
pntt p15, p1, 8, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p15, p3, 9, 0, 0
pfree p3
dload x10, x11, p1, 0, 1, 32
pntt p15, p1, 10, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p15, p3, 11, 0, 0
pmodld 0
dload x10, x11, p1, 0, 0, 0
pmul p1, p2, p1
dload x10, x11, p20, 0, 0, 0
pmul p2, p2, p20
pfree p20
pmodld 1
dload x10, x11, p20, 0, 0, 0
pmul p20, p17, p20
dload x10, x11, p21, 0, 0, 0
pmul p17, p17, p21
pfree p21
pmodld 2
dload x10, x11, p21, 0, 0, 0
pmul p21, p15, p21
dload x10, x11, p22, 0, 0, 0
pmul p15, p15, p22
pfree p22
pmodld 1
dload x10, x11, p22, 0, 0, 0
pfree p3
dload x10, x11, p23, 0, 1, 32
pintt p22, p23, 0, 0, 0
pfree p5
dload x10, x11, p3, 0, 1, 32
pintt p22, p3, 1, 0, 0
pfree p6
dload x10, x11, p5, 0, 1, 32
pintt p22, p5, 2, 0, 0
pfree p7
dload x10, x11, p6, 0, 1, 32
pintt p22, p6, 3, 0, 0
pfree p8
dload x10, x11, p7, 0, 1, 32
pintt p22, p7, 4, 0, 0
pfree p9
dload x10, x11, p8, 0, 1, 32
pintt p22, p8, 5, 0, 0
pfree p10
dload x10, x11, p9, 0, 1, 32
pintt p22, p9, 6, 0, 0
pfree p11
dload x10, x11, p10, 0, 1, 32
pintt p22, p10, 7, 0, 0
pfree p12
dload x10, x11, p11, 0, 1, 32
pintt p22, p11, 8, 0, 0
pfree p13
dload x10, x11, p12, 0, 1, 32
pintt p22, p12, 9, 0, 0
pfree p14
dload x10, x11, p13, 0, 1, 32
pintt p22, p13, 10, 0, 0
pfree p16
dload x10, x11, p14, 0, 1, 32
pintt p22, p14, 11, 0, 0
pfree p19
dload x10, x11, p16, 0, 1, 32
pmul p22, p22, p16, 1
dload x10, x11, p19, 0, 0, 0
pintt p19, p23, 0, 0, 0
pfree p23
pintt p19, p3, 1, 0, 0
pfree p3
pintt p19, p5, 2, 0, 0
pfree p5
pintt p19, p6, 3, 0, 0
pfree p6
pintt p19, p7, 4, 0, 0
pfree p7
pintt p19, p8, 5, 0, 0
pfree p8
pintt p19, p9, 6, 0, 0
pfree p9
pintt p19, p10, 7, 0, 0
pfree p10
pintt p19, p11, 8, 0, 0
pfree p11
pintt p19, p12, 9, 0, 0
pfree p12
pintt p19, p13, 10, 0, 0
pfree p13
pintt p19, p14, 11, 0, 0
pfree p14
pmul p19, p19, p16, 1
pfree p16
pmul p3, p19, p18, 1
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 0, 0, 0
dload x10, x11, p6, 0, 1, 32
pntt p3, p6, 1, 0, 0
dload x10, x11, p7, 0, 1, 32
pntt p3, p7, 2, 0, 0
dload x10, x11, p8, 0, 1, 32
pntt p3, p8, 3, 0, 0
dload x10, x11, p9, 0, 1, 32
pntt p3, p9, 4, 0, 0
dload x10, x11, p10, 0, 1, 32
pntt p3, p10, 5, 0, 0
dload x10, x11, p11, 0, 1, 32
pntt p3, p11, 6, 0, 0
dload x10, x11, p12, 0, 1, 32
pntt p3, p12, 7, 0, 0
dload x10, x11, p13, 0, 1, 32
pntt p3, p13, 8, 0, 0
dload x10, x11, p14, 0, 1, 32
pntt p3, p14, 9, 0, 0
dload x10, x11, p16, 0, 1, 32
pntt p3, p16, 10, 0, 0
dload x10, x11, p23, 0, 1, 32
pntt p3, p23, 11, 0, 0
dload x10, x11, p24, 0, 0, 0
pmul p19, p19, p24
pfree p24
dload x10, x11, p24, 0, 0, 0
pmac p20, p3, p24
pfree p24
dload x10, x11, p24, 0, 1, 32
pintt p20, p24, 0, 0, 0
pfree p23
dload x10, x11, p25, 0, 1, 32
pintt p20, p25, 1, 0, 0
pfree p16
dload x10, x11, p23, 0, 1, 32
pintt p20, p23, 2, 0, 0
pfree p14
dload x10, x11, p16, 0, 1, 32
pintt p20, p16, 3, 0, 0
pfree p13
dload x10, x11, p14, 0, 1, 32
pintt p20, p14, 4, 0, 0
pfree p12
dload x10, x11, p13, 0, 1, 32
pintt p20, p13, 5, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pintt p20, p12, 6, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pintt p20, p11, 7, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pintt p20, p10, 8, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pintt p20, p9, 9, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pintt p20, p8, 10, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pintt p20, p7, 11, 0, 0
pfree p5
dload x10, x11, p6, 0, 1, 32
pmul p20, p20, p6, 1
dload x10, x11, p5, 0, 0, 0
pmac p17, p3, p5
pfree p3
pfree p5
pintt p17, p24, 0, 0, 0
pfree p24
pintt p17, p25, 1, 0, 0
pfree p25
pintt p17, p23, 2, 0, 0
pfree p23
pintt p17, p16, 3, 0, 0
pfree p16
pintt p17, p14, 4, 0, 0
pfree p14
pintt p17, p13, 5, 0, 0
pfree p13
pintt p17, p12, 6, 0, 0
pfree p12
pintt p17, p11, 7, 0, 0
pfree p11
pintt p17, p10, 8, 0, 0
pfree p10
pintt p17, p9, 9, 0, 0
pfree p9
pintt p17, p8, 10, 0, 0
pfree p8
pintt p17, p7, 11, 0, 0
pfree p7
pmul p17, p17, p6, 1
pfree p6
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p3, p19, p3
dload x10, x11, p5, 0, 1, 32
pmul p3, p3, p5, 1
dload x10, x11, p6, 0, 1, 32
pntt p3, p6, 0, 0, 0
dload x10, x11, p7, 0, 1, 32
pntt p3, p7, 1, 0, 0
dload x10, x11, p8, 0, 1, 32
pntt p3, p8, 2, 0, 0
dload x10, x11, p9, 0, 1, 32
pntt p3, p9, 3, 0, 0
dload x10, x11, p10, 0, 1, 32
pntt p3, p10, 4, 0, 0
dload x10, x11, p11, 0, 1, 32
pntt p3, p11, 5, 0, 0
dload x10, x11, p12, 0, 1, 32
pntt p3, p12, 6, 0, 0
dload x10, x11, p13, 0, 1, 32
pntt p3, p13, 7, 0, 0
dload x10, x11, p14, 0, 1, 32
pntt p3, p14, 8, 0, 0
dload x10, x11, p16, 0, 1, 32
pntt p3, p16, 9, 0, 0
dload x10, x11, p23, 0, 1, 32
pntt p3, p23, 10, 0, 0
dload x10, x11, p24, 0, 1, 32
pntt p3, p24, 11, 0, 0
pmodld 2
dload x10, x11, p25, 0, 0, 0
pmul p19, p19, p25
pfree p25
pfree p18
dload x10, x11, p25, 0, 1, 32
pmul p19, p19, p25, 1
pfree p25
dload x10, x11, p18, 0, 1, 32
pntt p19, p18, 0, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pntt p19, p18, 1, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pntt p19, p18, 2, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pntt p19, p18, 3, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pntt p19, p18, 4, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pntt p19, p18, 5, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pntt p19, p18, 6, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pntt p19, p18, 7, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pntt p19, p18, 8, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pntt p19, p18, 9, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pntt p19, p18, 10, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pntt p19, p18, 11, 0, 0
pfree p18
pmodld 0
dload x10, x11, p18, 0, 0, 0
pmac p1, p3, p18
pfree p18
dload x10, x11, p18, 0, 1, 32
pintt p1, p18, 0, 0, 0
pfree p24
dload x10, x11, p25, 0, 1, 32
pintt p1, p25, 1, 0, 0
pfree p23
dload x10, x11, p24, 0, 1, 32
pintt p1, p24, 2, 0, 0
pfree p16
dload x10, x11, p23, 0, 1, 32
pintt p1, p23, 3, 0, 0
pfree p14
dload x10, x11, p16, 0, 1, 32
pintt p1, p16, 4, 0, 0
pfree p13
dload x10, x11, p14, 0, 1, 32
pintt p1, p14, 5, 0, 0
pfree p12
dload x10, x11, p13, 0, 1, 32
pintt p1, p13, 6, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pintt p1, p12, 7, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pintt p1, p11, 8, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pintt p1, p10, 9, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pintt p1, p9, 10, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pintt p1, p8, 11, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pmul p1, p1, p7, 1
dload x10, x11, p6, 0, 0, 0
pmac p2, p3, p6
pfree p3
pfree p6
pintt p2, p18, 0, 0, 0
pfree p18
pintt p2, p25, 1, 0, 0
pfree p25
pintt p2, p24, 2, 0, 0
pfree p24
pintt p2, p23, 3, 0, 0
pfree p23
pintt p2, p16, 4, 0, 0
pfree p16
pintt p2, p14, 5, 0, 0
pfree p14
pintt p2, p13, 6, 0, 0
pfree p13
pintt p2, p12, 7, 0, 0
pfree p12
pintt p2, p11, 8, 0, 0
pfree p11
pintt p2, p10, 9, 0, 0
pfree p10
pintt p2, p9, 10, 0, 0
pfree p9
pintt p2, p8, 11, 0, 0
pfree p8
pmul p2, p2, p7, 1
pfree p7
pmodld 2
dload x10, x11, p3, 0, 0, 0
pmac p21, p19, p3
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p21, p3, 0, 0, 0
dload x10, x11, p6, 0, 1, 32
pintt p21, p6, 1, 0, 0
dload x10, x11, p7, 0, 1, 32
pintt p21, p7, 2, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p21, p8, 3, 0, 0
dload x10, x11, p9, 0, 1, 32
pintt p21, p9, 4, 0, 0
dload x10, x11, p10, 0, 1, 32
pintt p21, p10, 5, 0, 0
dload x10, x11, p11, 0, 1, 32
pintt p21, p11, 6, 0, 0
dload x10, x11, p12, 0, 1, 32
pintt p21, p12, 7, 0, 0
dload x10, x11, p13, 0, 1, 32
pintt p21, p13, 8, 0, 0
dload x10, x11, p14, 0, 1, 32
pintt p21, p14, 9, 0, 0
dload x10, x11, p16, 0, 1, 32
pintt p21, p16, 10, 0, 0
dload x10, x11, p18, 0, 1, 32
pintt p21, p18, 11, 0, 0
dload x10, x11, p23, 0, 1, 32
pmul p21, p21, p23, 1
dload x10, x11, p24, 0, 0, 0
pmac p15, p19, p24
pfree p19
pfree p24
pintt p15, p3, 0, 0, 0
pfree p3
pintt p15, p6, 1, 0, 0
pfree p6
pintt p15, p7, 2, 0, 0
pfree p7
pintt p15, p8, 3, 0, 0
pfree p8
pintt p15, p9, 4, 0, 0
pfree p9
pintt p15, p10, 5, 0, 0
pfree p10
pintt p15, p11, 6, 0, 0
pfree p11
pintt p15, p12, 7, 0, 0
pfree p12
pintt p15, p13, 8, 0, 0
pfree p13
pintt p15, p14, 9, 0, 0
pfree p14
pintt p15, p16, 10, 0, 0
pfree p16
pintt p15, p18, 11, 0, 0
pfree p18
pmul p15, p15, p23, 1
pfree p23
pmodld 0
dload x10, x11, p3, 0, 0, 0
padd p1, p1, p3
padd p2, p2, p3
pfree p3
pmodld 1
dload x10, x11, p3, 0, 0, 0
padd p20, p20, p3
padd p17, p17, p3
pfree p3
pmodld 2
dload x10, x11, p3, 0, 0, 0
padd p21, p21, p3
padd p15, p15, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
pmul p21, p21, p3
pmul p15, p15, p3
pfree p3
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p6, p21, p3
psub p1, p1, p6
pfree p6
pmul p3, p15, p3
psub p2, p2, p3
pfree p3
pmodld 1
dload x10, x11, p3, 0, 0, 0
pmul p21, p21, p3
psub p20, p20, p21
pfree p21
pmul p15, p15, p3
pfree p3
psub p17, p17, p15
pfree p15
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p1, p1, p3
pmul p2, p2, p3
pfree p3
padd p1, p1, p0
pfree p0
pmul p1, p1, p5, 1
pmul p2, p2, p5, 1
pfree p5
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 0, 0, 0
pntt p2, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 1, 0, 0
pntt p2, p0, 1, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 2, 0, 0
pntt p2, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 3, 0, 0
pntt p2, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 4, 0, 0
pntt p2, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 5, 0, 0
pntt p2, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 6, 0, 0
pntt p2, p0, 6, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 7, 0, 0
pntt p2, p0, 7, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 8, 0, 0
pntt p2, p0, 8, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 9, 0, 0
pntt p2, p0, 9, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 10, 0, 0
pntt p2, p0, 10, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 11, 0, 0
dstore x10, x11, p1, 1, 0
pntt p2, p0, 11, 0, 0
pfree p0
dstore x10, x11, p2, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p20, p20, p0
pmul p17, p17, p0
pfree p0
padd p20, p20, p22
pfree p22
dload x10, x11, p0, 0, 1, 32
pmul p20, p20, p0, 1
pmul p17, p17, p0, 1
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 0, 0, 0
pntt p17, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 1, 0, 0
pntt p17, p0, 1, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 2, 0, 0
pntt p17, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 3, 0, 0
pntt p17, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 4, 0, 0
pntt p17, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 5, 0, 0
pntt p17, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 6, 0, 0
pntt p17, p0, 6, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 7, 0, 0
pntt p17, p0, 7, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 8, 0, 0
pntt p17, p0, 8, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 9, 0, 0
pntt p17, p0, 9, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 10, 0, 0
pntt p17, p0, 10, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 11, 0, 0
dstore x10, x11, p20, 1, 0
pntt p17, p0, 11, 0, 0
pfree p0
dstore x10, x11, p17, 1, 0
psync
