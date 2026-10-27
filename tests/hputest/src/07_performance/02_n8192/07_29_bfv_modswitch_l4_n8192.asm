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
pmodld 0
psync
padd p0, p0, p1
padd p2, p2, p1
pfree p1
pmodld 1
padd p3, p3, p5
padd p6, p6, p5
pfree p5
pmodld 2
padd p7, p7, p8
padd p9, p9, p8
pfree p8
pmodld 3
padd p10, p10, p11
padd p12, p12, p11
pfree p11
pmul p10, p10, p13
pmul p12, p12, p13
pfree p13
pmodld 0
pmul p1, p10, p14
psub p0, p0, p1
pfree p1
pmul p14, p12, p14
psub p2, p2, p14
pfree p14
pmul p0, p0, p15
dstore x10, x11, p0, 1, 0
pmul p2, p2, p15
pfree p15
dstore x10, x11, p2, 1, 0
pmodld 1
pmul p0, p10, p16
psub p3, p3, p0
pfree p0
pmul p16, p12, p16
psub p6, p6, p16
pfree p16
pmodld 2
pmul p10, p10, p17
psub p7, p7, p10
pfree p10
pmul p12, p12, p17
pfree p17
psub p9, p9, p12
pfree p12
pmodld 1
pmul p3, p3, p18
dstore x10, x11, p3, 1, 0
pmul p6, p6, p18
pfree p18
dstore x10, x11, p6, 1, 0
pmodld 2
pmul p7, p7, p19
dstore x10, x11, p7, 1, 0
pmul p9, p9, p19
psync
pfree p19
dstore x10, x11, p9, 1, 0
psync
