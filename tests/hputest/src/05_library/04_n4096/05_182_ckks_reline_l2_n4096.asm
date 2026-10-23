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
pintt p15, p2, 1, 0, 0
pintt p15, p3, 2, 0, 0
pintt p15, p5, 3, 0, 0
pintt p15, p6, 4, 0, 0
pintt p15, p7, 5, 0, 0
pintt p15, p8, 6, 0, 0
pintt p15, p9, 7, 0, 0
pintt p15, p10, 8, 0, 0
pintt p15, p11, 9, 0, 0
pintt p15, p12, 10, 0, 0
pintt p15, p13, 11, 0, 0
pmul p15, p15, p14, 1
dload x10, x11, p16, 0, 0, 0
pintt p16, p1, 0, 0, 0
pintt p16, p2, 1, 0, 0
pintt p16, p3, 2, 0, 0
pintt p16, p5, 3, 0, 0
pintt p16, p6, 4, 0, 0
pintt p16, p7, 5, 0, 0
pintt p16, p8, 6, 0, 0
pintt p16, p9, 7, 0, 0
pintt p16, p10, 8, 0, 0
pintt p16, p11, 9, 0, 0
pintt p16, p12, 10, 0, 0
pintt p16, p13, 11, 0, 0
pmul p16, p16, p14, 1
dload x10, x11, p17, 0, 1, 32
pmul p18, p16, p17, 1
pfree p14
dload x10, x11, p19, 0, 1, 32
pntt p18, p19, 0, 0, 0
pfree p13
dload x10, x11, p14, 0, 1, 32
pntt p18, p14, 1, 0, 0
pfree p12
dload x10, x11, p13, 0, 1, 32
pntt p18, p13, 2, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pntt p18, p12, 3, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pntt p18, p11, 4, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pntt p18, p10, 5, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pntt p18, p9, 6, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pntt p18, p8, 7, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pntt p18, p7, 8, 0, 0
pfree p5
dload x10, x11, p6, 0, 1, 32
pntt p18, p6, 9, 0, 0
pfree p3
dload x10, x11, p5, 0, 1, 32
pntt p18, p5, 10, 0, 0
pfree p2
dload x10, x11, p3, 0, 1, 32
pntt p18, p3, 11, 0, 0
dload x10, x11, p2, 0, 0, 0
pmul p16, p16, p2
pfree p2
pmodld 1
dload x10, x11, p2, 0, 0, 0
pmul p2, p16, p2
pfree p1
dload x10, x11, p20, 0, 1, 32
pmul p2, p2, p20, 1
pfree p3
dload x10, x11, p1, 0, 1, 32
pntt p2, p1, 0, 0, 0
pfree p5
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 1, 0, 0
pfree p6
dload x10, x11, p5, 0, 1, 32
pntt p2, p5, 2, 0, 0
pfree p7
dload x10, x11, p6, 0, 1, 32
pntt p2, p6, 3, 0, 0
pfree p8
dload x10, x11, p7, 0, 1, 32
pntt p2, p7, 4, 0, 0
pfree p9
dload x10, x11, p8, 0, 1, 32
pntt p2, p8, 5, 0, 0
pfree p10
dload x10, x11, p9, 0, 1, 32
pntt p2, p9, 6, 0, 0
pfree p11
dload x10, x11, p10, 0, 1, 32
pntt p2, p10, 7, 0, 0
pfree p12
dload x10, x11, p11, 0, 1, 32
pntt p2, p11, 8, 0, 0
pfree p13
dload x10, x11, p12, 0, 1, 32
pntt p2, p12, 9, 0, 0
pfree p14
dload x10, x11, p13, 0, 1, 32
pntt p2, p13, 10, 0, 0
pfree p19
dload x10, x11, p14, 0, 1, 32
pntt p2, p14, 11, 0, 0
pmodld 2
dload x10, x11, p19, 0, 0, 0
pmul p16, p16, p19
pfree p19
pfree p17
dload x10, x11, p19, 0, 1, 32
pmul p16, p16, p19, 1
pfree p19
dload x10, x11, p17, 0, 1, 32
pntt p16, p17, 0, 0, 0
pfree p17
dload x10, x11, p19, 0, 1, 32
pntt p16, p19, 1, 0, 0
pfree p19
dload x10, x11, p17, 0, 1, 32
pntt p16, p17, 2, 0, 0
pfree p17
dload x10, x11, p19, 0, 1, 32
pntt p16, p19, 3, 0, 0
pfree p19
dload x10, x11, p17, 0, 1, 32
pntt p16, p17, 4, 0, 0
pfree p17
dload x10, x11, p19, 0, 1, 32
pntt p16, p19, 5, 0, 0
pfree p19
dload x10, x11, p17, 0, 1, 32
pntt p16, p17, 6, 0, 0
pfree p17
dload x10, x11, p19, 0, 1, 32
pntt p16, p19, 7, 0, 0
pfree p19
dload x10, x11, p17, 0, 1, 32
pntt p16, p17, 8, 0, 0
pfree p17
dload x10, x11, p19, 0, 1, 32
pntt p16, p19, 9, 0, 0
pfree p19
dload x10, x11, p17, 0, 1, 32
pntt p16, p17, 10, 0, 0
pfree p17
dload x10, x11, p19, 0, 1, 32
pntt p16, p19, 11, 0, 0
pmodld 0
dload x10, x11, p17, 0, 0, 0
pmul p17, p18, p17
dload x10, x11, p21, 0, 0, 0
pmul p18, p18, p21
pfree p21
pmodld 1
dload x10, x11, p21, 0, 0, 0
pmul p21, p2, p21
dload x10, x11, p22, 0, 0, 0
pmul p2, p2, p22
pfree p22
pmodld 2
dload x10, x11, p22, 0, 0, 0
pmul p22, p16, p22
dload x10, x11, p23, 0, 0, 0
pmul p16, p16, p23
pfree p23
pmodld 1
dload x10, x11, p23, 0, 0, 0
pfree p19
dload x10, x11, p24, 0, 1, 32
pintt p23, p24, 0, 0, 0
pfree p14
dload x10, x11, p19, 0, 1, 32
pintt p23, p19, 1, 0, 0
pfree p13
dload x10, x11, p14, 0, 1, 32
pintt p23, p14, 2, 0, 0
pfree p12
dload x10, x11, p13, 0, 1, 32
pintt p23, p13, 3, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pintt p23, p12, 4, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pintt p23, p11, 5, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pintt p23, p10, 6, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pintt p23, p9, 7, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pintt p23, p8, 8, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pintt p23, p7, 9, 0, 0
pfree p5
dload x10, x11, p6, 0, 1, 32
pintt p23, p6, 10, 0, 0
pfree p3
dload x10, x11, p5, 0, 1, 32
pintt p23, p5, 11, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pmul p23, p23, p3, 1
dload x10, x11, p1, 0, 0, 0
pintt p1, p24, 0, 0, 0
pintt p1, p19, 1, 0, 0
pintt p1, p14, 2, 0, 0
pintt p1, p13, 3, 0, 0
pintt p1, p12, 4, 0, 0
pintt p1, p11, 5, 0, 0
pintt p1, p10, 6, 0, 0
pintt p1, p9, 7, 0, 0
pintt p1, p8, 8, 0, 0
pintt p1, p7, 9, 0, 0
pintt p1, p6, 10, 0, 0
pintt p1, p5, 11, 0, 0
pmul p1, p1, p3, 1
dload x10, x11, p25, 0, 0, 0
pintt p25, p24, 0, 0, 0
pintt p25, p19, 1, 0, 0
pintt p25, p14, 2, 0, 0
pintt p25, p13, 3, 0, 0
pintt p25, p12, 4, 0, 0
pintt p25, p11, 5, 0, 0
pintt p25, p10, 6, 0, 0
pintt p25, p9, 7, 0, 0
pintt p25, p8, 8, 0, 0
pintt p25, p7, 9, 0, 0
pintt p25, p6, 10, 0, 0
pintt p25, p5, 11, 0, 0
pmul p25, p25, p3, 1
pmul p26, p25, p20, 1
pfree p20
dload x10, x11, p27, 0, 1, 32
pntt p26, p27, 0, 0, 0
pfree p27
dload x10, x11, p20, 0, 1, 32
pntt p26, p20, 1, 0, 0
pfree p20
dload x10, x11, p27, 0, 1, 32
pntt p26, p27, 2, 0, 0
pfree p27
dload x10, x11, p20, 0, 1, 32
pntt p26, p20, 3, 0, 0
pfree p20
dload x10, x11, p27, 0, 1, 32
pntt p26, p27, 4, 0, 0
pfree p27
dload x10, x11, p20, 0, 1, 32
pntt p26, p20, 5, 0, 0
pfree p20
dload x10, x11, p27, 0, 1, 32
pntt p26, p27, 6, 0, 0
pfree p27
dload x10, x11, p20, 0, 1, 32
pntt p26, p20, 7, 0, 0
pfree p20
dload x10, x11, p27, 0, 1, 32
pntt p26, p27, 8, 0, 0
pfree p27
dload x10, x11, p20, 0, 1, 32
pntt p26, p20, 9, 0, 0
pfree p20
dload x10, x11, p27, 0, 1, 32
pntt p26, p27, 10, 0, 0
pfree p27
dload x10, x11, p20, 0, 1, 32
pntt p26, p20, 11, 0, 0
dload x10, x11, p27, 0, 0, 0
pmul p25, p25, p27
pfree p27
dload x10, x11, p27, 0, 0, 0
pmac p21, p26, p27
pfree p27
pintt p21, p24, 0, 0, 0
pintt p21, p19, 1, 0, 0
pintt p21, p14, 2, 0, 0
pintt p21, p13, 3, 0, 0
pintt p21, p12, 4, 0, 0
pintt p21, p11, 5, 0, 0
pintt p21, p10, 6, 0, 0
pintt p21, p9, 7, 0, 0
pintt p21, p8, 8, 0, 0
pintt p21, p7, 9, 0, 0
pintt p21, p6, 10, 0, 0
pintt p21, p5, 11, 0, 0
pmul p21, p21, p3, 1
dload x10, x11, p27, 0, 0, 0
pmac p2, p26, p27
pfree p26
pfree p27
pintt p2, p24, 0, 0, 0
pfree p24
pintt p2, p19, 1, 0, 0
pfree p19
pintt p2, p14, 2, 0, 0
pfree p14
pintt p2, p13, 3, 0, 0
pfree p13
pintt p2, p12, 4, 0, 0
pfree p12
pintt p2, p11, 5, 0, 0
pfree p11
pintt p2, p10, 6, 0, 0
pfree p10
pintt p2, p9, 7, 0, 0
pfree p9
pintt p2, p8, 8, 0, 0
pfree p8
pintt p2, p7, 9, 0, 0
pfree p7
pintt p2, p6, 10, 0, 0
pfree p6
pintt p2, p5, 11, 0, 0
pfree p5
pmul p2, p2, p3, 1
pfree p3
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p3, p25, p3
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
dload x10, x11, p19, 0, 1, 32
pntt p3, p19, 9, 0, 0
dload x10, x11, p24, 0, 1, 32
pntt p3, p24, 10, 0, 0
dload x10, x11, p26, 0, 1, 32
pntt p3, p26, 11, 0, 0
pmodld 2
dload x10, x11, p27, 0, 0, 0
pmul p25, p25, p27
pfree p27
pfree p20
dload x10, x11, p27, 0, 1, 32
pmul p25, p25, p27, 1
pfree p27
dload x10, x11, p20, 0, 1, 32
pntt p25, p20, 0, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p25, p20, 1, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p25, p20, 2, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p25, p20, 3, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p25, p20, 4, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p25, p20, 5, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p25, p20, 6, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p25, p20, 7, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p25, p20, 8, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p25, p20, 9, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p25, p20, 10, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pntt p25, p20, 11, 0, 0
pfree p20
pmodld 0
dload x10, x11, p20, 0, 0, 0
pmac p17, p3, p20
pfree p20
dload x10, x11, p20, 0, 1, 32
pintt p17, p20, 0, 0, 0
pfree p26
dload x10, x11, p27, 0, 1, 32
pintt p17, p27, 1, 0, 0
pfree p24
dload x10, x11, p26, 0, 1, 32
pintt p17, p26, 2, 0, 0
pfree p19
dload x10, x11, p24, 0, 1, 32
pintt p17, p24, 3, 0, 0
pfree p14
dload x10, x11, p19, 0, 1, 32
pintt p17, p19, 4, 0, 0
pfree p13
dload x10, x11, p14, 0, 1, 32
pintt p17, p14, 5, 0, 0
pfree p12
dload x10, x11, p13, 0, 1, 32
pintt p17, p13, 6, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pintt p17, p12, 7, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pintt p17, p11, 8, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pintt p17, p10, 9, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pintt p17, p9, 10, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pintt p17, p8, 11, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pmul p17, p17, p7, 1
dload x10, x11, p6, 0, 0, 0
pmac p18, p3, p6
pfree p3
pfree p6
pintt p18, p20, 0, 0, 0
pfree p20
pintt p18, p27, 1, 0, 0
pfree p27
pintt p18, p26, 2, 0, 0
pfree p26
pintt p18, p24, 3, 0, 0
pfree p24
pintt p18, p19, 4, 0, 0
pfree p19
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
pmul p18, p18, p7, 1
pfree p7
pmodld 2
dload x10, x11, p3, 0, 0, 0
pmac p22, p25, p3
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p22, p3, 0, 0, 0
dload x10, x11, p6, 0, 1, 32
pintt p22, p6, 1, 0, 0
dload x10, x11, p7, 0, 1, 32
pintt p22, p7, 2, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p22, p8, 3, 0, 0
dload x10, x11, p9, 0, 1, 32
pintt p22, p9, 4, 0, 0
dload x10, x11, p10, 0, 1, 32
pintt p22, p10, 5, 0, 0
dload x10, x11, p11, 0, 1, 32
pintt p22, p11, 6, 0, 0
dload x10, x11, p12, 0, 1, 32
pintt p22, p12, 7, 0, 0
dload x10, x11, p13, 0, 1, 32
pintt p22, p13, 8, 0, 0
dload x10, x11, p14, 0, 1, 32
pintt p22, p14, 9, 0, 0
dload x10, x11, p19, 0, 1, 32
pintt p22, p19, 10, 0, 0
dload x10, x11, p20, 0, 1, 32
pintt p22, p20, 11, 0, 0
dload x10, x11, p24, 0, 1, 32
pmul p22, p22, p24, 1
dload x10, x11, p26, 0, 0, 0
pmac p16, p25, p26
pfree p25
pfree p26
pintt p16, p3, 0, 0, 0
pfree p3
pintt p16, p6, 1, 0, 0
pfree p6
pintt p16, p7, 2, 0, 0
pfree p7
pintt p16, p8, 3, 0, 0
pfree p8
pintt p16, p9, 4, 0, 0
pfree p9
pintt p16, p10, 5, 0, 0
pfree p10
pintt p16, p11, 6, 0, 0
pfree p11
pintt p16, p12, 7, 0, 0
pfree p12
pintt p16, p13, 8, 0, 0
pfree p13
pintt p16, p14, 9, 0, 0
pfree p14
pintt p16, p19, 10, 0, 0
pfree p19
pintt p16, p20, 11, 0, 0
pfree p20
pmul p16, p16, p24, 1
pfree p24
pmodld 0
dload x10, x11, p3, 0, 0, 0
padd p17, p17, p3
padd p18, p18, p3
pfree p3
pmodld 1
dload x10, x11, p3, 0, 0, 0
padd p21, p21, p3
padd p2, p2, p3
pfree p3
pmodld 2
dload x10, x11, p3, 0, 0, 0
padd p22, p22, p3
padd p16, p16, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
pmul p22, p22, p3
pmul p16, p16, p3
pfree p3
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p6, p22, p3
psub p17, p17, p6
pfree p6
pmul p3, p16, p3
psub p18, p18, p3
pfree p3
pmodld 1
dload x10, x11, p3, 0, 0, 0
pmul p22, p22, p3
psub p21, p21, p22
pfree p22
pmul p16, p16, p3
pfree p3
psub p2, p2, p16
pfree p16
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p17, p17, p3
pmul p18, p18, p3
pfree p3
padd p17, p17, p0
pfree p0
padd p15, p15, p18
pfree p18
pmul p17, p17, p5, 1
pmul p15, p15, p5, 1
pfree p5
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 0, 0, 0
pntt p15, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 1, 0, 0
pntt p15, p0, 1, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 2, 0, 0
pntt p15, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 3, 0, 0
pntt p15, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 4, 0, 0
pntt p15, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 5, 0, 0
pntt p15, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 6, 0, 0
pntt p15, p0, 6, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 7, 0, 0
pntt p15, p0, 7, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 8, 0, 0
pntt p15, p0, 8, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 9, 0, 0
pntt p15, p0, 9, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 10, 0, 0
pntt p15, p0, 10, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 11, 0, 0
dstore x10, x11, p17, 1, 0
pntt p15, p0, 11, 0, 0
pfree p0
dstore x10, x11, p15, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p21, p21, p0
pmul p2, p2, p0
pfree p0
padd p21, p21, p23
pfree p23
padd p1, p1, p2
pfree p2
dload x10, x11, p0, 0, 1, 32
pmul p21, p21, p0, 1
pmul p1, p1, p0, 1
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 0, 0, 0
pntt p1, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 1, 0, 0
pntt p1, p0, 1, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 2, 0, 0
pntt p1, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 3, 0, 0
pntt p1, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 4, 0, 0
pntt p1, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 5, 0, 0
pntt p1, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 6, 0, 0
pntt p1, p0, 6, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 7, 0, 0
pntt p1, p0, 7, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 8, 0, 0
pntt p1, p0, 8, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 9, 0, 0
pntt p1, p0, 9, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 10, 0, 0
pntt p1, p0, 10, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 11, 0, 0
dstore x10, x11, p21, 1, 0
pntt p1, p0, 11, 0, 0
pfree p0
dstore x10, x11, p1, 1, 0
psync
