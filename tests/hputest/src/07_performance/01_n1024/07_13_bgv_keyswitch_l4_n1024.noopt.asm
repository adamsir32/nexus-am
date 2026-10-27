dload x10, x11, p4, 1, 0, 32
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 1, 32
dload x10, x11, p2, 0, 1, 32
dload x10, x11, p3, 0, 1, 32
dload x10, x11, p5, 0, 1, 32
dload x10, x11, p6, 0, 1, 32
dload x10, x11, p7, 0, 1, 32
dload x10, x11, p8, 0, 1, 32
dload x10, x11, p9, 0, 1, 32
dload x10, x11, p10, 0, 1, 32
dload x10, x11, p11, 0, 1, 32
dload x10, x11, p12, 0, 1, 32
dload x10, x11, p13, 0, 0, 0
dload x10, x11, p14, 0, 0, 0
dload x10, x11, p15, 0, 0, 0
dload x10, x11, p16, 0, 1, 32
dload x10, x11, p17, 0, 0, 0
dload x10, x11, p18, 0, 0, 0
dload x10, x11, p19, 0, 0, 0
dload x10, x11, p20, 0, 0, 0
dload x10, x11, p21, 0, 0, 0
dload x10, x11, p22, 0, 0, 0
dload x10, x11, p23, 0, 0, 0
dload x10, x11, p24, 0, 0, 0
pmodld 0
psync
pintt p0, p1, 0, 0, 0
pfree p1
pintt p0, p2, 1, 0, 0
pfree p2
pintt p0, p3, 2, 0, 0
pfree p3
pintt p0, p5, 3, 0, 0
pfree p5
pintt p0, p6, 4, 0, 0
pfree p6
pintt p0, p7, 5, 0, 0
pfree p7
pintt p0, p8, 6, 0, 0
pfree p8
pintt p0, p9, 7, 0, 0
pfree p9
pintt p0, p10, 8, 0, 0
pfree p10
pintt p0, p11, 9, 0, 0
pfree p11
pmul p0, p0, p12, 1
pfree p12
dstore x10, x11, p0, 1, 0
pmul p14, p13, p14
dstore x10, x11, p14, 0, 0
pmul p13, p13, p15
pfree p15
dstore x10, x11, p13, 0, 0
dload x10, x11, p0, 0, 0, 0
pmodld 1
pmul p0, p0, 1
pmul p0, p0, p16, 1
pfree p16
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 0, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 1, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 2, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 3, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 4, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 5, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 6, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 7, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 8, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 9, 0, 0
pfree p1
pmul p17, p0, p17
dstore x10, x11, p17, 0, 0
pmul p0, p0, p18
pfree p18
dstore x10, x11, p0, 0, 0
dload x10, x11, p1, 0, 0, 0
pmodld 2
pmul p1, p1, 1
dload x10, x11, p2, 0, 1, 32
pmul p1, p1, p2, 1
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 0, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 1, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 2, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 3, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 4, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 5, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 6, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 7, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 8, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p1, p2, 9, 0, 0
pfree p2
pmul p19, p1, p19
dstore x10, x11, p19, 0, 0
pmul p1, p1, p20
pfree p20
dstore x10, x11, p1, 0, 0
dload x10, x11, p2, 0, 0, 0
pmodld 3
pmul p2, p2, 1
dload x10, x11, p3, 0, 1, 32
pmul p2, p2, p3, 1
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 0, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 1, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 2, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 3, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 4, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 5, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 6, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 7, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 8, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 9, 0, 0
pfree p3
pmul p21, p2, p21
dstore x10, x11, p21, 0, 0
pmul p2, p2, p22
pfree p22
dstore x10, x11, p2, 0, 0
dload x10, x11, p3, 0, 0, 0
pmodld 4
pmul p3, p3, 1
dload x10, x11, p5, 0, 1, 32
pmul p3, p3, p5, 1
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 0, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 1, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 2, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 3, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 4, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 5, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 6, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 7, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 8, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 9, 0, 0
pfree p5
pmul p23, p3, p23
dstore x10, x11, p23, 0, 0
pmul p3, p3, p24
pfree p24
dstore x10, x11, p3, 0, 0
pmodld 1
dload x10, x11, p5, 0, 0, 0
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 0, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 1, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 2, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 3, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 4, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 5, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 6, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 7, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 8, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pintt p5, p6, 9, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pmul p5, p5, p6, 1
pfree p6
dstore x10, x11, p5, 1, 0
dload x10, x11, p5, 0, 0, 0
pmodld 0
pmul p5, p5, 1
dload x10, x11, p6, 0, 1, 32
pmul p5, p5, p6, 1
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 0, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 1, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 2, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 3, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 4, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 5, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 6, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 7, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 8, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 9, 0, 0
pfree p6
pfree p14
dload x10, x11, p6, 0, 0, 0
dload x10, x11, p7, 0, 0, 0
pmac p6, p5, p7
pfree p7
dstore x10, x11, p6, 0, 0
pfree p13
dload x10, x11, p7, 0, 0, 0
dload x10, x11, p8, 0, 0, 0
pmac p7, p5, p8
pfree p5
pfree p8
dstore x10, x11, p7, 0, 0
pfree p17
dload x10, x11, p5, 0, 0, 0
pmodld 1
dload x10, x11, p8, 0, 0, 0
dload x10, x11, p9, 0, 0, 0
pmac p5, p8, p9
pfree p9
dstore x10, x11, p5, 0, 0
pfree p0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p9, 0, 0, 0
pmac p0, p8, p9
pfree p8
pfree p9
dstore x10, x11, p0, 0, 0
dload x10, x11, p8, 0, 0, 0
pmodld 2
pmul p8, p8, 1
dload x10, x11, p9, 0, 1, 32
pmul p8, p8, p9, 1
pfree p9
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 0, 0, 0
pfree p9
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 1, 0, 0
pfree p9
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 2, 0, 0
pfree p9
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 3, 0, 0
pfree p9
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 4, 0, 0
pfree p9
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 5, 0, 0
pfree p9
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 6, 0, 0
pfree p9
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 7, 0, 0
pfree p9
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 8, 0, 0
pfree p9
dload x10, x11, p9, 0, 1, 32
pntt p8, p9, 9, 0, 0
pfree p9
pfree p19
dload x10, x11, p9, 0, 0, 0
dload x10, x11, p10, 0, 0, 0
pmac p9, p8, p10
pfree p10
dstore x10, x11, p9, 0, 0
pfree p1
dload x10, x11, p1, 0, 0, 0
dload x10, x11, p10, 0, 0, 0
pmac p1, p8, p10
pfree p8
pfree p10
dstore x10, x11, p1, 0, 0
dload x10, x11, p8, 0, 0, 0
pmodld 3
pmul p8, p8, 1
dload x10, x11, p10, 0, 1, 32
pmul p8, p8, p10, 1
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p8, p10, 0, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p8, p10, 1, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p8, p10, 2, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p8, p10, 3, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p8, p10, 4, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p8, p10, 5, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p8, p10, 6, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p8, p10, 7, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p8, p10, 8, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p8, p10, 9, 0, 0
pfree p10
pfree p21
dload x10, x11, p10, 0, 0, 0
dload x10, x11, p11, 0, 0, 0
pmac p10, p8, p11
pfree p11
dstore x10, x11, p10, 0, 0
pfree p2
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p11, 0, 0, 0
pmac p2, p8, p11
pfree p8
pfree p11
dstore x10, x11, p2, 0, 0
dload x10, x11, p8, 0, 0, 0
pmodld 4
pmul p8, p8, 1
dload x10, x11, p11, 0, 1, 32
pmul p8, p8, p11, 1
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p8, p11, 0, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p8, p11, 1, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p8, p11, 2, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p8, p11, 3, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p8, p11, 4, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p8, p11, 5, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p8, p11, 6, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p8, p11, 7, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p8, p11, 8, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p8, p11, 9, 0, 0
pfree p11
pfree p23
dload x10, x11, p11, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p11, p8, p12
pfree p12
dstore x10, x11, p11, 0, 0
pfree p3
dload x10, x11, p3, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p3, p8, p12
pfree p8
pfree p12
dstore x10, x11, p3, 0, 0
pmodld 2
dload x10, x11, p8, 0, 0, 0
dload x10, x11, p12, 0, 1, 32
pintt p8, p12, 0, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p8, p12, 1, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p8, p12, 2, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p8, p12, 3, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p8, p12, 4, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p8, p12, 5, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p8, p12, 6, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p8, p12, 7, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p8, p12, 8, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p8, p12, 9, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pmul p8, p8, p12, 1
pfree p12
dstore x10, x11, p8, 1, 0
dload x10, x11, p8, 0, 0, 0
pmodld 0
pmul p8, p8, 1
dload x10, x11, p12, 0, 1, 32
pmul p8, p8, p12, 1
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 0, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 1, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 2, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 3, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 4, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 5, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 6, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 7, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 8, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 9, 0, 0
pfree p12
pfree p6
dload x10, x11, p6, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p6, p8, p12
pfree p12
dstore x10, x11, p6, 0, 0
pfree p7
dload x10, x11, p7, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p7, p8, p12
pfree p8
pfree p12
dstore x10, x11, p7, 0, 0
dload x10, x11, p8, 0, 0, 0
pmodld 1
pmul p8, p8, 1
dload x10, x11, p12, 0, 1, 32
pmul p8, p8, p12, 1
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 0, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 1, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 2, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 3, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 4, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 5, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 6, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 7, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 8, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p8, p12, 9, 0, 0
pfree p12
pfree p5
dload x10, x11, p5, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p5, p8, p12
pfree p12
dstore x10, x11, p5, 0, 0
pfree p0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p0, p8, p12
pfree p8
pfree p12
dstore x10, x11, p0, 0, 0
pfree p9
dload x10, x11, p8, 0, 0, 0
pmodld 2
dload x10, x11, p9, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p8, p9, p12
pfree p12
dstore x10, x11, p8, 0, 0
pfree p1
dload x10, x11, p1, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p1, p9, p12
pfree p9
pfree p12
dstore x10, x11, p1, 0, 0
dload x10, x11, p9, 0, 0, 0
pmodld 3
pmul p9, p9, 1
dload x10, x11, p12, 0, 1, 32
pmul p9, p9, p12, 1
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 0, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 1, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 2, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 3, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 4, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 5, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 6, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 7, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 8, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 9, 0, 0
pfree p12
pfree p10
dload x10, x11, p10, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p10, p9, p12
pfree p12
dstore x10, x11, p10, 0, 0
pfree p2
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p2, p9, p12
pfree p9
pfree p12
dstore x10, x11, p2, 0, 0
dload x10, x11, p9, 0, 0, 0
pmodld 4
pmul p9, p9, 1
dload x10, x11, p12, 0, 1, 32
pmul p9, p9, p12, 1
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 0, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 1, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 2, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 3, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 4, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 5, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 6, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 7, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 8, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 9, 0, 0
pfree p12
pfree p11
dload x10, x11, p11, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p11, p9, p12
pfree p12
dstore x10, x11, p11, 0, 0
pfree p3
dload x10, x11, p3, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p3, p9, p12
pfree p9
pfree p12
dstore x10, x11, p3, 0, 0
pmodld 3
dload x10, x11, p9, 0, 0, 0
dload x10, x11, p12, 0, 1, 32
pintt p9, p12, 0, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p9, p12, 1, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p9, p12, 2, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p9, p12, 3, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p9, p12, 4, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p9, p12, 5, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p9, p12, 6, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p9, p12, 7, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p9, p12, 8, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pintt p9, p12, 9, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pmul p9, p9, p12, 1
pfree p12
dstore x10, x11, p9, 1, 0
dload x10, x11, p9, 0, 0, 0
pmodld 0
pmul p9, p9, 1
dload x10, x11, p12, 0, 1, 32
pmul p9, p9, p12, 1
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 0, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 1, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 2, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 3, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 4, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 5, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 6, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 7, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 8, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 9, 0, 0
pfree p12
pfree p6
dload x10, x11, p6, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p6, p9, p12
pfree p12
dstore x10, x11, p6, 0, 0
pfree p7
dload x10, x11, p7, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p7, p9, p12
pfree p9
pfree p12
dstore x10, x11, p7, 0, 0
dload x10, x11, p9, 0, 0, 0
pmodld 1
pmul p9, p9, 1
dload x10, x11, p12, 0, 1, 32
pmul p9, p9, p12, 1
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 0, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 1, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 2, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 3, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 4, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 5, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 6, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 7, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 8, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 9, 0, 0
pfree p12
pfree p5
dload x10, x11, p5, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p5, p9, p12
pfree p12
dstore x10, x11, p5, 0, 0
pfree p0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p0, p9, p12
pfree p9
pfree p12
dstore x10, x11, p0, 0, 0
dload x10, x11, p9, 0, 0, 0
pmodld 2
pmul p9, p9, 1
dload x10, x11, p12, 0, 1, 32
pmul p9, p9, p12, 1
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 0, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 1, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 2, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 3, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 4, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 5, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 6, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 7, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 8, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p9, p12, 9, 0, 0
pfree p12
pfree p8
dload x10, x11, p8, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p8, p9, p12
pfree p12
dstore x10, x11, p8, 0, 0
pfree p1
dload x10, x11, p1, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p1, p9, p12
pfree p9
pfree p12
dstore x10, x11, p1, 0, 0
pfree p10
dload x10, x11, p9, 0, 0, 0
pmodld 3
dload x10, x11, p10, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p9, p10, p12
pfree p12
dstore x10, x11, p9, 0, 0
pfree p2
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p2, p10, p12
pfree p10
pfree p12
dstore x10, x11, p2, 0, 0
dload x10, x11, p10, 0, 0, 0
pmodld 4
pmul p10, p10, 1
dload x10, x11, p12, 0, 1, 32
pmul p10, p10, p12, 1
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p10, p12, 0, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p10, p12, 1, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p10, p12, 2, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p10, p12, 3, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p10, p12, 4, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p10, p12, 5, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p10, p12, 6, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p10, p12, 7, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p10, p12, 8, 0, 0
pfree p12
dload x10, x11, p12, 0, 1, 32
pntt p10, p12, 9, 0, 0
pfree p12
pfree p11
dload x10, x11, p11, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p11, p10, p12
pfree p12
dstore x10, x11, p11, 0, 0
pfree p3
dload x10, x11, p3, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
pmac p3, p10, p12
pfree p10
pfree p12
dstore x10, x11, p3, 0, 0
pfree p11
dload x10, x11, p10, 0, 0, 0
dload x10, x11, p11, 0, 1, 32
pintt p10, p11, 0, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p10, p11, 1, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p10, p11, 2, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p10, p11, 3, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p10, p11, 4, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p10, p11, 5, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p10, p11, 6, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p10, p11, 7, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p10, p11, 8, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pintt p10, p11, 9, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pmul p10, p10, p11, 1
pfree p11
dstore x10, x11, p10, 1, 0
dload x10, x11, p10, 0, 0, 0
pmodld 5
dload x10, x11, p11, 0, 0, 0
pmul p10, p10, p11
pfree p11
dstore x10, x11, p10, 1, 0
dload x10, x11, p10, 0, 0, 0
pmodld 0
dload x10, x11, p11, 0, 0, 0
pmul p10, p10, p11
pfree p11
dload x10, x11, p11, 0, 0, 0
pmul p11, p11, 1
padd p10, p10, p11
pfree p11
dload x10, x11, p11, 0, 1, 32
pmul p10, p10, p11, 1
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p10, p11, 0, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p10, p11, 1, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p10, p11, 2, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p10, p11, 3, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p10, p11, 4, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p10, p11, 5, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p10, p11, 6, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p10, p11, 7, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p10, p11, 8, 0, 0
pfree p11
dload x10, x11, p11, 0, 1, 32
pntt p10, p11, 9, 0, 0
pfree p11
pfree p6
dload x10, x11, p6, 0, 0, 0
psub p6, p6, p10
pfree p10
dload x10, x11, p10, 0, 0, 0
pmul p6, p6, p10
pfree p10
dload x10, x11, p10, 0, 0, 0
padd p6, p6, p10
pfree p10
dstore x10, x11, p6, 1, 0
dload x10, x11, p6, 0, 0, 0
pmodld 1
dload x10, x11, p10, 0, 0, 0
pmul p6, p6, p10
pfree p10
dload x10, x11, p10, 0, 0, 0
pmul p10, p10, 1
padd p6, p6, p10
pfree p10
dload x10, x11, p10, 0, 1, 32
pmul p6, p6, p10, 1
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p6, p10, 0, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p6, p10, 1, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p6, p10, 2, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p6, p10, 3, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p6, p10, 4, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p6, p10, 5, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p6, p10, 6, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p6, p10, 7, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p6, p10, 8, 0, 0
pfree p10
dload x10, x11, p10, 0, 1, 32
pntt p6, p10, 9, 0, 0
pfree p10
pfree p5
dload x10, x11, p5, 0, 0, 0
psub p5, p5, p6
pfree p6
dload x10, x11, p6, 0, 0, 0
pmul p5, p5, p6
pfree p6
dload x10, x11, p6, 0, 0, 0
padd p5, p5, p6
pfree p6
dstore x10, x11, p5, 1, 0
dload x10, x11, p5, 0, 0, 0
pmodld 2
dload x10, x11, p6, 0, 0, 0
pmul p5, p5, p6
pfree p6
dload x10, x11, p6, 0, 0, 0
pmul p6, p6, 1
padd p5, p5, p6
pfree p6
dload x10, x11, p6, 0, 1, 32
pmul p5, p5, p6, 1
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 0, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 1, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 2, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 3, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 4, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 5, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 6, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 7, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 8, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 9, 0, 0
pfree p6
pfree p8
dload x10, x11, p6, 0, 0, 0
psub p6, p6, p5
pfree p5
dload x10, x11, p5, 0, 0, 0
pmul p6, p6, p5
pfree p5
dload x10, x11, p5, 0, 0, 0
padd p6, p6, p5
pfree p5
dstore x10, x11, p6, 1, 0
dload x10, x11, p5, 0, 0, 0
pmodld 3
dload x10, x11, p6, 0, 0, 0
pmul p5, p5, p6
pfree p6
dload x10, x11, p6, 0, 0, 0
pmul p6, p6, 1
padd p5, p5, p6
pfree p6
dload x10, x11, p6, 0, 1, 32
pmul p5, p5, p6, 1
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 0, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 1, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 2, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 3, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 4, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 5, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 6, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 7, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 8, 0, 0
pfree p6
dload x10, x11, p6, 0, 1, 32
pntt p5, p6, 9, 0, 0
pfree p6
pfree p9
dload x10, x11, p6, 0, 0, 0
psub p6, p6, p5
pfree p5
dload x10, x11, p5, 0, 0, 0
pmul p6, p6, p5
pfree p5
dload x10, x11, p5, 0, 0, 0
padd p6, p6, p5
pfree p5
dstore x10, x11, p6, 1, 0
pfree p3
dload x10, x11, p3, 0, 0, 0
pmodld 4
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 0, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 1, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 2, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 3, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 4, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 5, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 6, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 7, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 8, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 9, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pmul p3, p3, p5, 1
pfree p5
dstore x10, x11, p3, 1, 0
dload x10, x11, p3, 0, 0, 0
pmodld 5
dload x10, x11, p5, 0, 0, 0
pmul p3, p3, p5
pfree p5
dstore x10, x11, p3, 1, 0
dload x10, x11, p3, 0, 0, 0
pmodld 0
dload x10, x11, p5, 0, 0, 0
pmul p3, p3, p5
pfree p5
dload x10, x11, p5, 0, 0, 0
pmul p5, p5, 1
padd p3, p3, p5
pfree p5
dload x10, x11, p5, 0, 1, 32
pmul p3, p3, p5, 1
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 0, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 1, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 2, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 3, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 4, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 5, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 6, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 7, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 8, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 9, 0, 0
pfree p5
pfree p7
dload x10, x11, p5, 0, 0, 0
psub p5, p5, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
pmul p5, p5, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
padd p5, p5, p3
pfree p3
dstore x10, x11, p5, 1, 0
dload x10, x11, p3, 0, 0, 0
pmodld 1
dload x10, x11, p5, 0, 0, 0
pmul p3, p3, p5
pfree p5
dload x10, x11, p5, 0, 0, 0
pmul p5, p5, 1
padd p3, p3, p5
pfree p5
dload x10, x11, p5, 0, 1, 32
pmul p3, p3, p5, 1
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 0, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 1, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 2, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 3, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 4, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 5, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 6, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 7, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 8, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pntt p3, p5, 9, 0, 0
pfree p5
pfree p0
dload x10, x11, p0, 0, 0, 0
psub p0, p0, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
pmul p0, p0, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
padd p0, p0, p3
pfree p3
dstore x10, x11, p0, 1, 0
dload x10, x11, p0, 0, 0, 0
pmodld 2
dload x10, x11, p3, 0, 0, 0
pmul p0, p0, p3
pfree p3
dload x10, x11, p3, 0, 0, 0
pmul p3, p3, 1
padd p0, p0, p3
pfree p3
dload x10, x11, p3, 0, 1, 32
pmul p0, p0, p3, 1
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 0, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 1, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 2, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 3, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 4, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 5, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 6, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 7, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 8, 0, 0
pfree p3
dload x10, x11, p3, 0, 1, 32
pntt p0, p3, 9, 0, 0
pfree p3
pfree p1
dload x10, x11, p1, 0, 0, 0
psub p1, p1, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
pmul p1, p1, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
padd p1, p1, p0
pfree p0
dstore x10, x11, p1, 1, 0
dload x10, x11, p0, 0, 0, 0
pmodld 3
dload x10, x11, p1, 0, 0, 0
pmul p0, p0, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmul p1, p1, 1
padd p0, p0, p1
pfree p1
dload x10, x11, p1, 0, 1, 32
pmul p0, p0, p1, 1
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 0, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 1, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 2, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 3, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 4, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 5, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 6, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 7, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 8, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 9, 0, 0
pfree p1
pfree p2
dload x10, x11, p1, 0, 0, 0
psub p1, p1, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
pmul p1, p1, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
padd p1, p1, p0
psync
pfree p0
dstore x10, x11, p1, 1, 0
psync
