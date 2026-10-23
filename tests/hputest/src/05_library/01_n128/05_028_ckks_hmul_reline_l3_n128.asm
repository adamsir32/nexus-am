dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
pmul p2, p0, p1
dload x10, x11, p3, 0, 0, 0
pmul p0, p0, p3
dload x10, x11, p5, 0, 0, 0
pmac p0, p5, p1
pfree p1
pmul p5, p5, p3
pfree p3
dload x10, x11, p1, 0, 1, 32
pintt p2, p1, 0, 0, 0
pintt p0, p1, 0, 0, 0
pintt p5, p1, 0, 0, 0
dload x10, x11, p3, 0, 1, 32
pintt p2, p3, 1, 0, 0
pintt p0, p3, 1, 0, 0
pintt p5, p3, 1, 0, 0
dload x10, x11, p6, 0, 1, 32
pintt p2, p6, 2, 0, 0
pintt p0, p6, 2, 0, 0
pintt p5, p6, 2, 0, 0
dload x10, x11, p7, 0, 1, 32
pintt p2, p7, 3, 0, 0
pintt p0, p7, 3, 0, 0
pintt p5, p7, 3, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p2, p8, 4, 0, 0
pintt p0, p8, 4, 0, 0
pintt p5, p8, 4, 0, 0
dload x10, x11, p9, 0, 1, 32
pintt p2, p9, 5, 0, 0
pintt p0, p9, 5, 0, 0
pintt p5, p9, 5, 0, 0
dload x10, x11, p10, 0, 1, 32
pintt p2, p10, 6, 0, 0
pintt p0, p10, 6, 0, 0
pintt p5, p10, 6, 0, 0
dload x10, x11, p11, 0, 1, 32
pmul p2, p2, p11, 1
pmul p0, p0, p11, 1
pmul p5, p5, p11, 1
dload x10, x11, p12, 0, 0, 0
pmul p12, p5, p12
pmodld 1
dload x10, x11, p13, 0, 0, 0
pmul p13, p12, p13
pmodld 2
dload x10, x11, p14, 0, 0, 0
pmul p14, p12, p14
pmodld 3
dload x10, x11, p15, 0, 0, 0
pmul p12, p12, p15
pfree p15
pmodld 0
dload x10, x11, p15, 0, 1, 32
pmul p5, p5, p15, 1
dload x10, x11, p16, 0, 1, 32
pntt p5, p16, 0, 0, 0
dload x10, x11, p17, 0, 1, 32
pntt p5, p17, 1, 0, 0
dload x10, x11, p18, 0, 1, 32
pntt p5, p18, 2, 0, 0
dload x10, x11, p19, 0, 1, 32
pntt p5, p19, 3, 0, 0
dload x10, x11, p20, 0, 1, 32
pntt p5, p20, 4, 0, 0
pfree p11
dload x10, x11, p21, 0, 1, 32
pntt p5, p21, 5, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pntt p5, p11, 6, 0, 0
pmodld 1
pfree p9
dload x10, x11, p10, 0, 1, 32
pmul p13, p13, p10, 1
pfree p8
dload x10, x11, p9, 0, 1, 32
pntt p13, p9, 0, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pntt p13, p8, 1, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pntt p13, p7, 2, 0, 0
pfree p3
dload x10, x11, p6, 0, 1, 32
pntt p13, p6, 3, 0, 0
pfree p1
dload x10, x11, p3, 0, 1, 32
pntt p13, p3, 4, 0, 0
pfree p11
dload x10, x11, p1, 0, 1, 32
pntt p13, p1, 5, 0, 0
pfree p21
dload x10, x11, p11, 0, 1, 32
pntt p13, p11, 6, 0, 0
pmodld 2
pfree p20
dload x10, x11, p21, 0, 1, 32
pmul p14, p14, p21, 1
pfree p21
dload x10, x11, p20, 0, 1, 32
pntt p14, p20, 0, 0, 0
pfree p20
dload x10, x11, p21, 0, 1, 32
pntt p14, p21, 1, 0, 0
pfree p21
dload x10, x11, p20, 0, 1, 32
pntt p14, p20, 2, 0, 0
pfree p20
dload x10, x11, p21, 0, 1, 32
pntt p14, p21, 3, 0, 0
pfree p21
dload x10, x11, p20, 0, 1, 32
pntt p14, p20, 4, 0, 0
pfree p20
dload x10, x11, p21, 0, 1, 32
pntt p14, p21, 5, 0, 0
pfree p21
dload x10, x11, p20, 0, 1, 32
pntt p14, p20, 6, 0, 0
pmodld 3
pfree p20
dload x10, x11, p21, 0, 1, 32
pmul p12, p12, p21, 1
pfree p21
dload x10, x11, p20, 0, 1, 32
pntt p12, p20, 0, 0, 0
pfree p20
dload x10, x11, p21, 0, 1, 32
pntt p12, p21, 1, 0, 0
pfree p21
dload x10, x11, p20, 0, 1, 32
pntt p12, p20, 2, 0, 0
pfree p20
dload x10, x11, p21, 0, 1, 32
pntt p12, p21, 3, 0, 0
pfree p21
dload x10, x11, p20, 0, 1, 32
pntt p12, p20, 4, 0, 0
pfree p20
dload x10, x11, p21, 0, 1, 32
pntt p12, p21, 5, 0, 0
pfree p21
dload x10, x11, p20, 0, 1, 32
pntt p12, p20, 6, 0, 0
pmodld 0
dload x10, x11, p21, 0, 0, 0
pmul p21, p5, p21
dload x10, x11, p22, 0, 0, 0
pmul p5, p5, p22
pfree p22
pmodld 1
dload x10, x11, p22, 0, 0, 0
pmul p22, p13, p22
dload x10, x11, p23, 0, 0, 0
pmul p13, p13, p23
pfree p23
pmodld 2
dload x10, x11, p23, 0, 0, 0
pmul p23, p14, p23
dload x10, x11, p24, 0, 0, 0
pmul p14, p14, p24
pfree p24
pmodld 3
dload x10, x11, p24, 0, 0, 0
pmul p24, p12, p24
dload x10, x11, p25, 0, 0, 0
pmul p12, p12, p25
pfree p25
pmodld 1
dload x10, x11, p25, 0, 0, 0
dload x10, x11, p26, 0, 0, 0
pmul p27, p25, p26
dload x10, x11, p28, 0, 0, 0
pmul p25, p25, p28
dload x10, x11, p29, 0, 0, 0
pmac p25, p29, p26
pfree p26
pmul p29, p29, p28
pfree p28
pfree p20
dload x10, x11, p26, 0, 1, 32
pintt p27, p26, 0, 0, 0
pintt p25, p26, 0, 0, 0
pintt p29, p26, 0, 0, 0
pfree p26
dload x10, x11, p20, 0, 1, 32
pintt p27, p20, 1, 0, 0
pintt p25, p20, 1, 0, 0
pintt p29, p20, 1, 0, 0
pfree p20
dload x10, x11, p26, 0, 1, 32
pintt p27, p26, 2, 0, 0
pintt p25, p26, 2, 0, 0
pintt p29, p26, 2, 0, 0
pfree p26
dload x10, x11, p20, 0, 1, 32
pintt p27, p20, 3, 0, 0
pintt p25, p20, 3, 0, 0
pintt p29, p20, 3, 0, 0
pfree p20
dload x10, x11, p26, 0, 1, 32
pintt p27, p26, 4, 0, 0
pintt p25, p26, 4, 0, 0
pintt p29, p26, 4, 0, 0
pfree p26
dload x10, x11, p20, 0, 1, 32
pintt p27, p20, 5, 0, 0
pintt p25, p20, 5, 0, 0
pintt p29, p20, 5, 0, 0
pfree p20
dload x10, x11, p26, 0, 1, 32
pintt p27, p26, 6, 0, 0
pintt p25, p26, 6, 0, 0
pintt p29, p26, 6, 0, 0
pfree p26
dload x10, x11, p20, 0, 1, 32
pmul p27, p27, p20, 1
pmul p25, p25, p20, 1
pmul p29, p29, p20, 1
pmul p26, p29, p10, 1
pntt p26, p9, 0, 0, 0
pntt p26, p8, 1, 0, 0
pntt p26, p7, 2, 0, 0
pntt p26, p6, 3, 0, 0
pntt p26, p3, 4, 0, 0
pntt p26, p1, 5, 0, 0
pntt p26, p11, 6, 0, 0
dload x10, x11, p28, 0, 0, 0
pmul p29, p29, p28
pfree p28
dload x10, x11, p28, 0, 0, 0
pmac p22, p26, p28
pfree p28
dload x10, x11, p28, 0, 0, 0
pmac p13, p26, p28
pfree p26
pfree p28
pmodld 0
dload x10, x11, p26, 0, 0, 0
pmul p26, p29, p26
pmul p26, p26, p15, 1
pntt p26, p16, 0, 0, 0
pntt p26, p17, 1, 0, 0
pntt p26, p18, 2, 0, 0
pntt p26, p19, 3, 0, 0
pfree p20
dload x10, x11, p28, 0, 1, 32
pntt p26, p28, 4, 0, 0
pfree p11
dload x10, x11, p20, 0, 1, 32
pntt p26, p20, 5, 0, 0
pfree p1
dload x10, x11, p11, 0, 1, 32
pntt p26, p11, 6, 0, 0
dload x10, x11, p1, 0, 0, 0
pmac p21, p26, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmac p5, p26, p1
pfree p26
pfree p1
pmodld 2
dload x10, x11, p1, 0, 0, 0
pmul p1, p29, p1
pfree p3
dload x10, x11, p26, 0, 1, 32
pmul p1, p1, p26, 1
pfree p6
dload x10, x11, p3, 0, 1, 32
pntt p1, p3, 0, 0, 0
pfree p7
dload x10, x11, p6, 0, 1, 32
pntt p1, p6, 1, 0, 0
pfree p8
dload x10, x11, p7, 0, 1, 32
pntt p1, p7, 2, 0, 0
pfree p9
dload x10, x11, p8, 0, 1, 32
pntt p1, p8, 3, 0, 0
pfree p10
dload x10, x11, p9, 0, 1, 32
pntt p1, p9, 4, 0, 0
pfree p11
dload x10, x11, p10, 0, 1, 32
pntt p1, p10, 5, 0, 0
pfree p20
dload x10, x11, p11, 0, 1, 32
pntt p1, p11, 6, 0, 0
pmodld 3
dload x10, x11, p20, 0, 0, 0
pmul p29, p29, p20
pfree p20
pfree p28
dload x10, x11, p20, 0, 1, 32
pmul p29, p29, p20, 1
pfree p20
dload x10, x11, p28, 0, 1, 32
pntt p29, p28, 0, 0, 0
pfree p28
dload x10, x11, p20, 0, 1, 32
pntt p29, p20, 1, 0, 0
pfree p20
dload x10, x11, p28, 0, 1, 32
pntt p29, p28, 2, 0, 0
pfree p28
dload x10, x11, p20, 0, 1, 32
pntt p29, p20, 3, 0, 0
pfree p20
dload x10, x11, p28, 0, 1, 32
pntt p29, p28, 4, 0, 0
pfree p28
dload x10, x11, p20, 0, 1, 32
pntt p29, p20, 5, 0, 0
pfree p20
dload x10, x11, p28, 0, 1, 32
pntt p29, p28, 6, 0, 0
pmodld 2
dload x10, x11, p20, 0, 0, 0
pmac p23, p1, p20
pfree p20
dload x10, x11, p20, 0, 0, 0
pmac p14, p1, p20
pfree p1
pfree p20
pmodld 3
dload x10, x11, p1, 0, 0, 0
pmac p24, p29, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmac p12, p29, p1
pfree p29
pfree p1
pmodld 2
dload x10, x11, p1, 0, 0, 0
dload x10, x11, p20, 0, 0, 0
pmul p29, p1, p20
dload x10, x11, p30, 0, 0, 0
pmul p1, p1, p30
dload x10, x11, p31, 0, 0, 0
pmac p1, p31, p20
pfree p20
pmul p31, p31, p30
pfree p30
pfree p28
dload x10, x11, p20, 0, 1, 32
pintt p29, p20, 0, 0, 0
pintt p1, p20, 0, 0, 0
pintt p31, p20, 0, 0, 0
pfree p19
dload x10, x11, p28, 0, 1, 32
pintt p29, p28, 1, 0, 0
pintt p1, p28, 1, 0, 0
pintt p31, p28, 1, 0, 0
pfree p18
dload x10, x11, p19, 0, 1, 32
pintt p29, p19, 2, 0, 0
pintt p1, p19, 2, 0, 0
pintt p31, p19, 2, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pintt p29, p18, 3, 0, 0
pintt p1, p18, 3, 0, 0
pintt p31, p18, 3, 0, 0
pfree p16
dload x10, x11, p17, 0, 1, 32
pintt p29, p17, 4, 0, 0
pintt p1, p17, 4, 0, 0
pintt p31, p17, 4, 0, 0
pfree p15
dload x10, x11, p16, 0, 1, 32
pintt p29, p16, 5, 0, 0
pintt p1, p16, 5, 0, 0
pintt p31, p16, 5, 0, 0
pfree p16
dload x10, x11, p15, 0, 1, 32
pintt p29, p15, 6, 0, 0
pintt p1, p15, 6, 0, 0
pintt p31, p15, 6, 0, 0
pfree p15
dload x10, x11, p16, 0, 1, 32
pmul p29, p29, p16, 1
pmul p1, p1, p16, 1
pmul p31, p31, p16, 1
pmul p15, p31, p26, 1
pntt p15, p3, 0, 0, 0
pntt p15, p6, 1, 0, 0
pntt p15, p7, 2, 0, 0
pntt p15, p8, 3, 0, 0
pntt p15, p9, 4, 0, 0
pntt p15, p10, 5, 0, 0
pntt p15, p11, 6, 0, 0
dload x10, x11, p30, 0, 0, 0
pmul p31, p31, p30
pfree p30
dload x10, x11, p30, 0, 0, 0
pmac p23, p15, p30
pfree p30
pintt p23, p20, 0, 0, 0
pintt p23, p28, 1, 0, 0
pintt p23, p19, 2, 0, 0
pintt p23, p18, 3, 0, 0
pintt p23, p17, 4, 0, 0
pfree p11
dload x10, x11, p30, 0, 1, 32
pintt p23, p30, 5, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pintt p23, p11, 6, 0, 0
pmul p23, p23, p16, 1
dload x10, x11, p10, 0, 0, 0
pmac p14, p15, p10
pfree p15
pfree p10
pintt p14, p20, 0, 0, 0
pfree p20
pintt p14, p28, 1, 0, 0
pfree p28
pintt p14, p19, 2, 0, 0
pfree p19
pintt p14, p18, 3, 0, 0
pfree p18
pintt p14, p17, 4, 0, 0
pfree p17
pintt p14, p30, 5, 0, 0
pfree p30
pintt p14, p11, 6, 0, 0
pfree p11
pmul p14, p14, p16, 1
pfree p16
pmodld 0
dload x10, x11, p10, 0, 0, 0
pmul p10, p31, p10
dload x10, x11, p11, 0, 1, 32
pmul p10, p10, p11, 1
dload x10, x11, p15, 0, 1, 32
pntt p10, p15, 0, 0, 0
dload x10, x11, p16, 0, 1, 32
pntt p10, p16, 1, 0, 0
dload x10, x11, p17, 0, 1, 32
pntt p10, p17, 2, 0, 0
dload x10, x11, p18, 0, 1, 32
pntt p10, p18, 3, 0, 0
dload x10, x11, p19, 0, 1, 32
pntt p10, p19, 4, 0, 0
dload x10, x11, p20, 0, 1, 32
pntt p10, p20, 5, 0, 0
dload x10, x11, p28, 0, 1, 32
pntt p10, p28, 6, 0, 0
dload x10, x11, p30, 0, 0, 0
pmac p21, p10, p30
pfree p30
pfree p9
dload x10, x11, p30, 0, 1, 32
pintt p21, p30, 0, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pintt p21, p9, 1, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pintt p21, p8, 2, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pintt p21, p7, 3, 0, 0
pfree p3
dload x10, x11, p6, 0, 1, 32
pintt p21, p6, 4, 0, 0
pfree p26
dload x10, x11, p3, 0, 1, 32
pintt p21, p3, 5, 0, 0
pfree p28
dload x10, x11, p26, 0, 1, 32
pintt p21, p26, 6, 0, 0
pfree p20
dload x10, x11, p28, 0, 1, 32
pmul p21, p21, p28, 1
dload x10, x11, p20, 0, 0, 0
pmac p5, p10, p20
pfree p10
pfree p20
pintt p5, p30, 0, 0, 0
pfree p30
pintt p5, p9, 1, 0, 0
pfree p9
pintt p5, p8, 2, 0, 0
pfree p8
pintt p5, p7, 3, 0, 0
pfree p7
pintt p5, p6, 4, 0, 0
pfree p6
pintt p5, p3, 5, 0, 0
pfree p3
pintt p5, p26, 6, 0, 0
pfree p26
pmul p5, p5, p28, 1
pfree p28
pmodld 1
dload x10, x11, p3, 0, 0, 0
pmul p3, p31, p3
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
dload x10, x11, p20, 0, 1, 32
pntt p3, p20, 4, 0, 0
dload x10, x11, p26, 0, 1, 32
pntt p3, p26, 5, 0, 0
dload x10, x11, p28, 0, 1, 32
pntt p3, p28, 6, 0, 0
pmodld 3
dload x10, x11, p30, 0, 0, 0
pmul p31, p31, p30
pfree p30
pfree p28
dload x10, x11, p30, 0, 1, 32
pmul p31, p31, p30, 1
pfree p30
dload x10, x11, p28, 0, 1, 32
pntt p31, p28, 0, 0, 0
pfree p28
dload x10, x11, p28, 0, 1, 32
pntt p31, p28, 1, 0, 0
pfree p28
dload x10, x11, p28, 0, 1, 32
pntt p31, p28, 2, 0, 0
pfree p28
dload x10, x11, p28, 0, 1, 32
pntt p31, p28, 3, 0, 0
pfree p28
dload x10, x11, p28, 0, 1, 32
pntt p31, p28, 4, 0, 0
pfree p28
dload x10, x11, p28, 0, 1, 32
pntt p31, p28, 5, 0, 0
pfree p28
dload x10, x11, p28, 0, 1, 32
pntt p31, p28, 6, 0, 0
pfree p28
pmodld 1
dload x10, x11, p28, 0, 0, 0
pmac p22, p3, p28
pfree p28
dload x10, x11, p28, 0, 1, 32
pintt p22, p28, 0, 0, 0
pfree p26
dload x10, x11, p30, 0, 1, 32
pintt p22, p30, 1, 0, 0
pfree p20
dload x10, x11, p26, 0, 1, 32
pintt p22, p26, 2, 0, 0
pfree p10
dload x10, x11, p20, 0, 1, 32
pintt p22, p20, 3, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pintt p22, p10, 4, 0, 0
pfree p8
dload x10, x11, p9, 0, 1, 32
pintt p22, p9, 5, 0, 0
pfree p7
dload x10, x11, p8, 0, 1, 32
pintt p22, p8, 6, 0, 0
pfree p6
dload x10, x11, p7, 0, 1, 32
pmul p22, p22, p7, 1
dload x10, x11, p6, 0, 0, 0
pmac p13, p3, p6
pfree p3
pfree p6
pintt p13, p28, 0, 0, 0
pfree p28
pintt p13, p30, 1, 0, 0
pfree p30
pintt p13, p26, 2, 0, 0
pfree p26
pintt p13, p20, 3, 0, 0
pfree p20
pintt p13, p10, 4, 0, 0
pfree p10
pintt p13, p9, 5, 0, 0
pfree p9
pintt p13, p8, 6, 0, 0
pfree p8
pmul p13, p13, p7, 1
pfree p7
pmodld 3
dload x10, x11, p3, 0, 0, 0
pmac p24, p31, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
pmac p12, p31, p3
pfree p31
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p24, p3, 0, 0, 0
pintt p12, p3, 0, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p24, p3, 1, 0, 0
pintt p12, p3, 1, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p24, p3, 2, 0, 0
pintt p12, p3, 2, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p24, p3, 3, 0, 0
pintt p12, p3, 3, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p24, p3, 4, 0, 0
pintt p12, p3, 4, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p24, p3, 5, 0, 0
pintt p12, p3, 5, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pintt p24, p3, 6, 0, 0
pintt p12, p3, 6, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pmul p24, p24, p3, 1
pmul p12, p12, p3, 1
pfree p3
pmodld 0
dload x10, x11, p3, 0, 0, 0
padd p21, p21, p3
padd p5, p5, p3
pfree p3
pmodld 1
dload x10, x11, p3, 0, 0, 0
padd p22, p22, p3
padd p13, p13, p3
pfree p3
pmodld 2
dload x10, x11, p3, 0, 0, 0
padd p23, p23, p3
padd p14, p14, p3
pfree p3
pmodld 3
dload x10, x11, p3, 0, 0, 0
padd p24, p24, p3
padd p12, p12, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
pmul p24, p24, p3
pmul p12, p12, p3
pfree p3
pmodld 0
dload x10, x11, p3, 0, 0, 0
pmul p6, p24, p3
psub p21, p21, p6
pfree p6
pmul p3, p12, p3
psub p5, p5, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
pmul p21, p21, p3
pmul p5, p5, p3
pfree p3
padd p21, p21, p2
pfree p2
padd p0, p0, p5
pfree p5
pmul p21, p21, p11, 1
pmul p0, p0, p11, 1
pfree p11
pntt p21, p15, 0, 0, 0
pntt p0, p15, 0, 0, 0
pfree p15
pntt p21, p16, 1, 0, 0
pntt p0, p16, 1, 0, 0
pfree p16
pntt p21, p17, 2, 0, 0
pntt p0, p17, 2, 0, 0
pfree p17
pntt p21, p18, 3, 0, 0
pntt p0, p18, 3, 0, 0
pfree p18
pntt p21, p19, 4, 0, 0
pntt p0, p19, 4, 0, 0
pfree p19
dload x10, x11, p2, 0, 1, 32
pntt p21, p2, 5, 0, 0
pntt p0, p2, 5, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p21, p2, 6, 0, 0
dstore x10, x11, p21, 1, 0
pntt p0, p2, 6, 0, 0
pfree p2
dstore x10, x11, p0, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p2, p24, p0
psub p22, p22, p2
pfree p2
pmul p0, p12, p0
psub p13, p13, p0
pfree p0
pmodld 2
dload x10, x11, p0, 0, 0, 0
pmul p24, p24, p0
psub p23, p23, p24
pfree p24
pmul p12, p12, p0
pfree p0
psub p14, p14, p12
pfree p12
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p22, p22, p0
pmul p13, p13, p0
pfree p0
padd p22, p22, p27
pfree p27
padd p25, p25, p13
pfree p13
dload x10, x11, p0, 0, 1, 32
pmul p22, p22, p0, 1
pmul p25, p25, p0, 1
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 0, 0, 0
pntt p25, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 1, 0, 0
pntt p25, p0, 1, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 2, 0, 0
pntt p25, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 3, 0, 0
pntt p25, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 4, 0, 0
pntt p25, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 5, 0, 0
pntt p25, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p22, p0, 6, 0, 0
dstore x10, x11, p22, 1, 0
pntt p25, p0, 6, 0, 0
pfree p0
dstore x10, x11, p25, 1, 0
pmodld 2
dload x10, x11, p0, 0, 0, 0
pmul p23, p23, p0
pmul p14, p14, p0
pfree p0
padd p23, p23, p29
pfree p29
padd p1, p1, p14
pfree p14
dload x10, x11, p0, 0, 1, 32
pmul p23, p23, p0, 1
pmul p1, p1, p0, 1
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p23, p0, 0, 0, 0
pntt p1, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p23, p0, 1, 0, 0
pntt p1, p0, 1, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p23, p0, 2, 0, 0
pntt p1, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p23, p0, 3, 0, 0
pntt p1, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p23, p0, 4, 0, 0
pntt p1, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p23, p0, 5, 0, 0
pntt p1, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p23, p0, 6, 0, 0
dstore x10, x11, p23, 1, 0
pntt p1, p0, 6, 0, 0
pfree p0
dstore x10, x11, p1, 1, 0
psync
