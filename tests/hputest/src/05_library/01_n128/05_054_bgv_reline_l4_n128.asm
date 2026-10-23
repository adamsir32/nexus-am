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
pmul p6, p2, 1
pmodld 3
pmul p7, p2, 1
pmodld 4
pmul p2, p2, 1
pmodld 0
dload x10, x11, p8, 0, 0, 0
pmul p0, p0, p8
pmodld 1
dload x10, x11, p9, 0, 1, 32
pmul p5, p5, p9, 1
pntt p5, p3, 0, 0, 0
dload x10, x11, p10, 0, 1, 32
pntt p5, p10, 1, 0, 0
dload x10, x11, p11, 0, 1, 32
pntt p5, p11, 2, 0, 0
dload x10, x11, p12, 0, 1, 32
pntt p5, p12, 3, 0, 0
dload x10, x11, p13, 0, 1, 32
pntt p5, p13, 4, 0, 0
dload x10, x11, p14, 0, 1, 32
pntt p5, p14, 5, 0, 0
dload x10, x11, p15, 0, 1, 32
pntt p5, p15, 6, 0, 0
pmodld 2
dload x10, x11, p16, 0, 1, 32
pmul p6, p6, p16, 1
pntt p6, p3, 0, 0, 0
dload x10, x11, p17, 0, 1, 32
pntt p6, p17, 1, 0, 0
dload x10, x11, p18, 0, 1, 32
pntt p6, p18, 2, 0, 0
dload x10, x11, p19, 0, 1, 32
pntt p6, p19, 3, 0, 0
dload x10, x11, p20, 0, 1, 32
pntt p6, p20, 4, 0, 0
dload x10, x11, p21, 0, 1, 32
pntt p6, p21, 5, 0, 0
pfree p15
dload x10, x11, p22, 0, 1, 32
pntt p6, p22, 6, 0, 0
pmodld 3
pfree p14
dload x10, x11, p15, 0, 1, 32
pmul p7, p7, p15, 1
pntt p7, p3, 0, 0, 0
pfree p13
dload x10, x11, p14, 0, 1, 32
pntt p7, p14, 1, 0, 0
pfree p12
dload x10, x11, p13, 0, 1, 32
pntt p7, p13, 2, 0, 0
pfree p11
dload x10, x11, p12, 0, 1, 32
pntt p7, p12, 3, 0, 0
pfree p10
dload x10, x11, p11, 0, 1, 32
pntt p7, p11, 4, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pntt p7, p10, 5, 0, 0
pfree p10
dload x10, x11, p9, 0, 1, 32
pntt p7, p9, 6, 0, 0
pmodld 4
pfree p9
dload x10, x11, p10, 0, 1, 32
pmul p2, p2, p10, 1
pntt p2, p3, 0, 0, 0
pfree p10
dload x10, x11, p9, 0, 1, 32
pntt p2, p9, 1, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pntt p2, p10, 2, 0, 0
pfree p10
dload x10, x11, p9, 0, 1, 32
pntt p2, p9, 3, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pntt p2, p10, 4, 0, 0
pfree p10
dload x10, x11, p9, 0, 1, 32
pntt p2, p9, 5, 0, 0
pfree p9
dload x10, x11, p10, 0, 1, 32
pntt p2, p10, 6, 0, 0
pmodld 1
dload x10, x11, p9, 0, 0, 0
pmul p23, p5, p9
dload x10, x11, p24, 0, 0, 0
pmul p5, p5, p24
dload x10, x11, p25, 0, 0, 0
pmac p5, p25, p24
dload x10, x11, p26, 0, 0, 0
pintt p26, p3, 0, 0, 0
dload x10, x11, p27, 0, 0, 0
pmac p23, p25, p27
pfree p25
pfree p27
pfree p10
dload x10, x11, p25, 0, 1, 32
pintt p26, p25, 1, 0, 0
pfree p25
dload x10, x11, p10, 0, 1, 32
pintt p26, p10, 2, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pintt p26, p10, 3, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pintt p26, p10, 4, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pintt p26, p10, 5, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pintt p26, p10, 6, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pmul p26, p26, p10, 1
pfree p10
pmodld 0
pmul p10, p26, 1
pmodld 2
pmul p25, p26, 1
pmul p25, p25, p16, 1
pntt p25, p3, 0, 0, 0
pntt p25, p17, 1, 0, 0
pntt p25, p18, 2, 0, 0
pntt p25, p19, 3, 0, 0
pntt p25, p20, 4, 0, 0
pntt p25, p21, 5, 0, 0
pntt p25, p22, 6, 0, 0
pmodld 3
pmul p27, p26, 1
pmul p27, p27, p15, 1
pntt p27, p3, 0, 0, 0
pntt p27, p14, 1, 0, 0
pntt p27, p13, 2, 0, 0
pntt p27, p12, 3, 0, 0
pntt p27, p11, 4, 0, 0
dload x10, x11, p28, 0, 1, 32
pntt p27, p28, 5, 0, 0
pfree p22
dload x10, x11, p29, 0, 1, 32
pntt p27, p29, 6, 0, 0
pmodld 4
pmul p26, p26, 1
pfree p21
dload x10, x11, p22, 0, 1, 32
pmul p26, p26, p22, 1
pntt p26, p3, 0, 0, 0
pfree p20
dload x10, x11, p21, 0, 1, 32
pntt p26, p21, 1, 0, 0
pfree p19
dload x10, x11, p20, 0, 1, 32
pntt p26, p20, 2, 0, 0
pfree p18
dload x10, x11, p19, 0, 1, 32
pntt p26, p19, 3, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p26, p18, 4, 0, 0
pfree p16
dload x10, x11, p17, 0, 1, 32
pntt p26, p17, 5, 0, 0
pfree p17
dload x10, x11, p16, 0, 1, 32
pntt p26, p16, 6, 0, 0
pmodld 0
pfree p16
dload x10, x11, p17, 0, 1, 32
pmul p10, p10, p17, 1
pntt p10, p3, 0, 0, 0
pfree p18
dload x10, x11, p16, 0, 1, 32
pntt p10, p16, 1, 0, 0
pfree p19
dload x10, x11, p18, 0, 1, 32
pntt p10, p18, 2, 0, 0
pfree p20
dload x10, x11, p19, 0, 1, 32
pntt p10, p19, 3, 0, 0
pfree p21
dload x10, x11, p20, 0, 1, 32
pntt p10, p20, 4, 0, 0
pfree p22
dload x10, x11, p21, 0, 1, 32
pntt p10, p21, 5, 0, 0
pfree p29
dload x10, x11, p22, 0, 1, 32
pntt p10, p22, 6, 0, 0
pmac p0, p10, p8
dload x10, x11, p29, 0, 0, 0
pmac p1, p10, p29
pfree p10
pmodld 2
dload x10, x11, p10, 0, 0, 0
pmul p30, p6, p10
pmac p30, p25, p10
dload x10, x11, p31, 0, 0, 0
pmul p6, p6, p31
pmac p6, p25, p31
pfree p25
dload x10, x11, p25, 0, 0, 0
pmac p6, p25, p31
dload x10, x11, p32, 0, 0, 0
pintt p32, p3, 0, 0, 0
dload x10, x11, p33, 0, 0, 0
pmac p30, p25, p33
pfree p25
pfree p33
pfree p28
dload x10, x11, p25, 0, 1, 32
pintt p32, p25, 1, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p32, p25, 2, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p32, p25, 3, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p32, p25, 4, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p32, p25, 5, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pintt p32, p25, 6, 0, 0
pfree p25
dload x10, x11, p25, 0, 1, 32
pmul p32, p32, p25, 1
pfree p25
pmodld 0
pmul p25, p32, 1
pmul p25, p25, p17, 1
pntt p25, p3, 0, 0, 0
pntt p25, p16, 1, 0, 0
pntt p25, p18, 2, 0, 0
pntt p25, p19, 3, 0, 0
pntt p25, p20, 4, 0, 0
pntt p25, p21, 5, 0, 0
pntt p25, p22, 6, 0, 0
pmac p1, p25, p29
pmac p0, p25, p8
pfree p25
pmodld 1
pmul p25, p32, 1
dload x10, x11, p28, 0, 1, 32
pmul p25, p25, p28, 1
pntt p25, p3, 0, 0, 0
pfree p28
dload x10, x11, p33, 0, 1, 32
pntt p25, p33, 1, 0, 0
pfree p33
dload x10, x11, p28, 0, 1, 32
pntt p25, p28, 2, 0, 0
pfree p28
dload x10, x11, p33, 0, 1, 32
pntt p25, p33, 3, 0, 0
pfree p33
dload x10, x11, p28, 0, 1, 32
pntt p25, p28, 4, 0, 0
pfree p28
dload x10, x11, p33, 0, 1, 32
pntt p25, p33, 5, 0, 0
pfree p33
dload x10, x11, p28, 0, 1, 32
pntt p25, p28, 6, 0, 0
pmac p23, p25, p9
pmac p5, p25, p24
pfree p25
pmodld 3
pmul p25, p32, 1
pmul p25, p25, p15, 1
pntt p25, p3, 0, 0, 0
pntt p25, p14, 1, 0, 0
pntt p25, p13, 2, 0, 0
pntt p25, p12, 3, 0, 0
pntt p25, p11, 4, 0, 0
pfree p11
dload x10, x11, p33, 0, 1, 32
pntt p25, p33, 5, 0, 0
pfree p33
dload x10, x11, p11, 0, 1, 32
pntt p25, p11, 6, 0, 0
pmodld 4
pmul p32, p32, 1
pfree p11
dload x10, x11, p33, 0, 1, 32
pmul p32, p32, p33, 1
pntt p32, p3, 0, 0, 0
pfree p12
dload x10, x11, p11, 0, 1, 32
pntt p32, p11, 1, 0, 0
pfree p13
dload x10, x11, p12, 0, 1, 32
pntt p32, p12, 2, 0, 0
pfree p14
dload x10, x11, p13, 0, 1, 32
pntt p32, p13, 3, 0, 0
pfree p15
dload x10, x11, p14, 0, 1, 32
pntt p32, p14, 4, 0, 0
pfree p14
dload x10, x11, p15, 0, 1, 32
pntt p32, p15, 5, 0, 0
pfree p15
dload x10, x11, p14, 0, 1, 32
pntt p32, p14, 6, 0, 0
pmodld 3
dload x10, x11, p15, 0, 0, 0
pmul p34, p7, p15
pmac p34, p27, p15
pmac p34, p25, p15
pfree p15
dload x10, x11, p15, 0, 0, 0
pmul p7, p7, p15
pmac p7, p27, p15
pfree p27
pmac p7, p25, p15
pfree p25
dload x10, x11, p25, 0, 0, 0
pmac p7, p25, p15
pfree p15
dload x10, x11, p15, 0, 0, 0
pintt p15, p3, 0, 0, 0
dload x10, x11, p27, 0, 0, 0
pmac p34, p25, p27
pfree p25
pfree p27
pfree p14
dload x10, x11, p25, 0, 1, 32
pintt p15, p25, 1, 0, 0
pfree p25
dload x10, x11, p14, 0, 1, 32
pintt p15, p14, 2, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p15, p14, 3, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p15, p14, 4, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p15, p14, 5, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pintt p15, p14, 6, 0, 0
pfree p14
dload x10, x11, p14, 0, 1, 32
pmul p15, p15, p14, 1
pfree p14
pmodld 0
pmul p14, p15, 1
pmul p14, p14, p17, 1
pntt p14, p3, 0, 0, 0
pntt p14, p16, 1, 0, 0
pntt p14, p18, 2, 0, 0
pntt p14, p19, 3, 0, 0
pntt p14, p20, 4, 0, 0
pntt p14, p21, 5, 0, 0
pntt p14, p22, 6, 0, 0
pmac p1, p14, p29
pfree p29
pmac p0, p14, p8
pfree p14
pfree p8
pmodld 1
pmul p8, p15, 1
dload x10, x11, p14, 0, 1, 32
pmul p8, p8, p14, 1
pntt p8, p3, 0, 0, 0
pfree p14
dload x10, x11, p25, 0, 1, 32
pntt p8, p25, 1, 0, 0
pfree p25
dload x10, x11, p14, 0, 1, 32
pntt p8, p14, 2, 0, 0
pfree p14
dload x10, x11, p25, 0, 1, 32
pntt p8, p25, 3, 0, 0
pfree p25
dload x10, x11, p14, 0, 1, 32
pntt p8, p14, 4, 0, 0
pfree p14
dload x10, x11, p25, 0, 1, 32
pntt p8, p25, 5, 0, 0
pntt p8, p28, 6, 0, 0
pmac p23, p8, p9
pfree p9
pmac p5, p8, p24
pfree p8
pfree p24
pmodld 2
pmul p8, p15, 1
pfree p28
dload x10, x11, p9, 0, 1, 32
pmul p8, p8, p9, 1
pntt p8, p3, 0, 0, 0
pfree p9
dload x10, x11, p14, 0, 1, 32
pntt p8, p14, 1, 0, 0
pfree p14
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 2, 0, 0
pfree p9
dload x10, x11, p14, 0, 1, 32
pntt p8, p14, 3, 0, 0
pfree p14
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 4, 0, 0
pfree p9
dload x10, x11, p14, 0, 1, 32
pntt p8, p14, 5, 0, 0
pfree p14
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 6, 0, 0
pmac p30, p8, p10
pfree p10
pmac p6, p8, p31
pfree p8
pfree p31
pmodld 4
pmul p15, p15, 1
pmul p15, p15, p33, 1
pfree p33
pntt p15, p3, 0, 0, 0
pntt p15, p11, 1, 0, 0
pfree p11
pntt p15, p12, 2, 0, 0
pfree p12
pntt p15, p13, 3, 0, 0
pfree p13
dload x10, x11, p8, 0, 1, 32
pntt p15, p8, 4, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pntt p15, p8, 5, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pntt p15, p8, 6, 0, 0
pfree p8
dload x10, x11, p8, 0, 0, 0
pmul p10, p2, p8
pmac p10, p26, p8
pmac p10, p32, p8
pmac p10, p15, p8
pfree p8
pintt p10, p3, 0, 0, 0
dload x10, x11, p8, 0, 0, 0
pmul p2, p2, p8
pmac p2, p26, p8
pfree p26
pmac p2, p32, p8
pfree p32
pmac p2, p15, p8
pfree p15
pfree p8
pintt p2, p3, 0, 0, 0
dload x10, x11, p8, 0, 1, 32
pintt p10, p8, 1, 0, 0
pintt p2, p8, 1, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p10, p8, 2, 0, 0
pintt p2, p8, 2, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p10, p8, 3, 0, 0
pintt p2, p8, 3, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p10, p8, 4, 0, 0
pintt p2, p8, 4, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p10, p8, 5, 0, 0
pintt p2, p8, 5, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pintt p10, p8, 6, 0, 0
pintt p2, p8, 6, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pmul p10, p10, p8, 1
pmul p2, p2, p8, 1
pfree p8
pmodld 0
pmul p8, p10, 1
pmodld 1
pmul p11, p10, 1
pmodld 2
pmul p12, p10, 1
pmodld 3
pmul p13, p10, 1
pmodld 0
pmul p14, p2, 1
pmodld 1
pmul p15, p2, 1
pmodld 2
pmul p24, p2, 1
pmodld 3
pmul p26, p2, 1
pmodld 5
dload x10, x11, p27, 0, 0, 0
pmul p10, p10, p27
pmul p2, p2, p27
pfree p27
pmodld 0
dload x10, x11, p27, 0, 0, 0
pmul p28, p10, p27
padd p28, p28, p8
pfree p8
pmul p28, p28, p17, 1
pntt p28, p3, 0, 0, 0
pntt p28, p16, 1, 0, 0
pntt p28, p18, 2, 0, 0
pntt p28, p19, 3, 0, 0
pntt p28, p20, 4, 0, 0
pntt p28, p21, 5, 0, 0
pntt p28, p22, 6, 0, 0
psub p1, p1, p28
pfree p28
pmodld 1
pmul p8, p10, p27
padd p8, p8, p11
pfree p11
dload x10, x11, p11, 0, 1, 32
pmul p8, p8, p11, 1
pntt p8, p3, 0, 0, 0
dload x10, x11, p28, 0, 1, 32
pntt p8, p28, 1, 0, 0
dload x10, x11, p29, 0, 1, 32
pntt p8, p29, 2, 0, 0
dload x10, x11, p31, 0, 1, 32
pntt p8, p31, 3, 0, 0
pfree p9
dload x10, x11, p32, 0, 1, 32
pntt p8, p32, 4, 0, 0
pntt p8, p25, 5, 0, 0
pfree p25
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 6, 0, 0
psub p23, p23, p8
pfree p8
pmodld 3
pmul p8, p10, p27
padd p8, p8, p13
pfree p13
pfree p9
dload x10, x11, p13, 0, 1, 32
pmul p8, p8, p13, 1
pntt p8, p3, 0, 0, 0
pfree p13
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 1, 0, 0
pfree p9
dload x10, x11, p13, 0, 1, 32
pntt p8, p13, 2, 0, 0
pfree p13
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 3, 0, 0
pfree p9
dload x10, x11, p13, 0, 1, 32
pntt p8, p13, 4, 0, 0
pfree p13
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 5, 0, 0
pfree p9
dload x10, x11, p13, 0, 1, 32
pntt p8, p13, 6, 0, 0
psub p34, p34, p8
pfree p8
pmodld 0
pmul p8, p2, p27
padd p8, p8, p14
pfree p14
pmul p8, p8, p17, 1
pfree p17
pntt p8, p3, 0, 0, 0
pntt p8, p16, 1, 0, 0
pfree p16
pntt p8, p18, 2, 0, 0
pfree p18
pntt p8, p19, 3, 0, 0
pfree p19
pntt p8, p20, 4, 0, 0
pfree p20
pntt p8, p21, 5, 0, 0
pfree p21
pntt p8, p22, 6, 0, 0
pfree p22
psub p0, p0, p8
pfree p8
pmodld 1
pmul p8, p2, p27
padd p8, p8, p15
pfree p15
pmul p8, p8, p11, 1
pfree p11
pntt p8, p3, 0, 0, 0
pntt p8, p28, 1, 0, 0
pfree p28
pntt p8, p29, 2, 0, 0
pfree p29
pntt p8, p31, 3, 0, 0
pfree p31
pntt p8, p32, 4, 0, 0
pfree p32
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 5, 0, 0
pfree p9
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 6, 0, 0
pfree p9
psub p5, p5, p8
pfree p8
pmodld 3
pmul p27, p2, p27
padd p27, p27, p26
pfree p26
dload x10, x11, p8, 0, 1, 32
pmul p27, p27, p8, 1
pfree p8
pntt p27, p3, 0, 0, 0
dload x10, x11, p8, 0, 1, 32
pntt p27, p8, 1, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pntt p27, p8, 2, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pntt p27, p8, 3, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pntt p27, p8, 4, 0, 0
pfree p8
dload x10, x11, p8, 0, 1, 32
pntt p27, p8, 5, 0, 0
pfree p8
pntt p27, p13, 6, 0, 0
pfree p13
psub p7, p7, p27
pfree p27
pmodld 0
dload x10, x11, p8, 0, 0, 0
pmul p1, p1, p8
pmul p0, p0, p8
pfree p8
dload x10, x11, p8, 0, 0, 0
padd p1, p1, p8
pfree p8
dstore x10, x11, p1, 1, 0
dload x10, x11, p1, 0, 0, 0
padd p0, p0, p1
pfree p1
dstore x10, x11, p0, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p23, p23, p0
pmul p5, p5, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
padd p23, p23, p0
pfree p0
dstore x10, x11, p23, 1, 0
dload x10, x11, p0, 0, 0, 0
padd p5, p5, p0
pfree p0
dstore x10, x11, p5, 1, 0
pmodld 2
dload x10, x11, p0, 0, 0, 0
pmul p10, p10, p0
padd p10, p10, p12
pfree p12
pmul p2, p2, p0
pfree p0
padd p2, p2, p24
pfree p24
dload x10, x11, p0, 0, 1, 32
pmul p10, p10, p0, 1
pmul p2, p2, p0, 1
pfree p0
pntt p10, p3, 0, 0, 0
pntt p2, p3, 0, 0, 0
pfree p3
dload x10, x11, p0, 0, 1, 32
pntt p10, p0, 1, 0, 0
pntt p2, p0, 1, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p10, p0, 2, 0, 0
pntt p2, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p10, p0, 3, 0, 0
pntt p2, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p10, p0, 4, 0, 0
pntt p2, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p10, p0, 5, 0, 0
pntt p2, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p10, p0, 6, 0, 0
psub p30, p30, p10
pfree p10
pntt p2, p0, 6, 0, 0
pfree p0
psub p6, p6, p2
pfree p2
dload x10, x11, p0, 0, 0, 0
pmul p30, p30, p0
pmul p6, p6, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
padd p30, p30, p0
pfree p0
dstore x10, x11, p30, 1, 0
dload x10, x11, p0, 0, 0, 0
padd p6, p6, p0
pfree p0
dstore x10, x11, p6, 1, 0
pmodld 3
dload x10, x11, p0, 0, 0, 0
pmul p34, p34, p0
pmul p7, p7, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
padd p34, p34, p0
pfree p0
dstore x10, x11, p34, 1, 0
dload x10, x11, p0, 0, 0, 0
padd p7, p7, p0
pfree p0
dstore x10, x11, p7, 1, 0
psync
