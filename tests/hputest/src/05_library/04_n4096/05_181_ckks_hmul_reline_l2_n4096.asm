dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
pmul p2, p0, p1
dload x10, x11, p3, 0, 1, 32
pintt p2, p3, 0, 0, 0
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 1, 0, 0
dload x10, x11, p6, 0, 1, 32
pintt p2, p6, 2, 0, 0
dload x10, x11, p7, 0, 1, 32
pintt p2, p7, 3, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p2, p8, 4, 0, 0
dload x10, x11, p9, 0, 1, 32
pintt p2, p9, 5, 0, 0
dload x10, x11, p10, 0, 1, 32
pintt p2, p10, 6, 0, 0
dload x10, x11, p11, 0, 1, 32
pintt p2, p11, 7, 0, 0
dload x10, x11, p12, 0, 1, 32
pintt p2, p12, 8, 0, 0
dload x10, x11, p13, 0, 1, 32
pintt p2, p13, 9, 0, 0
dload x10, x11, p14, 0, 1, 32
pintt p2, p14, 10, 0, 0
dload x10, x11, p15, 0, 1, 32
pintt p2, p15, 11, 0, 0
dload x10, x11, p16, 0, 1, 32
pmul p2, p2, p16, 1
dload x10, x11, p17, 0, 0, 0
pmul p0, p0, p17
dload x10, x11, p18, 0, 0, 0
pmac p0, p18, p1
pfree p1
pmul p18, p18, p17
pfree p17
pintt p0, p3, 0, 0, 0
pintt p0, p5, 1, 0, 0
pintt p0, p6, 2, 0, 0
pintt p0, p7, 3, 0, 0
pintt p0, p8, 4, 0, 0
pintt p0, p9, 5, 0, 0
pintt p0, p10, 6, 0, 0
pintt p0, p11, 7, 0, 0
pintt p0, p12, 8, 0, 0
pintt p0, p13, 9, 0, 0
pintt p0, p14, 10, 0, 0
pintt p0, p15, 11, 0, 0
pmul p0, p0, p16, 1
pintt p18, p3, 0, 0, 0
pintt p18, p5, 1, 0, 0
pintt p18, p6, 2, 0, 0
pintt p18, p7, 3, 0, 0
pintt p18, p8, 4, 0, 0
pintt p18, p9, 5, 0, 0
pintt p18, p10, 6, 0, 0
pintt p18, p11, 7, 0, 0
pintt p18, p12, 8, 0, 0
pintt p18, p13, 9, 0, 0
pintt p18, p14, 10, 0, 0
pintt p18, p15, 11, 0, 0
pmul p18, p18, p16, 1
dload x10, x11, p1, 0, 1, 32
pmul p17, p18, p1, 1
pfree p16
dload x10, x11, p19, 0, 1, 32
pntt p17, p19, 0, 0, 0
pfree p15
dload x10, x11, p16, 0, 1, 32
pntt p17, p16, 1, 0, 0
pfree p14
dload x10, x11, p15, 0, 1, 32
pntt p17, p15, 2, 0, 0
pfree p13
dload x10, x11, p14, 0, 1, 32
pntt p17, p14, 3, 0, 0
pfree p12
dload x10, x11, p13, 0, 1, 32
pntt p17, p13, 4, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pntt p17, p12, 5, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pntt p17, p11, 6, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pntt p17, p10, 7, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pntt p17, p9, 8, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pntt p17, p8, 9, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pntt p17, p7, 10, 0, 0
pfree p5
dload x10, x11, p6, 0, 1, 32
pntt p17, p6, 11, 0, 0
dload x10, x11, p5, 0, 0, 0
pmul p18, p18, p5
pfree p5
pmodld 1
dload x10, x11, p5, 0, 0, 0
pmul p5, p18, p5
pfree p3
dload x10, x11, p20, 0, 1, 32
pmul p5, p5, p20, 1
pfree p6
dload x10, x11, p3, 0, 1, 32
pntt p5, p3, 0, 0, 0
pfree p7
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 1, 0, 0
pfree p8
dload x10, x11, p7, 0, 1, 32
pntt p5, p7, 2, 0, 0
pfree p9
dload x10, x11, p8, 0, 1, 32
pntt p5, p8, 3, 0, 0
pfree p10
dload x10, x11, p9, 0, 1, 32
pntt p5, p9, 4, 0, 0
pfree p11
dload x10, x11, p10, 0, 1, 32
pntt p5, p10, 5, 0, 0
pfree p12
dload x10, x11, p11, 0, 1, 32
pntt p5, p11, 6, 0, 0
pfree p13
dload x10, x11, p12, 0, 1, 32
pntt p5, p12, 7, 0, 0
pfree p14
dload x10, x11, p13, 0, 1, 32
pntt p5, p13, 8, 0, 0
pfree p15
dload x10, x11, p14, 0, 1, 32
pntt p5, p14, 9, 0, 0
pfree p16
dload x10, x11, p15, 0, 1, 32
pntt p5, p15, 10, 0, 0
pfree p19
dload x10, x11, p16, 0, 1, 32
pntt p5, p16, 11, 0, 0
pmodld 2
dload x10, x11, p19, 0, 0, 0
pmul p18, p18, p19
pfree p19
pfree p1
dload x10, x11, p19, 0, 1, 32
pmul p18, p18, p19, 1
pfree p19
dload x10, x11, p1, 0, 1, 32
pntt p18, p1, 0, 0, 0
pfree p1
dload x10, x11, p19, 0, 1, 32
pntt p18, p19, 1, 0, 0
pfree p19
dload x10, x11, p1, 0, 1, 32
pntt p18, p1, 2, 0, 0
pfree p1
dload x10, x11, p19, 0, 1, 32
pntt p18, p19, 3, 0, 0
pfree p19
dload x10, x11, p1, 0, 1, 32
pntt p18, p1, 4, 0, 0
pfree p1
dload x10, x11, p19, 0, 1, 32
pntt p18, p19, 5, 0, 0
pfree p19
dload x10, x11, p1, 0, 1, 32
pntt p18, p1, 6, 0, 0
pfree p1
dload x10, x11, p19, 0, 1, 32
pntt p18, p19, 7, 0, 0
pfree p19
dload x10, x11, p1, 0, 1, 32
pntt p18, p1, 8, 0, 0
pfree p1
dload x10, x11, p19, 0, 1, 32
pntt p18, p19, 9, 0, 0
pfree p19
dload x10, x11, p1, 0, 1, 32
pntt p18, p1, 10, 0, 0
pfree p1
dload x10, x11, p19, 0, 1, 32
pntt p18, p19, 11, 0, 0
pmodld 0
dload x10, x11, p1, 0, 0, 0
pmul p1, p17, p1
dload x10, x11, p21, 0, 0, 0
pmul p17, p17, p21
pfree p21
pmodld 1
dload x10, x11, p21, 0, 0, 0
pmul p21, p5, p21
dload x10, x11, p22, 0, 0, 0
pmul p5, p5, p22
pfree p22
pmodld 2
dload x10, x11, p22, 0, 0, 0
pmul p22, p18, p22
dload x10, x11, p23, 0, 0, 0
pmul p18, p18, p23
pfree p23
pmodld 1
dload x10, x11, p23, 0, 0, 0
dload x10, x11, p24, 0, 0, 0
pmul p25, p23, p24
pfree p19
dload x10, x11, p26, 0, 1, 32
pintt p25, p26, 0, 0, 0
pfree p16
dload x10, x11, p19, 0, 1, 32
pintt p25, p19, 1, 0, 0
pfree p15
dload x10, x11, p16, 0, 1, 32
pintt p25, p16, 2, 0, 0
pfree p14
dload x10, x11, p15, 0, 1, 32
pintt p25, p15, 3, 0, 0
pfree p13
dload x10, x11, p14, 0, 1, 32
pintt p25, p14, 4, 0, 0
pfree p12
dload x10, x11, p13, 0, 1, 32
pintt p25, p13, 5, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pintt p25, p12, 6, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pintt p25, p11, 7, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pintt p25, p10, 8, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pintt p25, p9, 9, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pintt p25, p8, 10, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pintt p25, p7, 11, 0, 0
pfree p3
dload x10, x11, p6, 0, 1, 32
pmul p25, p25, p6, 1
dload x10, x11, p3, 0, 0, 0
pmul p23, p23, p3
dload x10, x11, p27, 0, 0, 0
pmac p23, p27, p24
pfree p24
pmul p27, p27, p3
pfree p3
pintt p23, p26, 0, 0, 0
pintt p23, p19, 1, 0, 0
pintt p23, p16, 2, 0, 0
pintt p23, p15, 3, 0, 0
pintt p23, p14, 4, 0, 0
pintt p23, p13, 5, 0, 0
pintt p23, p12, 6, 0, 0
pintt p23, p11, 7, 0, 0
pintt p23, p10, 8, 0, 0
pintt p23, p9, 9, 0, 0
pintt p23, p8, 10, 0, 0
pintt p23, p7, 11, 0, 0
pmul p23, p23, p6, 1
pintt p27, p26, 0, 0, 0
pintt p27, p19, 1, 0, 0
pintt p27, p16, 2, 0, 0
pintt p27, p15, 3, 0, 0
pintt p27, p14, 4, 0, 0
pintt p27, p13, 5, 0, 0
pintt p27, p12, 6, 0, 0
pintt p27, p11, 7, 0, 0
pintt p27, p10, 8, 0, 0
pintt p27, p9, 9, 0, 0
pintt p27, p8, 10, 0, 0
pintt p27, p7, 11, 0, 0
pmul p27, p27, p6, 1
pmul p3, p27, p20, 1
pfree p20
dload x10, x11, p24, 0, 1, 32
pntt p3, p24, 0, 0, 0
pfree p24
dload x10, x11, p20, 0, 1, 32
pntt p3, p20, 1, 0, 0
pfree p20
dload x10, x11, p24, 0, 1, 32
pntt p3, p24, 2, 0, 0
pfree p24
dload x10, x11, p20, 0, 1, 32
pntt p3, p20, 3, 0, 0
pfree p20
dload x10, x11, p24, 0, 1, 32
pntt p3, p24, 4, 0, 0
pfree p24
dload x10, x11, p20, 0, 1, 32
pntt p3, p20, 5, 0, 0
pfree p20
dload x10, x11, p24, 0, 1, 32
pntt p3, p24, 6, 0, 0
pfree p24
dload x10, x11, p20, 0, 1, 32
pntt p3, p20, 7, 0, 0
pfree p20
dload x10, x11, p24, 0, 1, 32
pntt p3, p24, 8, 0, 0
pfree p24
dload x10, x11, p20, 0, 1, 32
pntt p3, p20, 9, 0, 0
pfree p20
dload x10, x11, p24, 0, 1, 32
pntt p3, p24, 10, 0, 0
pfree p24
dload x10, x11, p20, 0, 1, 32
pntt p3, p20, 11, 0, 0
dload x10, x11, p24, 0, 0, 0
pmul p27, p27, p24
pfree p24
dload x10, x11, p24, 0, 0, 0
pmac p21, p3, p24
pfree p24
pintt p21, p26, 0, 0, 0
pintt p21, p19, 1, 0, 0
pintt p21, p16, 2, 0, 0
pintt p21, p15, 3, 0, 0
pintt p21, p14, 4, 0, 0
pintt p21, p13, 5, 0, 0
pintt p21, p12, 6, 0, 0
pintt p21, p11, 7, 0, 0
pintt p21, p10, 8, 0, 0
pintt p21, p9, 9, 0, 0
pintt p21, p8, 10, 0, 0
pintt p21, p7, 11, 0, 0
pmul p21, p21, p6, 1
dload x10, x11, p24, 0, 0, 0
pmac p5, p3, p24
pfree p3
pfree p24
pintt p5, p26, 0, 0, 0
pfree p26
pintt p5, p19, 1, 0, 0
pfree p19
pintt p5, p16, 2, 0, 0
pfree p16
pintt p5, p15, 3, 0, 0
pfree p15
pintt p5, p14, 4, 0, 0
pfree p14
pintt p5, p13, 5, 0, 0
pfree p13
pintt p5, p12, 6, 0, 0
pfree p12
pintt p5, p11, 7, 0, 0
pfree p11
pintt p5, p10, 8, 0, 0
pfree p10
pintt p5, p9, 9, 0, 0
pfree p9
pintt p5, p8, 10, 0, 0
pfree p8
pintt p5, p7, 11, 0, 0
pfree p7
pmul p5, p5, p6, 1
pfree p6
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p3, p27, p3
dload x10, x11, p6, 0, 1, 32
pmul p3, p3, p6, 1
dload x10, x11, p7, 0, 1, 32
pntt p3, p7, 0, 0, 0
dload x10, x11, p8, 0, 1, 32
pntt p3, p8, 1, 0, 0
dload x10, x11, p9, 0, 1, 32
pntt p3, p9, 2, 0, 0
dload x10, x11, p10, 0, 1, 32
pntt p3, p10, 3, 0, 0
dload x10, x11, p11, 0, 1, 32
pntt p3, p11, 4, 0, 0
dload x10, x11, p12, 0, 1, 32
pntt p3, p12, 5, 0, 0
dload x10, x11, p13, 0, 1, 32
pntt p3, p13, 6, 0, 0
dload x10, x11, p14, 0, 1, 32
pntt p3, p14, 7, 0, 0
dload x10, x11, p15, 0, 1, 32
pntt p3, p15, 8, 0, 0
dload x10, x11, p16, 0, 1, 32
pntt p3, p16, 9, 0, 0
dload x10, x11, p19, 0, 1, 32
pntt p3, p19, 10, 0, 0
dload x10, x11, p24, 0, 1, 32
pntt p3, p24, 11, 0, 0
pmodld 2
dload x10, x11, p26, 0, 0, 0
pmul p27, p27, p26
pfree p26
pfree p20
dload x10, x11, p26, 0, 1, 32
pmul p27, p27, p26, 1
pfree p26
dload x10, x11, p20, 0, 1, 32
pntt p27, p20, 0, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p27, p20, 1, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p27, p20, 2, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p27, p20, 3, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p27, p20, 4, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p27, p20, 5, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p27, p20, 6, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p27, p20, 7, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p27, p20, 8, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p27, p20, 9, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p27, p20, 10, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p27, p20, 11, 0, 0
pfree p20
pmodld 0
dload x10, x11, p20, 0, 0, 0
pmac p1, p3, p20
pfree p20
dload x10, x11, p20, 0, 1, 32
pintt p1, p20, 0, 0, 0
pfree p24
dload x10, x11, p26, 0, 1, 32
pintt p1, p26, 1, 0, 0
pfree p19
dload x10, x11, p24, 0, 1, 32
pintt p1, p24, 2, 0, 0
pfree p16
dload x10, x11, p19, 0, 1, 32
pintt p1, p19, 3, 0, 0
pfree p15
dload x10, x11, p16, 0, 1, 32
pintt p1, p16, 4, 0, 0
pfree p14
dload x10, x11, p15, 0, 1, 32
pintt p1, p15, 5, 0, 0
pfree p13
dload x10, x11, p14, 0, 1, 32
pintt p1, p14, 6, 0, 0
pfree p12
dload x10, x11, p13, 0, 1, 32
pintt p1, p13, 7, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pintt p1, p12, 8, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pintt p1, p11, 9, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pintt p1, p10, 10, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pintt p1, p9, 11, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pmul p1, p1, p8, 1
dload x10, x11, p7, 0, 0, 0
pmac p17, p3, p7
pfree p3
pfree p7
pintt p17, p20, 0, 0, 0
pfree p20
pintt p17, p26, 1, 0, 0
pfree p26
pintt p17, p24, 2, 0, 0
pfree p24
pintt p17, p19, 3, 0, 0
pfree p19
pintt p17, p16, 4, 0, 0
pfree p16
pintt p17, p15, 5, 0, 0
pfree p15
pintt p17, p14, 6, 0, 0
pfree p14
pintt p17, p13, 7, 0, 0
pfree p13
pintt p17, p12, 8, 0, 0
pfree p12
pintt p17, p11, 9, 0, 0
pfree p11
pintt p17, p10, 10, 0, 0
pfree p10
pintt p17, p9, 11, 0, 0
pfree p9
pmul p17, p17, p8, 1
pfree p8
pmodld 2
dload x10, x11, p3, 0, 0, 0
pmac p22, p27, p3
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p22, p3, 0, 0, 0
dload x10, x11, p7, 0, 1, 32
pintt p22, p7, 1, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p22, p8, 2, 0, 0
dload x10, x11, p9, 0, 1, 32
pintt p22, p9, 3, 0, 0
dload x10, x11, p10, 0, 1, 32
pintt p22, p10, 4, 0, 0
dload x10, x11, p11, 0, 1, 32
pintt p22, p11, 5, 0, 0
dload x10, x11, p12, 0, 1, 32
pintt p22, p12, 6, 0, 0
dload x10, x11, p13, 0, 1, 32
pintt p22, p13, 7, 0, 0
dload x10, x11, p14, 0, 1, 32
pintt p22, p14, 8, 0, 0
dload x10, x11, p15, 0, 1, 32
pintt p22, p15, 9, 0, 0
dload x10, x11, p16, 0, 1, 32
pintt p22, p16, 10, 0, 0
dload x10, x11, p19, 0, 1, 32
pintt p22, p19, 11, 0, 0
dload x10, x11, p20, 0, 1, 32
pmul p22, p22, p20, 1
dload x10, x11, p24, 0, 0, 0
pmac p18, p27, p24
pfree p27
pfree p24
pintt p18, p3, 0, 0, 0
pfree p3
pintt p18, p7, 1, 0, 0
pfree p7
pintt p18, p8, 2, 0, 0
pfree p8
pintt p18, p9, 3, 0, 0
pfree p9
pintt p18, p10, 4, 0, 0
pfree p10
pintt p18, p11, 5, 0, 0
pfree p11
pintt p18, p12, 6, 0, 0
pfree p12
pintt p18, p13, 7, 0, 0
pfree p13
pintt p18, p14, 8, 0, 0
pfree p14
pintt p18, p15, 9, 0, 0
pfree p15
pintt p18, p16, 10, 0, 0
pfree p16
pintt p18, p19, 11, 0, 0
pfree p19
pmul p18, p18, p20, 1
pfree p20
pmodld 0
dload x10, x11, p3, 0, 0, 0
padd p1, p1, p3
padd p17, p17, p3
pfree p3
pmodld 1
dload x10, x11, p3, 0, 0, 0
padd p21, p21, p3
padd p5, p5, p3
pfree p3
pmodld 2
dload x10, x11, p3, 0, 0, 0
padd p22, p22, p3
padd p18, p18, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
pmul p22, p22, p3
pmul p18, p18, p3
pfree p3
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p7, p22, p3
psub p1, p1, p7
pfree p7
pmul p3, p18, p3
psub p17, p17, p3
pfree p3
pmodld 1
dload x10, x11, p3, 0, 0, 0
pmul p22, p22, p3
psub p21, p21, p22
pfree p22
pmul p18, p18, p3
pfree p3
psub p5, p5, p18
pfree p18
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p1, p1, p3
pmul p17, p17, p3
pfree p3
padd p1, p1, p2
pfree p2
padd p0, p0, p17
pfree p17
pmul p1, p1, p6, 1
pmul p0, p0, p6, 1
pfree p6
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 0, 0, 0
pntt p0, p2, 0, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 1, 0, 0
pntt p0, p2, 1, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 2, 0, 0
pntt p0, p2, 2, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 3, 0, 0
pntt p0, p2, 3, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 4, 0, 0
pntt p0, p2, 4, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 5, 0, 0
pntt p0, p2, 5, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 6, 0, 0
pntt p0, p2, 6, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 7, 0, 0
pntt p0, p2, 7, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 8, 0, 0
pntt p0, p2, 8, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 9, 0, 0
pntt p0, p2, 9, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 10, 0, 0
pntt p0, p2, 10, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 11, 0, 0
dstore x10, x11, p1, 1, 0
pntt p0, p2, 11, 0, 0
pfree p2
dstore x10, x11, p0, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p21, p21, p0
pmul p5, p5, p0
pfree p0
padd p21, p21, p25
pfree p25
padd p23, p23, p5
pfree p5
dload x10, x11, p0, 0, 1, 32
pmul p21, p21, p0, 1
pmul p23, p23, p0, 1
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 0, 0, 0
pntt p23, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 1, 0, 0
pntt p23, p0, 1, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 2, 0, 0
pntt p23, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 3, 0, 0
pntt p23, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 4, 0, 0
pntt p23, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 5, 0, 0
pntt p23, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 6, 0, 0
pntt p23, p0, 6, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 7, 0, 0
pntt p23, p0, 7, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 8, 0, 0
pntt p23, p0, 8, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 9, 0, 0
pntt p23, p0, 9, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 10, 0, 0
pntt p23, p0, 10, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 11, 0, 0
dstore x10, x11, p21, 1, 0
pntt p23, p0, 11, 0, 0
pfree p0
dstore x10, x11, p23, 1, 0
psync
