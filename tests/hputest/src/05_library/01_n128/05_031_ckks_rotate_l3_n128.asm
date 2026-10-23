dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 0, 0, 0
dload x10, x11, p2, 0, 0, 0
pintt p2, p1, 0, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 1, 0, 0
pintt p2, p1, 1, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 2, 0, 0
pintt p2, p1, 2, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 3, 0, 0
pintt p2, p1, 3, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 4, 0, 0
pintt p2, p1, 4, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 5, 0, 0
pintt p2, p1, 5, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 6, 0, 0
pintt p2, p1, 6, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pmul p0, p0, p1, 1
pmul p2, p2, p1, 1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmul p1, p2, p1
pmodld 1
dload x10, x11, p3, 0, 0, 0
pmul p3, p1, p3
pmodld 2
dload x10, x11, p5, 0, 0, 0
pmul p5, p1, p5
pmodld 3
dload x10, x11, p6, 0, 0, 0
pmul p1, p1, p6
pfree p6
pmodld 0
dload x10, x11, p6, 0, 1, 32
pmul p2, p2, p6, 1
dload x10, x11, p7, 0, 1, 32
pntt p2, p7, 0, 0, 0
dload x10, x11, p8, 0, 1, 32
pntt p2, p8, 1, 0, 0
dload x10, x11, p9, 0, 1, 32
pntt p2, p9, 2, 0, 0
dload x10, x11, p10, 0, 1, 32
pntt p2, p10, 3, 0, 0
dload x10, x11, p11, 0, 1, 32
pntt p2, p11, 4, 0, 0
dload x10, x11, p12, 0, 1, 32
pntt p2, p12, 5, 0, 0
dload x10, x11, p13, 0, 1, 32
pntt p2, p13, 6, 0, 0
pmodld 1
dload x10, x11, p14, 0, 1, 32
pmul p3, p3, p14, 1
dload x10, x11, p15, 0, 1, 32
pntt p3, p15, 0, 0, 0
dload x10, x11, p16, 0, 1, 32
pntt p3, p16, 1, 0, 0
dload x10, x11, p17, 0, 1, 32
pntt p3, p17, 2, 0, 0
dload x10, x11, p18, 0, 1, 32
pntt p3, p18, 3, 0, 0
dload x10, x11, p19, 0, 1, 32
pntt p3, p19, 4, 0, 0
pfree p13
dload x10, x11, p20, 0, 1, 32
pntt p3, p20, 5, 0, 0
pfree p12
dload x10, x11, p13, 0, 1, 32
pntt p3, p13, 6, 0, 0
pmodld 2
pfree p11
dload x10, x11, p12, 0, 1, 32
pmul p5, p5, p12, 1
pfree p12
dload x10, x11, p11, 0, 1, 32
pntt p5, p11, 0, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pntt p5, p12, 1, 0, 0
pfree p12
dload x10, x11, p11, 0, 1, 32
pntt p5, p11, 2, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pntt p5, p12, 3, 0, 0
pfree p12
dload x10, x11, p11, 0, 1, 32
pntt p5, p11, 4, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pntt p5, p12, 5, 0, 0
pfree p12
dload x10, x11, p11, 0, 1, 32
pntt p5, p11, 6, 0, 0
pmodld 3
pfree p11
dload x10, x11, p12, 0, 1, 32
pmul p1, p1, p12, 1
pfree p12
dload x10, x11, p11, 0, 1, 32
pntt p1, p11, 0, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pntt p1, p12, 1, 0, 0
pfree p12
dload x10, x11, p11, 0, 1, 32
pntt p1, p11, 2, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pntt p1, p12, 3, 0, 0
pfree p12
dload x10, x11, p11, 0, 1, 32
pntt p1, p11, 4, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pntt p1, p12, 5, 0, 0
pfree p12
dload x10, x11, p11, 0, 1, 32
pntt p1, p11, 6, 0, 0
pmodld 0
dload x10, x11, p12, 0, 0, 0
pmul p12, p2, p12
dload x10, x11, p21, 0, 0, 0
pmul p2, p2, p21
pfree p21
pmodld 1
dload x10, x11, p21, 0, 0, 0
pmul p21, p3, p21
dload x10, x11, p22, 0, 0, 0
pmul p3, p3, p22
pfree p22
pmodld 2
dload x10, x11, p22, 0, 0, 0
pmul p22, p5, p22
dload x10, x11, p23, 0, 0, 0
pmul p5, p5, p23
pfree p23
pmodld 3
dload x10, x11, p23, 0, 0, 0
pmul p23, p1, p23
dload x10, x11, p24, 0, 0, 0
pmul p1, p1, p24
pfree p24
pmodld 1
dload x10, x11, p24, 0, 0, 0
pfree p11
dload x10, x11, p25, 0, 1, 32
pintt p24, p25, 0, 0, 0
dload x10, x11, p11, 0, 0, 0
pintt p11, p25, 0, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p24, p25, 1, 0, 0
pintt p11, p25, 1, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p24, p25, 2, 0, 0
pintt p11, p25, 2, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p24, p25, 3, 0, 0
pintt p11, p25, 3, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p24, p25, 4, 0, 0
pintt p11, p25, 4, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p24, p25, 5, 0, 0
pintt p11, p25, 5, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p24, p25, 6, 0, 0
pintt p11, p25, 6, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pmul p24, p24, p25, 1
pmul p11, p11, p25, 1
pfree p25
pmul p25, p11, p14, 1
pntt p25, p15, 0, 0, 0
pntt p25, p16, 1, 0, 0
pntt p25, p17, 2, 0, 0
pntt p25, p18, 3, 0, 0
pntt p25, p19, 4, 0, 0
pntt p25, p20, 5, 0, 0
pntt p25, p13, 6, 0, 0
dload x10, x11, p26, 0, 0, 0
pmul p11, p11, p26
pfree p26
dload x10, x11, p26, 0, 0, 0
pmac p21, p25, p26
pfree p26
dload x10, x11, p26, 0, 0, 0
pmac p3, p25, p26
pfree p25
pfree p26
pmodld 0
dload x10, x11, p25, 0, 0, 0
pmul p25, p11, p25
pmul p25, p25, p6, 1
pntt p25, p7, 0, 0, 0
pntt p25, p8, 1, 0, 0
pntt p25, p9, 2, 0, 0
pntt p25, p10, 3, 0, 0
dload x10, x11, p26, 0, 1, 32
pntt p25, p26, 4, 0, 0
pfree p13
dload x10, x11, p27, 0, 1, 32
pntt p25, p27, 5, 0, 0
pfree p20
dload x10, x11, p13, 0, 1, 32
pntt p25, p13, 6, 0, 0
dload x10, x11, p20, 0, 0, 0
pmac p12, p25, p20
pfree p20
dload x10, x11, p20, 0, 0, 0
pmac p2, p25, p20
pfree p25
pfree p20
pmodld 2
dload x10, x11, p20, 0, 0, 0
pmul p20, p11, p20
pfree p19
dload x10, x11, p25, 0, 1, 32
pmul p20, p20, p25, 1
pfree p18
dload x10, x11, p19, 0, 1, 32
pntt p20, p19, 0, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p20, p18, 1, 0, 0
pfree p16
dload x10, x11, p17, 0, 1, 32
pntt p20, p17, 2, 0, 0
pfree p15
dload x10, x11, p16, 0, 1, 32
pntt p20, p16, 3, 0, 0
pfree p14
dload x10, x11, p15, 0, 1, 32
pntt p20, p15, 4, 0, 0
pfree p13
dload x10, x11, p14, 0, 1, 32
pntt p20, p14, 5, 0, 0
pfree p27
dload x10, x11, p13, 0, 1, 32
pntt p20, p13, 6, 0, 0
pmodld 3
dload x10, x11, p27, 0, 0, 0
pmul p11, p11, p27
pfree p27
pfree p26
dload x10, x11, p27, 0, 1, 32
pmul p11, p11, p27, 1
pfree p27
dload x10, x11, p26, 0, 1, 32
pntt p11, p26, 0, 0, 0
pfree p26
dload x10, x11, p27, 0, 1, 32
pntt p11, p27, 1, 0, 0
pfree p27
dload x10, x11, p26, 0, 1, 32
pntt p11, p26, 2, 0, 0
pfree p26
dload x10, x11, p27, 0, 1, 32
pntt p11, p27, 3, 0, 0
pfree p27
dload x10, x11, p26, 0, 1, 32
pntt p11, p26, 4, 0, 0
pfree p26
dload x10, x11, p27, 0, 1, 32
pntt p11, p27, 5, 0, 0
pfree p27
dload x10, x11, p26, 0, 1, 32
pntt p11, p26, 6, 0, 0
pmodld 2
dload x10, x11, p27, 0, 0, 0
pmac p22, p20, p27
pfree p27
dload x10, x11, p27, 0, 0, 0
pmac p5, p20, p27
pfree p20
pfree p27
pmodld 3
dload x10, x11, p20, 0, 0, 0
pmac p23, p11, p20
pfree p20
dload x10, x11, p20, 0, 0, 0
pmac p1, p11, p20
pfree p11
pfree p20
pmodld 2
dload x10, x11, p11, 0, 0, 0
pfree p26
dload x10, x11, p20, 0, 1, 32
pintt p11, p20, 0, 0, 0
dload x10, x11, p26, 0, 0, 0
pintt p26, p20, 0, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pintt p11, p20, 1, 0, 0
pintt p26, p20, 1, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pintt p11, p20, 2, 0, 0
pintt p26, p20, 2, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pintt p11, p20, 3, 0, 0
pintt p26, p20, 3, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pintt p11, p20, 4, 0, 0
pintt p26, p20, 4, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pintt p11, p20, 5, 0, 0
pintt p26, p20, 5, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pintt p11, p20, 6, 0, 0
pintt p26, p20, 6, 0, 0
pfree p20
dload x10, x11, p20, 0, 1, 32
pmul p11, p11, p20, 1
pmul p26, p26, p20, 1
pfree p20
pmul p20, p26, p25, 1
pntt p20, p19, 0, 0, 0
pntt p20, p18, 1, 0, 0
pntt p20, p17, 2, 0, 0
pntt p20, p16, 3, 0, 0
pntt p20, p15, 4, 0, 0
pntt p20, p14, 5, 0, 0
pntt p20, p13, 6, 0, 0
dload x10, x11, p27, 0, 0, 0
pmul p26, p26, p27
pfree p27
dload x10, x11, p27, 0, 0, 0
pmac p22, p20, p27
pfree p27
dload x10, x11, p27, 0, 0, 0
pmac p5, p20, p27
pfree p20
pfree p27
pmodld 0
dload x10, x11, p20, 0, 0, 0
pmul p20, p26, p20
pmul p20, p20, p6, 1
pntt p20, p7, 0, 0, 0
pntt p20, p8, 1, 0, 0
pntt p20, p9, 2, 0, 0
pntt p20, p10, 3, 0, 0
dload x10, x11, p27, 0, 1, 32
pntt p20, p27, 4, 0, 0
pfree p13
dload x10, x11, p28, 0, 1, 32
pntt p20, p28, 5, 0, 0
pfree p14
dload x10, x11, p13, 0, 1, 32
pntt p20, p13, 6, 0, 0
dload x10, x11, p14, 0, 0, 0
pmac p12, p20, p14
pfree p14
dload x10, x11, p14, 0, 0, 0
pmac p2, p20, p14
pfree p20
pfree p14
pmodld 1
dload x10, x11, p14, 0, 0, 0
pmul p14, p26, p14
pfree p15
dload x10, x11, p20, 0, 1, 32
pmul p14, p14, p20, 1
pfree p16
dload x10, x11, p15, 0, 1, 32
pntt p14, p15, 0, 0, 0
pfree p17
dload x10, x11, p16, 0, 1, 32
pntt p14, p16, 1, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pntt p14, p17, 2, 0, 0
pfree p19
dload x10, x11, p18, 0, 1, 32
pntt p14, p18, 3, 0, 0
pfree p25
dload x10, x11, p19, 0, 1, 32
pntt p14, p19, 4, 0, 0
pfree p19
dload x10, x11, p25, 0, 1, 32
pntt p14, p25, 5, 0, 0
pfree p25
dload x10, x11, p19, 0, 1, 32
pntt p14, p19, 6, 0, 0
pmodld 3
dload x10, x11, p25, 0, 0, 0
pmul p26, p26, p25
pfree p25
pfree p19
dload x10, x11, p25, 0, 1, 32
pmul p26, p26, p25, 1
pfree p25
dload x10, x11, p19, 0, 1, 32
pntt p26, p19, 0, 0, 0
pfree p19
dload x10, x11, p19, 0, 1, 32
pntt p26, p19, 1, 0, 0
pfree p19
dload x10, x11, p19, 0, 1, 32
pntt p26, p19, 2, 0, 0
pfree p19
dload x10, x11, p19, 0, 1, 32
pntt p26, p19, 3, 0, 0
pfree p19
dload x10, x11, p19, 0, 1, 32
pntt p26, p19, 4, 0, 0
pfree p19
dload x10, x11, p19, 0, 1, 32
pntt p26, p19, 5, 0, 0
pfree p19
dload x10, x11, p19, 0, 1, 32
pntt p26, p19, 6, 0, 0
pfree p19
pmodld 1
dload x10, x11, p19, 0, 0, 0
pmac p21, p14, p19
pfree p19
dload x10, x11, p19, 0, 0, 0
pmac p3, p14, p19
pfree p14
pfree p19
pmodld 3
dload x10, x11, p14, 0, 0, 0
pmac p23, p26, p14
pfree p14
dload x10, x11, p14, 0, 0, 0
pmac p1, p26, p14
pfree p26
pfree p14
pmodld 0
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 0, 0, 0
pintt p2, p14, 0, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 1, 0, 0
pintt p2, p14, 1, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 2, 0, 0
pintt p2, p14, 2, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 3, 0, 0
pintt p2, p14, 3, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 4, 0, 0
pintt p2, p14, 4, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 5, 0, 0
pintt p2, p14, 5, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p12, p14, 6, 0, 0
pintt p2, p14, 6, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pmul p12, p12, p14, 1
pmul p2, p2, p14, 1
pfree p14
pmodld 1
dload x10, x11, p14, 0, 1, 32
pintt p21, p14, 0, 0, 0
pintt p3, p14, 0, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p21, p14, 1, 0, 0
pintt p3, p14, 1, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p21, p14, 2, 0, 0
pintt p3, p14, 2, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p21, p14, 3, 0, 0
pintt p3, p14, 3, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p21, p14, 4, 0, 0
pintt p3, p14, 4, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p21, p14, 5, 0, 0
pintt p3, p14, 5, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p21, p14, 6, 0, 0
pintt p3, p14, 6, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pmul p21, p21, p14, 1
pmul p3, p3, p14, 1
pfree p14
pmodld 2
dload x10, x11, p14, 0, 1, 32
pintt p22, p14, 0, 0, 0
pintt p5, p14, 0, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p22, p14, 1, 0, 0
pintt p5, p14, 1, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p22, p14, 2, 0, 0
pintt p5, p14, 2, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p22, p14, 3, 0, 0
pintt p5, p14, 3, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p22, p14, 4, 0, 0
pintt p5, p14, 4, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p22, p14, 5, 0, 0
pintt p5, p14, 5, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p22, p14, 6, 0, 0
pintt p5, p14, 6, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pmul p22, p22, p14, 1
pmul p5, p5, p14, 1
pfree p14
pmodld 3
dload x10, x11, p14, 0, 1, 32
pintt p23, p14, 0, 0, 0
pintt p1, p14, 0, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p23, p14, 1, 0, 0
pintt p1, p14, 1, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p23, p14, 2, 0, 0
pintt p1, p14, 2, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p23, p14, 3, 0, 0
pintt p1, p14, 3, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p23, p14, 4, 0, 0
pintt p1, p14, 4, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p23, p14, 5, 0, 0
pintt p1, p14, 5, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p23, p14, 6, 0, 0
pintt p1, p14, 6, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pmul p23, p23, p14, 1
pmul p1, p1, p14, 1
pfree p14
pmodld 0
dload x10, x11, p14, 0, 0, 0
padd p12, p12, p14
padd p2, p2, p14
pfree p14
pmodld 1
dload x10, x11, p14, 0, 0, 0
padd p21, p21, p14
padd p3, p3, p14
pfree p14
pmodld 2
dload x10, x11, p14, 0, 0, 0
padd p22, p22, p14
padd p5, p5, p14
pfree p14
pmodld 3
dload x10, x11, p14, 0, 0, 0
padd p23, p23, p14
padd p1, p1, p14
pfree p14
dload x10, x11, p14, 0, 0, 0
pmul p23, p23, p14
pmul p1, p1, p14
pfree p14
pmodld 0
dload x10, x11, p14, 0, 0, 0
pmul p19, p23, p14
psub p12, p12, p19
pfree p19
pmul p14, p1, p14
psub p2, p2, p14
pfree p14
dload x10, x11, p14, 0, 0, 0
pmul p12, p12, p14
pmul p2, p2, p14
pfree p14
padd p12, p12, p0
pfree p0
pmul p12, p12, p6, 1
pmul p2, p2, p6, 1
pfree p6
pntt p12, p7, 0, 0, 0
pntt p2, p7, 0, 0, 0
pfree p7
pntt p12, p8, 1, 0, 0
pntt p2, p8, 1, 0, 0
pfree p8
pntt p12, p9, 2, 0, 0
pntt p2, p9, 2, 0, 0
pfree p9
pntt p12, p10, 3, 0, 0
pntt p2, p10, 3, 0, 0
pfree p10
pntt p12, p27, 4, 0, 0
pntt p2, p27, 4, 0, 0
pfree p27
pntt p12, p28, 5, 0, 0
pntt p2, p28, 5, 0, 0
pfree p28
pntt p12, p13, 6, 0, 0
dstore x10, x11, p12, 1, 0
pntt p2, p13, 6, 0, 0
pfree p13
dstore x10, x11, p2, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p2, p23, p0
psub p21, p21, p2
pfree p2
pmul p0, p1, p0
psub p3, p3, p0
pfree p0
pmodld 2
dload x10, x11, p0, 0, 0, 0
pmul p23, p23, p0
psub p22, p22, p23
pfree p23
pmul p1, p1, p0
pfree p0
psub p5, p5, p1
pfree p1
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p21, p21, p0
pmul p3, p3, p0
pfree p0
padd p21, p21, p24
pfree p24
pmul p21, p21, p20, 1
pmul p3, p3, p20, 1
pfree p20
pntt p21, p15, 0, 0, 0
pntt p3, p15, 0, 0, 0
pfree p15
pntt p21, p16, 1, 0, 0
pntt p3, p16, 1, 0, 0
pfree p16
pntt p21, p17, 2, 0, 0
pntt p3, p17, 2, 0, 0
pfree p17
pntt p21, p18, 3, 0, 0
pntt p3, p18, 3, 0, 0
pfree p18
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 4, 0, 0
pntt p3, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 5, 0, 0
pntt p3, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p21, p0, 6, 0, 0
dstore x10, x11, p21, 1, 0
pntt p3, p0, 6, 0, 0
pfree p0
dstore x10, x11, p3, 1, 0
pmodld 2
dload x10, x11, p0, 0, 0, 0
pmul p22, p22, p0
pmul p5, p5, p0
pfree p0
padd p22, p22, p11
pfree p11
dload x10, x11, p0, 0, 1, 32
pmul p22, p22, p0, 1
pmul p5, p5, p0, 1
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 0, 0, 0
pntt p5, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 1, 0, 0
pntt p5, p0, 1, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 2, 0, 0
pntt p5, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 3, 0, 0
pntt p5, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 4, 0, 0
pntt p5, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 5, 0, 0
pntt p5, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 6, 0, 0
dstore x10, x11, p22, 1, 0
pntt p5, p0, 6, 0, 0
pfree p0
dstore x10, x11, p5, 1, 0
psync
