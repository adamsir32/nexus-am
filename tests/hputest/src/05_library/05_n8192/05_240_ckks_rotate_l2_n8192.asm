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
pintt p0, p14, 12, 0, 0
dload x10, x11, p15, 0, 1, 32
pmul p0, p0, p15, 1
dload x10, x11, p16, 0, 0, 0
pintt p16, p1, 0, 0, 0
pfree p1
pintt p16, p2, 1, 0, 0
pfree p2
pintt p16, p3, 2, 0, 0
pfree p3
pintt p16, p5, 3, 0, 0
pfree p5
pintt p16, p6, 4, 0, 0
pfree p6
pintt p16, p7, 5, 0, 0
pfree p7
pintt p16, p8, 6, 0, 0
pfree p8
pintt p16, p9, 7, 0, 0
pfree p9
pintt p16, p10, 8, 0, 0
pfree p10
pintt p16, p11, 9, 0, 0
pfree p11
pintt p16, p12, 10, 0, 0
pfree p12
pintt p16, p13, 11, 0, 0
pfree p13
pintt p16, p14, 12, 0, 0
pfree p14
pmul p16, p16, p15, 1
pfree p15
dload x10, x11, p1, 0, 1, 32
pmul p2, p16, p1, 1
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
dload x10, x11, p15, 0, 1, 32
pntt p2, p15, 11, 0, 0
dload x10, x11, p17, 0, 1, 32
pntt p2, p17, 12, 0, 0
dload x10, x11, p18, 0, 0, 0
pmul p16, p16, p18
pfree p18
pmodld 1
dload x10, x11, p18, 0, 0, 0
pmul p18, p16, p18
pfree p17
dload x10, x11, p19, 0, 1, 32
pmul p18, p18, p19, 1
pfree p15
dload x10, x11, p17, 0, 1, 32
pntt p18, p17, 0, 0, 0
pfree p14
dload x10, x11, p15, 0, 1, 32
pntt p18, p15, 1, 0, 0
pfree p13
dload x10, x11, p14, 0, 1, 32
pntt p18, p14, 2, 0, 0
pfree p12
dload x10, x11, p13, 0, 1, 32
pntt p18, p13, 3, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pntt p18, p12, 4, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pntt p18, p11, 5, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pntt p18, p10, 6, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pntt p18, p9, 7, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pntt p18, p8, 8, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pntt p18, p7, 9, 0, 0
pfree p5
dload x10, x11, p6, 0, 1, 32
pntt p18, p6, 10, 0, 0
pfree p3
dload x10, x11, p5, 0, 1, 32
pntt p18, p5, 11, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p18, p3, 12, 0, 0
pmodld 2
dload x10, x11, p1, 0, 0, 0
pmul p16, p16, p1
pfree p1
pfree p3
dload x10, x11, p1, 0, 1, 32
pmul p16, p16, p1, 1
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p16, p3, 0, 0, 0
pfree p3
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 1, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p16, p3, 2, 0, 0
pfree p3
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 3, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p16, p3, 4, 0, 0
pfree p3
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 5, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p16, p3, 6, 0, 0
pfree p3
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 7, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p16, p3, 8, 0, 0
pfree p3
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 9, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p16, p3, 10, 0, 0
pfree p3
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 11, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p16, p3, 12, 0, 0
pmodld 0
dload x10, x11, p1, 0, 0, 0
pmul p1, p2, p1
dload x10, x11, p20, 0, 0, 0
pmul p2, p2, p20
pfree p20
pmodld 1
dload x10, x11, p20, 0, 0, 0
pmul p20, p18, p20
dload x10, x11, p21, 0, 0, 0
pmul p18, p18, p21
pfree p21
pmodld 2
dload x10, x11, p21, 0, 0, 0
pmul p21, p16, p21
dload x10, x11, p22, 0, 0, 0
pmul p16, p16, p22
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
pfree p15
dload x10, x11, p14, 0, 1, 32
pintt p22, p14, 11, 0, 0
pfree p17
dload x10, x11, p15, 0, 1, 32
pintt p22, p15, 12, 0, 0
pfree p19
dload x10, x11, p17, 0, 1, 32
pmul p22, p22, p17, 1
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
pintt p19, p15, 12, 0, 0
pfree p15
pmul p19, p19, p17, 1
pfree p17
dload x10, x11, p3, 0, 1, 32
pmul p5, p19, p3, 1
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 0, 0, 0
dload x10, x11, p7, 0, 1, 32
pntt p5, p7, 1, 0, 0
dload x10, x11, p8, 0, 1, 32
pntt p5, p8, 2, 0, 0
dload x10, x11, p9, 0, 1, 32
pntt p5, p9, 3, 0, 0
dload x10, x11, p10, 0, 1, 32
pntt p5, p10, 4, 0, 0
dload x10, x11, p11, 0, 1, 32
pntt p5, p11, 5, 0, 0
dload x10, x11, p12, 0, 1, 32
pntt p5, p12, 6, 0, 0
dload x10, x11, p13, 0, 1, 32
pntt p5, p13, 7, 0, 0
dload x10, x11, p14, 0, 1, 32
pntt p5, p14, 8, 0, 0
dload x10, x11, p15, 0, 1, 32
pntt p5, p15, 9, 0, 0
dload x10, x11, p17, 0, 1, 32
pntt p5, p17, 10, 0, 0
dload x10, x11, p23, 0, 1, 32
pntt p5, p23, 11, 0, 0
dload x10, x11, p24, 0, 1, 32
pntt p5, p24, 12, 0, 0
dload x10, x11, p25, 0, 0, 0
pmul p19, p19, p25
pfree p25
dload x10, x11, p25, 0, 0, 0
pmac p20, p5, p25
pfree p25
pfree p24
dload x10, x11, p25, 0, 1, 32
pintt p20, p25, 0, 0, 0
pfree p23
dload x10, x11, p24, 0, 1, 32
pintt p20, p24, 1, 0, 0
pfree p17
dload x10, x11, p23, 0, 1, 32
pintt p20, p23, 2, 0, 0
pfree p15
dload x10, x11, p17, 0, 1, 32
pintt p20, p17, 3, 0, 0
pfree p14
dload x10, x11, p15, 0, 1, 32
pintt p20, p15, 4, 0, 0
pfree p13
dload x10, x11, p14, 0, 1, 32
pintt p20, p14, 5, 0, 0
pfree p12
dload x10, x11, p13, 0, 1, 32
pintt p20, p13, 6, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pintt p20, p12, 7, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pintt p20, p11, 8, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pintt p20, p10, 9, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pintt p20, p9, 10, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pintt p20, p8, 11, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pintt p20, p7, 12, 0, 0
pfree p3
dload x10, x11, p6, 0, 1, 32
pmul p20, p20, p6, 1
dload x10, x11, p3, 0, 0, 0
pmac p18, p5, p3
pfree p5
pfree p3
pintt p18, p25, 0, 0, 0
pfree p25
pintt p18, p24, 1, 0, 0
pfree p24
pintt p18, p23, 2, 0, 0
pfree p23
pintt p18, p17, 3, 0, 0
pfree p17
pintt p18, p15, 4, 0, 0
pfree p15
pintt p18, p14, 5, 0, 0
pfree p14
pintt p18, p13, 6, 0, 0
pfree p13
pintt p18, p12, 7, 0, 0
pfree p12
pintt p18, p11, 8, 0, 0
pfree p11
pintt p18, p10, 9, 0, 0
pfree p10
pintt p18, p9, 10, 0, 0
pfree p9
pintt p18, p8, 11, 0, 0
pfree p8
pintt p18, p7, 12, 0, 0
pfree p7
pmul p18, p18, p6, 1
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
dload x10, x11, p15, 0, 1, 32
pntt p3, p15, 9, 0, 0
dload x10, x11, p17, 0, 1, 32
pntt p3, p17, 10, 0, 0
dload x10, x11, p23, 0, 1, 32
pntt p3, p23, 11, 0, 0
dload x10, x11, p24, 0, 1, 32
pntt p3, p24, 12, 0, 0
pmodld 2
dload x10, x11, p25, 0, 0, 0
pmul p19, p19, p25
pfree p25
pfree p24
dload x10, x11, p25, 0, 1, 32
pmul p19, p19, p25, 1
pfree p25
dload x10, x11, p24, 0, 1, 32
pntt p19, p24, 0, 0, 0
pfree p24
dload x10, x11, p24, 0, 1, 32
pntt p19, p24, 1, 0, 0
pfree p24
dload x10, x11, p24, 0, 1, 32
pntt p19, p24, 2, 0, 0
pfree p24
dload x10, x11, p24, 0, 1, 32
pntt p19, p24, 3, 0, 0
pfree p24
dload x10, x11, p24, 0, 1, 32
pntt p19, p24, 4, 0, 0
pfree p24
dload x10, x11, p24, 0, 1, 32
pntt p19, p24, 5, 0, 0
pfree p24
dload x10, x11, p24, 0, 1, 32
pntt p19, p24, 6, 0, 0
pfree p24
dload x10, x11, p24, 0, 1, 32
pntt p19, p24, 7, 0, 0
pfree p24
dload x10, x11, p24, 0, 1, 32
pntt p19, p24, 8, 0, 0
pfree p24
dload x10, x11, p24, 0, 1, 32
pntt p19, p24, 9, 0, 0
pfree p24
dload x10, x11, p24, 0, 1, 32
pntt p19, p24, 10, 0, 0
pfree p24
dload x10, x11, p24, 0, 1, 32
pntt p19, p24, 11, 0, 0
pfree p24
dload x10, x11, p24, 0, 1, 32
pntt p19, p24, 12, 0, 0
pfree p24
pmodld 0
dload x10, x11, p24, 0, 0, 0
pmac p1, p3, p24
pfree p24
dload x10, x11, p24, 0, 1, 32
pintt p1, p24, 0, 0, 0
pfree p23
dload x10, x11, p25, 0, 1, 32
pintt p1, p25, 1, 0, 0
pfree p17
dload x10, x11, p23, 0, 1, 32
pintt p1, p23, 2, 0, 0
pfree p15
dload x10, x11, p17, 0, 1, 32
pintt p1, p17, 3, 0, 0
pfree p14
dload x10, x11, p15, 0, 1, 32
pintt p1, p15, 4, 0, 0
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
pintt p1, p7, 12, 0, 0
pfree p5
dload x10, x11, p6, 0, 1, 32
pmul p1, p1, p6, 1
dload x10, x11, p5, 0, 0, 0
pmac p2, p3, p5
pfree p3
pfree p5
pintt p2, p24, 0, 0, 0
pfree p24
pintt p2, p25, 1, 0, 0
pfree p25
pintt p2, p23, 2, 0, 0
pfree p23
pintt p2, p17, 3, 0, 0
pfree p17
pintt p2, p15, 4, 0, 0
pfree p15
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
pintt p2, p7, 12, 0, 0
pfree p7
pmul p2, p2, p6, 1
pfree p6
pmodld 2
dload x10, x11, p3, 0, 0, 0
pmac p21, p19, p3
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p21, p3, 0, 0, 0
dload x10, x11, p5, 0, 1, 32
pintt p21, p5, 1, 0, 0
dload x10, x11, p6, 0, 1, 32
pintt p21, p6, 2, 0, 0
dload x10, x11, p7, 0, 1, 32
pintt p21, p7, 3, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p21, p8, 4, 0, 0
dload x10, x11, p9, 0, 1, 32
pintt p21, p9, 5, 0, 0
dload x10, x11, p10, 0, 1, 32
pintt p21, p10, 6, 0, 0
dload x10, x11, p11, 0, 1, 32
pintt p21, p11, 7, 0, 0
dload x10, x11, p12, 0, 1, 32
pintt p21, p12, 8, 0, 0
dload x10, x11, p13, 0, 1, 32
pintt p21, p13, 9, 0, 0
dload x10, x11, p14, 0, 1, 32
pintt p21, p14, 10, 0, 0
dload x10, x11, p15, 0, 1, 32
pintt p21, p15, 11, 0, 0
dload x10, x11, p17, 0, 1, 32
pintt p21, p17, 12, 0, 0
dload x10, x11, p23, 0, 1, 32
pmul p21, p21, p23, 1
dload x10, x11, p24, 0, 0, 0
pmac p16, p19, p24
pfree p19
pfree p24
pintt p16, p3, 0, 0, 0
pfree p3
pintt p16, p5, 1, 0, 0
pfree p5
pintt p16, p6, 2, 0, 0
pfree p6
pintt p16, p7, 3, 0, 0
pfree p7
pintt p16, p8, 4, 0, 0
pfree p8
pintt p16, p9, 5, 0, 0
pfree p9
pintt p16, p10, 6, 0, 0
pfree p10
pintt p16, p11, 7, 0, 0
pfree p11
pintt p16, p12, 8, 0, 0
pfree p12
pintt p16, p13, 9, 0, 0
pfree p13
pintt p16, p14, 10, 0, 0
pfree p14
pintt p16, p15, 11, 0, 0
pfree p15
pintt p16, p17, 12, 0, 0
pfree p17
pmul p16, p16, p23, 1
pfree p23
pmodld 0
dload x10, x11, p3, 0, 0, 0
padd p1, p1, p3
padd p2, p2, p3
pfree p3
pmodld 1
dload x10, x11, p3, 0, 0, 0
padd p20, p20, p3
padd p18, p18, p3
pfree p3
pmodld 2
dload x10, x11, p3, 0, 0, 0
padd p21, p21, p3
padd p16, p16, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
pmul p21, p21, p3
pmul p16, p16, p3
pfree p3
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p5, p21, p3
psub p1, p1, p5
pfree p5
pmul p3, p16, p3
psub p2, p2, p3
pfree p3
pmodld 1
dload x10, x11, p3, 0, 0, 0
pmul p21, p21, p3
psub p20, p20, p21
pfree p21
pmul p16, p16, p3
pfree p3
psub p18, p18, p16
pfree p16
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p1, p1, p3
pmul p2, p2, p3
pfree p3
padd p1, p1, p0
pfree p0
dload x10, x11, p0, 0, 1, 32
pmul p1, p1, p0, 1
pmul p2, p2, p0, 1
pfree p0
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
pntt p2, p0, 11, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p1, p0, 12, 0, 0
dstore x10, x11, p1, 1, 0
pntt p2, p0, 12, 0, 0
pfree p0
dstore x10, x11, p2, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p20, p20, p0
pmul p18, p18, p0
pfree p0
padd p20, p20, p22
pfree p22
dload x10, x11, p0, 0, 1, 32
pmul p20, p20, p0, 1
pmul p18, p18, p0, 1
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 0, 0, 0
pntt p18, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 1, 0, 0
pntt p18, p0, 1, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 2, 0, 0
pntt p18, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 3, 0, 0
pntt p18, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 4, 0, 0
pntt p18, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 5, 0, 0
pntt p18, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 6, 0, 0
pntt p18, p0, 6, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 7, 0, 0
pntt p18, p0, 7, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 8, 0, 0
pntt p18, p0, 8, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 9, 0, 0
pntt p18, p0, 9, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 10, 0, 0
pntt p18, p0, 10, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 11, 0, 0
pntt p18, p0, 11, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p20, p0, 12, 0, 0
dstore x10, x11, p20, 1, 0
pntt p18, p0, 12, 0, 0
pfree p0
dstore x10, x11, p18, 1, 0
psync
