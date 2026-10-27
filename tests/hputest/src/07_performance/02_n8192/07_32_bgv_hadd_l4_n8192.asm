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
pmodld 0
psync
padd p0, p0, p1
pfree p1
dstore x10, x11, p0, 1, 0
pmodld 1
padd p2, p2, p3
pfree p3
dstore x10, x11, p2, 1, 0
pmodld 2
padd p5, p5, p6
pfree p6
dstore x10, x11, p5, 1, 0
pmodld 3
padd p7, p7, p8
pfree p8
dstore x10, x11, p7, 1, 0
pmodld 0
padd p9, p9, p9
dstore x10, x11, p9, 1, 0
pmodld 1
padd p10, p10, p10
dstore x10, x11, p10, 1, 0
pmodld 2
padd p11, p11, p11
dstore x10, x11, p11, 1, 0
pmodld 3
padd p12, p12, p12
psync
dstore x10, x11, p12, 1, 0
psync
