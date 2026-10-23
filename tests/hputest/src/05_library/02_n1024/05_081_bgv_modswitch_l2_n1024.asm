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
pintt p0, p9, 7, 0, 0
dload x10, x11, p10, 0, 1, 32
pintt p0, p10, 8, 0, 0
dload x10, x11, p11, 0, 1, 32
pintt p0, p11, 9, 0, 0
dload x10, x11, p12, 0, 1, 32
pmul p0, p0, p12, 1
pmodld 3
dload x10, x11, p13, 0, 0, 0
pmul p14, p0, p13
pmodld 0
dload x10, x11, p15, 0, 0, 0
pmul p14, p14, p15
pmul p0, p0, 1
padd p14, p14, p0
pfree p0
dload x10, x11, p0, 0, 1, 32
pmul p14, p14, p0, 1
pntt p14, p1, 0, 0, 0
dload x10, x11, p16, 0, 1, 32
pntt p14, p16, 1, 0, 0
dload x10, x11, p17, 0, 1, 32
pntt p14, p17, 2, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p14, p18, 3, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pntt p14, p17, 4, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p14, p18, 5, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pntt p14, p17, 6, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p14, p18, 7, 0, 0
pfree p18
dload x10, x11, p17, 0, 1, 32
pntt p14, p17, 8, 0, 0
pfree p17
dload x10, x11, p18, 0, 1, 32
pntt p14, p18, 9, 0, 0
dload x10, x11, p17, 0, 0, 0
psub p17, p17, p14
pfree p14
dload x10, x11, p14, 0, 0, 0
pmul p17, p17, p14
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
pintt p17, p9, 7, 0, 0
pfree p9
pintt p17, p10, 8, 0, 0
pfree p10
pintt p17, p11, 9, 0, 0
pfree p11
pmul p17, p17, p12, 1
pfree p12
pmodld 3
pmul p13, p17, p13
pmodld 0
pmul p13, p13, p15
pfree p15
pmul p17, p17, 1
padd p13, p13, p17
pfree p17
pmul p13, p13, p0, 1
pfree p0
pntt p13, p1, 0, 0, 0
pfree p1
pntt p13, p16, 1, 0, 0
pfree p16
dload x10, x11, p0, 0, 1, 32
pntt p13, p0, 2, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p13, p0, 3, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p13, p0, 4, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p13, p0, 5, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p13, p0, 6, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p13, p0, 7, 0, 0
pfree p0
dload x10, x11, p0, 0, 1, 32
pntt p13, p0, 8, 0, 0
pfree p0
pntt p13, p18, 9, 0, 0
pfree p18
dload x10, x11, p0, 0, 0, 0
psub p0, p0, p13
pfree p13
pmul p0, p0, p14
pfree p14
dstore x10, x11, p0, 1, 0
psync
