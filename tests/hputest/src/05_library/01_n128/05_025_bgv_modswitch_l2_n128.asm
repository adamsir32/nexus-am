dload x10, x11, p4, 1, 0, 32
pmodld 1
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
pmul p0, p0, p9, 1
pmodld 3
dload x10, x11, p10, 0, 0, 0
pmul p11, p0, p10
pmodld 0
dload x10, x11, p12, 0, 0, 0
pmul p11, p11, p12
pmul p0, p0, 1
padd p11, p11, p0
pfree p0
dload x10, x11, p0, 0, 1, 32
pmul p11, p11, p0, 1
pntt p11, p1, 0, 0, 0
dload x10, x11, p13, 0, 1, 32
pntt p11, p13, 1, 0, 0
dload x10, x11, p14, 0, 1, 32
pntt p11, p14, 2, 0, 0
dload x10, x11, p15, 0, 1, 32
pntt p11, p15, 3, 0, 0
dload x10, x11, p16, 0, 1, 32
pntt p11, p16, 4, 0, 0
dload x10, x11, p17, 0, 1, 32
pntt p11, p17, 5, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p11, p18, 6, 0, 0
dload x10, x11, p17, 0, 0, 0
psub p17, p17, p11
pfree p11
dload x10, x11, p11, 0, 0, 0
pmul p17, p17, p11
dstore x10, x11, p17, 1, 0
pmodld 1
dload x10, x11, p17, 0, 0, 0
pintt p17, p1, 0, 0, 0
pintt p17, p2, 1, 0, 0
pfree p2
pintt p17, p3, 2, 0, 0
pfree p3
pintt p17, p5, 3, 0, 0
pfree p5
pintt p17, p6, 4, 0, 0
pfree p6
pintt p17, p7, 5, 0, 0
pfree p7
pintt p17, p8, 6, 0, 0
pfree p8
pmul p17, p17, p9, 1
pfree p9
pmodld 3
pmul p10, p17, p10
pmodld 0
pmul p10, p10, p12
pfree p12
pmul p17, p17, 1
padd p10, p10, p17
pfree p17
pmul p10, p10, p0, 1
pfree p0
pntt p10, p1, 0, 0, 0
pfree p1
pntt p10, p13, 1, 0, 0
pfree p13
pntt p10, p14, 2, 0, 0
pfree p14
pntt p10, p15, 3, 0, 0
pfree p15
pntt p10, p16, 4, 0, 0
pfree p16
dload x10, x11, p0, 0, 1, 32
pntt p10, p0, 5, 0, 0
pfree p0
pntt p10, p18, 6, 0, 0
pfree p18
dload x10, x11, p0, 0, 0, 0
psub p0, p0, p10
pfree p10
pmul p0, p0, p11
pfree p11
dstore x10, x11, p0, 1, 0
psync
