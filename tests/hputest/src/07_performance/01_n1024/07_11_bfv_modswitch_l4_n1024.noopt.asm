dload x10, x11, p4, 1, 0, 32
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p3, 0, 0, 0
dload x10, x11, p5, 0, 0, 0
dload x10, x11, p6, 0, 0, 0
dload x10, x11, p7, 0, 0, 0
dload x10, x11, p8, 0, 0, 0
dload x10, x11, p9, 0, 0, 0
dload x10, x11, p10, 0, 0, 0
dload x10, x11, p11, 0, 0, 0
dload x10, x11, p12, 0, 0, 0
dload x10, x11, p13, 0, 0, 0
dload x10, x11, p14, 0, 0, 0
dload x10, x11, p15, 0, 0, 0
dload x10, x11, p16, 0, 0, 0
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
padd p0, p0, p1
pfree p1
dstore x10, x11, p0, 0, 0
pmodld 1
padd p2, p2, p3
pfree p3
dstore x10, x11, p2, 0, 0
pmodld 2
padd p5, p5, p6
pfree p6
dstore x10, x11, p5, 0, 0
pmodld 3
padd p7, p7, p8
pfree p8
dstore x10, x11, p7, 0, 0
pfree p7
dload x10, x11, p1, 0, 0, 0
pmul p1, p1, p9
pfree p9
dstore x10, x11, p1, 1, 0
dload x10, x11, p1, 0, 0, 0
pmodld 0
pmul p1, p1, p10
pfree p10
dstore x10, x11, p1, 0, 0
dload x10, x11, p3, 0, 0, 0
pmodld 1
pmul p3, p3, p11
pfree p11
dstore x10, x11, p3, 0, 0
dload x10, x11, p6, 0, 0, 0
pmodld 2
pmul p6, p6, p12
pfree p12
dstore x10, x11, p6, 0, 0
pfree p0
dload x10, x11, p0, 0, 0, 0
pfree p1
dload x10, x11, p1, 0, 0, 0
pmodld 0
psub p0, p0, p1
pfree p1
pmul p0, p0, p13
pfree p13
dstore x10, x11, p0, 1, 0
pfree p2
dload x10, x11, p0, 0, 0, 0
pfree p3
dload x10, x11, p1, 0, 0, 0
pmodld 1
psub p0, p0, p1
pfree p1
pmul p0, p0, p14
pfree p14
dstore x10, x11, p0, 1, 0
pfree p5
dload x10, x11, p0, 0, 0, 0
pfree p6
dload x10, x11, p1, 0, 0, 0
pmodld 2
psub p0, p0, p1
pfree p1
pmul p0, p0, p15
pfree p15
dstore x10, x11, p0, 1, 0
pmodld 0
padd p16, p16, p17
pfree p17
dstore x10, x11, p16, 0, 0
pmodld 1
padd p18, p18, p19
pfree p19
dstore x10, x11, p18, 0, 0
pmodld 2
padd p20, p20, p21
pfree p21
dstore x10, x11, p20, 0, 0
pmodld 3
padd p22, p22, p23
pfree p23
dstore x10, x11, p22, 0, 0
pfree p22
dload x10, x11, p0, 0, 0, 0
pmul p0, p0, p24
pfree p24
dstore x10, x11, p0, 1, 0
dload x10, x11, p0, 0, 0, 0
pmodld 0
dload x10, x11, p1, 0, 0, 0
pmul p0, p0, p1
pfree p1
dstore x10, x11, p0, 0, 0
dload x10, x11, p1, 0, 0, 0
pmodld 1
dload x10, x11, p2, 0, 0, 0
pmul p1, p1, p2
pfree p2
dstore x10, x11, p1, 0, 0
dload x10, x11, p2, 0, 0, 0
pmodld 2
dload x10, x11, p3, 0, 0, 0
pmul p2, p2, p3
pfree p3
dstore x10, x11, p2, 0, 0
pfree p16
dload x10, x11, p3, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 0, 0
pmodld 0
psub p3, p3, p0
pfree p0
dload x10, x11, p0, 0, 0, 0
pmul p3, p3, p0
pfree p0
dstore x10, x11, p3, 1, 0
pfree p18
dload x10, x11, p0, 0, 0, 0
pfree p1
dload x10, x11, p1, 0, 0, 0
pmodld 1
psub p0, p0, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmul p0, p0, p1
pfree p1
dstore x10, x11, p0, 1, 0
pfree p20
dload x10, x11, p0, 0, 0, 0
pfree p2
dload x10, x11, p1, 0, 0, 0
pmodld 2
psub p0, p0, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmul p0, p0, p1
psync
pfree p1
dstore x10, x11, p0, 1, 0
psync
