dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
padd p0, p0, p1
dload x10, x11, p2, 0, 0, 0
padd p2, p2, p1
pfree p1
pmodld 1
dload x10, x11, p1, 0, 0, 0
dload x10, x11, p3, 0, 0, 0
padd p1, p1, p3
dload x10, x11, p5, 0, 0, 0
padd p5, p5, p3
pfree p3
pmodld 2
dload x10, x11, p3, 0, 0, 0
dload x10, x11, p6, 0, 0, 0
padd p3, p3, p6
dload x10, x11, p7, 0, 0, 0
padd p7, p7, p6
pfree p6
pmodld 3
dload x10, x11, p6, 0, 0, 0
dload x10, x11, p8, 0, 0, 0
padd p6, p6, p8
dload x10, x11, p9, 0, 0, 0
padd p9, p9, p8
pfree p8
dload x10, x11, p8, 0, 0, 0
pmul p6, p6, p8
pmul p9, p9, p8
pfree p8
pmodld 0
dload x10, x11, p8, 0, 0, 0
pmul p10, p6, p8
psub p0, p0, p10
pfree p10
pmul p8, p9, p8
psub p2, p2, p8
pfree p8
dload x10, x11, p8, 0, 0, 0
pmul p0, p0, p8
dstore x10, x11, p0, 1, 0
pmul p2, p2, p8
pfree p8
dstore x10, x11, p2, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p2, p6, p0
psub p1, p1, p2
pfree p2
pmul p0, p9, p0
psub p5, p5, p0
pfree p0
pmodld 2
dload x10, x11, p0, 0, 0, 0
pmul p6, p6, p0
psub p3, p3, p6
pfree p6
pmul p9, p9, p0
pfree p0
psub p7, p7, p9
pfree p9
pmodld 1
dload x10, x11, p0, 0, 0, 0
pmul p1, p1, p0
dstore x10, x11, p1, 1, 0
pmul p5, p5, p0
pfree p0
dstore x10, x11, p5, 1, 0
pmodld 2
dload x10, x11, p0, 0, 0, 0
pmul p3, p3, p0
dstore x10, x11, p3, 1, 0
pmul p7, p7, p0
pfree p0
dstore x10, x11, p7, 1, 0
psync
