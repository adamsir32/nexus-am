dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
padd p0, p0, p1
pmodld 1
dload x10, x11, p2, 0, 0, 0
padd p2, p2, p1
pmodld 2
dload x10, x11, p3, 0, 0, 0
padd p3, p3, p1
pfree p1
pmodld 0
dload x10, x11, p1, 0, 1, 32
pintt p0, p1, 0, 0, 0
pmodld 1
pintt p2, p1, 0, 0, 0
pmodld 2
pintt p3, p1, 0, 0, 0
pmodld 0
dload x10, x11, p5, 0, 1, 32
pintt p0, p5, 1, 0, 0
dload x10, x11, p6, 0, 1, 32
pintt p0, p6, 2, 0, 0
dload x10, x11, p7, 0, 1, 32
pintt p0, p7, 3, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p0, p8, 4, 0, 0
dload x10, x11, p9, 0, 1, 32
pintt p0, p9, 5, 0, 0
dload x10, x11, p10, 0, 1, 32
pintt p0, p10, 6, 0, 0
dload x10, x11, p11, 0, 1, 32
pmul p0, p0, p11, 1
dload x10, x11, p12, 0, 1, 32
pmul p0, p0, p12, 1
pntt p0, p1, 0, 0, 0
dload x10, x11, p13, 0, 1, 32
pntt p0, p13, 1, 0, 0
dload x10, x11, p14, 0, 1, 32
pntt p0, p14, 2, 0, 0
dload x10, x11, p15, 0, 1, 32
pntt p0, p15, 3, 0, 0
dload x10, x11, p16, 0, 1, 32
pntt p0, p16, 4, 0, 0
dload x10, x11, p17, 0, 1, 32
pntt p0, p17, 5, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p0, p18, 6, 0, 0
pmodld 1
pfree p18
dload x10, x11, p17, 0, 1, 32
pintt p2, p17, 1, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pintt p2, p18, 2, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pintt p2, p17, 3, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pintt p2, p18, 4, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pintt p2, p17, 5, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pintt p2, p18, 6, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pmul p2, p2, p17, 1
pfree p17
dload x10, x11, p18, 0, 1, 32
pmul p2, p2, p18, 1
pntt p2, p1, 0, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pntt p2, p17, 1, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p2, p18, 2, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pntt p2, p17, 3, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p2, p18, 4, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pntt p2, p17, 5, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p2, p18, 6, 0, 0
pmodld 2
pfree p18
dload x10, x11, p17, 0, 1, 32
pintt p3, p17, 1, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pintt p3, p18, 2, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pintt p3, p17, 3, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pintt p3, p18, 4, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pintt p3, p17, 5, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pintt p3, p18, 6, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pmul p3, p3, p17, 1
pfree p17
dload x10, x11, p18, 0, 1, 32
pmul p3, p3, p18, 1
pntt p3, p1, 0, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pntt p3, p17, 1, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p3, p18, 2, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pntt p3, p17, 3, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p3, p18, 4, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pntt p3, p17, 5, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p3, p18, 6, 0, 0
pmodld 0
dload x10, x11, p17, 0, 0, 0
pintt p17, p1, 0, 0, 0
pintt p17, p5, 1, 0, 0
pfree p5
pintt p17, p6, 2, 0, 0
pfree p6
pintt p17, p7, 3, 0, 0
pfree p7
pintt p17, p8, 4, 0, 0
pfree p8
pintt p17, p9, 5, 0, 0
pfree p9
pintt p17, p10, 6, 0, 0
pfree p10
pmul p17, p17, p11, 1
pfree p11
pmul p17, p17, p12, 1
pntt p17, p1, 0, 0, 0
pntt p17, p13, 1, 0, 0
pntt p17, p14, 2, 0, 0
pntt p17, p15, 3, 0, 0
pntt p17, p16, 4, 0, 0
dload x10, x11, p5, 0, 1, 32
pntt p17, p5, 5, 0, 0
dload x10, x11, p6, 0, 1, 32
pntt p17, p6, 6, 0, 0
dstore x10, x11, p17, 0, 0
dload x10, x11, p7, 0, 0, 0
pintt p7, p1, 0, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p7, p8, 1, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p7, p8, 2, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p7, p8, 3, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p7, p8, 4, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p7, p8, 5, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p7, p8, 6, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pmul p7, p7, p8, 1
pfree p8
pmodld 1
pmul p8, p7, 1
dload x10, x11, p9, 0, 1, 32
pmul p8, p8, p9, 1
pntt p8, p1, 0, 0, 0
dload x10, x11, p10, 0, 1, 32
pntt p8, p10, 1, 0, 0
dload x10, x11, p11, 0, 1, 32
pntt p8, p11, 2, 0, 0
dload x10, x11, p19, 0, 1, 32
pntt p8, p19, 3, 0, 0
dload x10, x11, p20, 0, 1, 32
pntt p8, p20, 4, 0, 0
pfree p6
dload x10, x11, p21, 0, 1, 32
pntt p8, p21, 5, 0, 0
pfree p5
dload x10, x11, p6, 0, 1, 32
pntt p8, p6, 6, 0, 0
pmodld 2
pmul p5, p7, 1
pfree p16
dload x10, x11, p22, 0, 1, 32
pmul p5, p5, p22, 1
pntt p5, p1, 0, 0, 0
pfree p22
dload x10, x11, p16, 0, 1, 32
pntt p5, p16, 1, 0, 0
pfree p16
dload x10, x11, p22, 0, 1, 32
pntt p5, p22, 2, 0, 0
pfree p22
dload x10, x11, p16, 0, 1, 32
pntt p5, p16, 3, 0, 0
pfree p16
dload x10, x11, p22, 0, 1, 32
pntt p5, p22, 4, 0, 0
pfree p22
dload x10, x11, p16, 0, 1, 32
pntt p5, p16, 5, 0, 0
pntt p5, p18, 6, 0, 0
pmodld 3
pmul p7, p7, 1
pmodld 1
dload x10, x11, p22, 0, 0, 0
pintt p22, p1, 0, 0, 0
pfree p18
dload x10, x11, p23, 0, 1, 32
pintt p22, p23, 1, 0, 0
pfree p23
dload x10, x11, p18, 0, 1, 32
pintt p22, p18, 2, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pintt p22, p18, 3, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pintt p22, p18, 4, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pintt p22, p18, 5, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pintt p22, p18, 6, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pmul p22, p22, p18, 1
pfree p18
pmul p22, p22, p9, 1
pntt p22, p1, 0, 0, 0
pntt p22, p10, 1, 0, 0
pntt p22, p11, 2, 0, 0
pntt p22, p19, 3, 0, 0
pntt p22, p20, 4, 0, 0
pntt p22, p21, 5, 0, 0
pntt p22, p6, 6, 0, 0
dstore x10, x11, p22, 0, 0
dload x10, x11, p18, 0, 0, 0
pintt p18, p1, 0, 0, 0
dload x10, x11, p23, 0, 1, 32
pintt p18, p23, 1, 0, 0
pfree p23
dload x10, x11, p23, 0, 1, 32
pintt p18, p23, 2, 0, 0
pfree p23
dload x10, x11, p23, 0, 1, 32
pintt p18, p23, 3, 0, 0
pfree p23
dload x10, x11, p23, 0, 1, 32
pintt p18, p23, 4, 0, 0
pfree p23
dload x10, x11, p23, 0, 1, 32
pintt p18, p23, 5, 0, 0
pfree p23
dload x10, x11, p23, 0, 1, 32
pintt p18, p23, 6, 0, 0
pfree p23
dload x10, x11, p23, 0, 1, 32
pmul p18, p18, p23, 1
pfree p23
pmodld 0
pmul p23, p18, 1
pmul p23, p23, p12, 1
pntt p23, p1, 0, 0, 0
pntt p23, p13, 1, 0, 0
pntt p23, p14, 2, 0, 0
pntt p23, p15, 3, 0, 0
dload x10, x11, p24, 0, 1, 32
pntt p23, p24, 4, 0, 0
pfree p6
dload x10, x11, p25, 0, 1, 32
pntt p23, p25, 5, 0, 0
pfree p21
dload x10, x11, p6, 0, 1, 32
pntt p23, p6, 6, 0, 0
pmodld 2
pmul p21, p18, 1
pfree p20
dload x10, x11, p26, 0, 1, 32
pmul p21, p21, p26, 1
pntt p21, p1, 0, 0, 0
pfree p19
dload x10, x11, p20, 0, 1, 32
pntt p21, p20, 1, 0, 0
pfree p11
dload x10, x11, p19, 0, 1, 32
pntt p21, p19, 2, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pntt p21, p11, 3, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pntt p21, p10, 4, 0, 0
pntt p21, p16, 5, 0, 0
pfree p6
dload x10, x11, p9, 0, 1, 32
pntt p21, p9, 6, 0, 0
pmodld 3
pmul p18, p18, 1
pmodld 2
dload x10, x11, p6, 0, 0, 0
pintt p6, p1, 0, 0, 0
pfree p25
dload x10, x11, p27, 0, 1, 32
pintt p6, p27, 1, 0, 0
pfree p27
dload x10, x11, p25, 0, 1, 32
pintt p6, p25, 2, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p6, p25, 3, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p6, p25, 4, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p6, p25, 5, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p6, p25, 6, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pmul p6, p6, p25, 1
pfree p25
pmul p6, p6, p26, 1
pntt p6, p1, 0, 0, 0
pntt p6, p20, 1, 0, 0
pntt p6, p19, 2, 0, 0
pntt p6, p11, 3, 0, 0
pntt p6, p10, 4, 0, 0
pntt p6, p16, 5, 0, 0
pntt p6, p9, 6, 0, 0
dstore x10, x11, p6, 0, 0
dload x10, x11, p25, 0, 0, 0
pintt p25, p1, 0, 0, 0
dload x10, x11, p27, 0, 1, 32
pintt p25, p27, 1, 0, 0
pfree p27
dload x10, x11, p27, 0, 1, 32
pintt p25, p27, 2, 0, 0
pfree p27
dload x10, x11, p27, 0, 1, 32
pintt p25, p27, 3, 0, 0
pfree p27
dload x10, x11, p27, 0, 1, 32
pintt p25, p27, 4, 0, 0
pfree p27
dload x10, x11, p27, 0, 1, 32
pintt p25, p27, 5, 0, 0
pfree p27
dload x10, x11, p27, 0, 1, 32
pintt p25, p27, 6, 0, 0
pfree p27
dload x10, x11, p27, 0, 1, 32
pmul p25, p25, p27, 1
pfree p27
pmodld 0
pmul p27, p25, 1
pmul p27, p27, p12, 1
pntt p27, p1, 0, 0, 0
pntt p27, p13, 1, 0, 0
pntt p27, p14, 2, 0, 0
pntt p27, p15, 3, 0, 0
pntt p27, p24, 4, 0, 0
dload x10, x11, p28, 0, 1, 32
pntt p27, p28, 5, 0, 0
pfree p9
dload x10, x11, p29, 0, 1, 32
pntt p27, p29, 6, 0, 0
pmodld 1
pmul p9, p25, 1
pfree p16
dload x10, x11, p30, 0, 1, 32
pmul p9, p9, p30, 1
pntt p9, p1, 0, 0, 0
pfree p10
dload x10, x11, p16, 0, 1, 32
pntt p9, p16, 1, 0, 0
pfree p11
dload x10, x11, p10, 0, 1, 32
pntt p9, p10, 2, 0, 0
pfree p19
dload x10, x11, p11, 0, 1, 32
pntt p9, p11, 3, 0, 0
pfree p20
dload x10, x11, p19, 0, 1, 32
pntt p9, p19, 4, 0, 0
pfree p26
dload x10, x11, p20, 0, 1, 32
pntt p9, p20, 5, 0, 0
pfree p20
dload x10, x11, p26, 0, 1, 32
pntt p9, p26, 6, 0, 0
pmodld 3
pmul p25, p25, 1
pmodld 0
dload x10, x11, p20, 0, 0, 0
pmul p20, p17, p20
dload x10, x11, p31, 0, 0, 0
pmul p17, p17, p31
pfree p31
dload x10, x11, p31, 0, 0, 0
pmac p20, p23, p31
pfree p31
dload x10, x11, p31, 0, 0, 0
pmac p17, p23, p31
pfree p23
pfree p31
dload x10, x11, p23, 0, 0, 0
pmac p20, p27, p23
pfree p23
dload x10, x11, p23, 0, 0, 0
pmac p17, p27, p23
pfree p27
pfree p23
pmodld 1
dload x10, x11, p23, 0, 0, 0
pmul p23, p8, p23
dload x10, x11, p27, 0, 0, 0
pmul p8, p8, p27
pfree p27
dload x10, x11, p27, 0, 0, 0
pmac p23, p22, p27
pfree p27
dload x10, x11, p27, 0, 0, 0
pmac p8, p22, p27
pfree p22
pfree p27
dload x10, x11, p22, 0, 0, 0
pmac p23, p9, p22
pfree p22
dload x10, x11, p22, 0, 0, 0
pmac p8, p9, p22
pfree p9
pfree p22
pmodld 2
dload x10, x11, p9, 0, 0, 0
pmul p9, p5, p9
dload x10, x11, p22, 0, 0, 0
pmul p5, p5, p22
pfree p22
dload x10, x11, p22, 0, 0, 0
pmac p9, p21, p22
pfree p22
dload x10, x11, p22, 0, 0, 0
pmac p5, p21, p22
pfree p21
pfree p22
dload x10, x11, p21, 0, 0, 0
pmac p9, p6, p21
pfree p21
dload x10, x11, p21, 0, 0, 0
pmac p5, p6, p21
pfree p6
pfree p21
pmodld 3
pfree p26
dload x10, x11, p6, 0, 1, 32
pmul p7, p7, p6, 1
pntt p7, p1, 0, 0, 0
pmul p18, p18, p6, 1
pmul p25, p25, p6, 1
pfree p6
pntt p18, p1, 0, 0, 0
pntt p25, p1, 0, 0, 0
dload x10, x11, p6, 0, 1, 32
pntt p7, p6, 1, 0, 0
pntt p18, p6, 1, 0, 0
pntt p25, p6, 1, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p7, p6, 2, 0, 0
pntt p18, p6, 2, 0, 0
pntt p25, p6, 2, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p7, p6, 3, 0, 0
pntt p18, p6, 3, 0, 0
pntt p25, p6, 3, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p7, p6, 4, 0, 0
pntt p18, p6, 4, 0, 0
pntt p25, p6, 4, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p7, p6, 5, 0, 0
pntt p18, p6, 5, 0, 0
pntt p25, p6, 5, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p7, p6, 6, 0, 0
pntt p18, p6, 6, 0, 0
pntt p25, p6, 6, 0, 0
pfree p6
dload x10, x11, p6, 0, 0, 0
pmul p6, p7, p6
dload x10, x11, p21, 0, 0, 0
pmul p7, p7, p21
pfree p21
dload x10, x11, p21, 0, 0, 0
pmac p6, p18, p21
pfree p21
dload x10, x11, p21, 0, 0, 0
pmac p7, p18, p21
pfree p18
pfree p21
dload x10, x11, p18, 0, 0, 0
pmac p6, p25, p18
pfree p18
pintt p6, p1, 0, 0, 0
dload x10, x11, p18, 0, 0, 0
pmac p7, p25, p18
pfree p25
pfree p18
pintt p7, p1, 0, 0, 0
dload x10, x11, p18, 0, 1, 32
pintt p6, p18, 1, 0, 0
pintt p7, p18, 1, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pintt p6, p18, 2, 0, 0
pintt p7, p18, 2, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pintt p6, p18, 3, 0, 0
pintt p7, p18, 3, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pintt p6, p18, 4, 0, 0
pintt p7, p18, 4, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pintt p6, p18, 5, 0, 0
pintt p7, p18, 5, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pintt p6, p18, 6, 0, 0
pintt p7, p18, 6, 0, 0
pfree p18
dload x10, x11, p18, 0, 1, 32
pmul p6, p6, p18, 1
pmul p7, p7, p18, 1
pfree p18
pmodld 0
pmul p18, p6, 1
pmodld 1
pmul p21, p6, 1
pmodld 2
pmul p22, p6, 1
pmodld 0
pmul p25, p7, 1
pmodld 1
pmul p26, p7, 1
pmodld 2
pmul p27, p7, 1
pmodld 4
dload x10, x11, p31, 0, 0, 0
pmul p6, p6, p31
pmul p7, p7, p31
pfree p31
pmodld 0
dload x10, x11, p31, 0, 0, 0
pmul p32, p6, p31
padd p32, p32, p18
pfree p18
pmul p32, p32, p12, 1
pntt p32, p1, 0, 0, 0
pntt p32, p13, 1, 0, 0
pntt p32, p14, 2, 0, 0
pntt p32, p15, 3, 0, 0
pntt p32, p24, 4, 0, 0
pntt p32, p28, 5, 0, 0
pntt p32, p29, 6, 0, 0
psub p20, p20, p32
pfree p32
pmodld 1
pmul p18, p6, p31
padd p18, p18, p21
pfree p21
pmul p18, p18, p30, 1
pntt p18, p1, 0, 0, 0
pntt p18, p16, 1, 0, 0
pntt p18, p10, 2, 0, 0
pntt p18, p11, 3, 0, 0
pntt p18, p19, 4, 0, 0
dload x10, x11, p21, 0, 1, 32
pntt p18, p21, 5, 0, 0
pfree p21
dload x10, x11, p32, 0, 1, 32
pntt p18, p32, 6, 0, 0
psub p23, p23, p18
pfree p18
pmodld 0
pmul p18, p7, p31
padd p18, p18, p25
pfree p25
pmul p18, p18, p12, 1
pfree p12
pntt p18, p1, 0, 0, 0
pntt p18, p13, 1, 0, 0
pfree p13
pntt p18, p14, 2, 0, 0
pfree p14
pntt p18, p15, 3, 0, 0
pfree p15
pntt p18, p24, 4, 0, 0
pfree p24
pntt p18, p28, 5, 0, 0
pfree p28
pntt p18, p29, 6, 0, 0
pfree p29
psub p17, p17, p18
pfree p18
pmodld 1
pmul p31, p7, p31
padd p31, p31, p26
pfree p26
pmul p31, p31, p30, 1
pfree p30
pntt p31, p1, 0, 0, 0
pntt p31, p16, 1, 0, 0
pfree p16
pntt p31, p10, 2, 0, 0
pfree p10
pntt p31, p11, 3, 0, 0
pfree p11
pntt p31, p19, 4, 0, 0
pfree p19
dload x10, x11, p10, 0, 1, 32
pntt p31, p10, 5, 0, 0
pfree p10
pntt p31, p32, 6, 0, 0
pfree p32
psub p8, p8, p31
pfree p31
pmodld 0
dload x10, x11, p10, 0, 0, 0
pmul p20, p20, p10
padd p20, p20, p0
pfree p0
pmul p17, p17, p10
pfree p10
dload x10, x11, p0, 0, 0, 0
padd p17, p17, p0
pfree p0
dstore x10, x11, p17, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p23, p23, p0
padd p23, p23, p2
pfree p2
pmul p8, p8, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
padd p8, p8, p0
pfree p0
dstore x10, x11, p8, 1, 0
pmodld 2
dload x10, x11, p0, 0, 0, 0
pmul p6, p6, p0
padd p6, p6, p22
pfree p22
pmul p7, p7, p0
pfree p0
padd p7, p7, p27
pfree p27
dload x10, x11, p0, 0, 1, 32
pmul p6, p6, p0, 1
pmul p7, p7, p0, 1
pfree p0
pntt p6, p1, 0, 0, 0
pntt p7, p1, 0, 0, 0
pfree p1
dload x10, x11, p0, 0, 1, 32
pntt p6, p0, 1, 0, 0
pntt p7, p0, 1, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p6, p0, 2, 0, 0
pntt p7, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p6, p0, 3, 0, 0
pntt p7, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p6, p0, 4, 0, 0
pntt p7, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p6, p0, 5, 0, 0
pntt p7, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p6, p0, 6, 0, 0
psub p9, p9, p6
pfree p6
pntt p7, p0, 6, 0, 0
pfree p0
psub p5, p5, p7
pfree p7
dload x10, x11, p0, 0, 0, 0
pmul p9, p9, p0
padd p9, p9, p3
pfree p3
pmul p5, p5, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
padd p5, p5, p0
pfree p0
dstore x10, x11, p5, 1, 0
pmodld 0
dload x10, x11, p0, 0, 0, 0
padd p20, p20, p0
dstore x10, x11, p20, 1, 0
pmodld 1
padd p23, p23, p0
dstore x10, x11, p23, 1, 0
pmodld 2
padd p9, p9, p0
pfree p0
dstore x10, x11, p9, 1, 0
psync
