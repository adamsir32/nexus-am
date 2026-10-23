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
pintt p0, p12, 10, 0, 0
dload x10, x11, p13, 0, 1, 32
pintt p0, p13, 11, 0, 0
dload x10, x11, p14, 0, 1, 32
pintt p0, p14, 12, 0, 0
dload x10, x11, p15, 0, 1, 32
pmul p0, p0, p15, 1
pmodld 3
dload x10, x11, p16, 0, 0, 0
pmul p17, p0, p16
pmodld 0
dload x10, x11, p18, 0, 0, 0
pmul p17, p17, p18
pmul p0, p0, 1
padd p17, p17, p0
pfree p0
pfree p15
dload x10, x11, p0, 0, 1, 32
pmul p17, p17, p0, 1
pntt p17, p1, 0, 0, 0
pfree p0
dload x10, x11, p15, 0, 1, 32
pntt p17, p15, 1, 0, 0
pfree p15
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 2, 0, 0
pfree p0
dload x10, x11, p15, 0, 1, 32
pntt p17, p15, 3, 0, 0
pfree p15
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 4, 0, 0
pfree p0
dload x10, x11, p15, 0, 1, 32
pntt p17, p15, 5, 0, 0
pfree p15
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 6, 0, 0
pfree p0
dload x10, x11, p15, 0, 1, 32
pntt p17, p15, 7, 0, 0
pfree p15
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 8, 0, 0
pfree p0
dload x10, x11, p15, 0, 1, 32
pntt p17, p15, 9, 0, 0
pfree p15
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 10, 0, 0
pfree p0
dload x10, x11, p15, 0, 1, 32
pntt p17, p15, 11, 0, 0
pfree p15
dload x10, x11, p0, 0, 1, 32
pntt p17, p0, 12, 0, 0
dload x10, x11, p15, 0, 0, 0
psub p15, p15, p17
pfree p17
dload x10, x11, p17, 0, 0, 0
pmul p15, p15, p17
dstore x10, x11, p15, 1, 0
pmodld 1
dload x10, x11, p15, 0, 0, 0
pintt p15, p1, 0, 0, 0
pintt p15, p2, 1, 0, 0
pfree p2
pintt p15, p3, 2, 0, 0
pfree p3
pintt p15, p5, 3, 0, 0
pfree p5
pintt p15, p6, 4, 0, 0
pfree p6
pintt p15, p7, 5, 0, 0
pfree p7
pintt p15, p8, 6, 0, 0
pfree p8
pintt p15, p9, 7, 0, 0
pfree p9
pintt p15, p10, 8, 0, 0
pfree p10
pintt p15, p11, 9, 0, 0
pfree p11
pintt p15, p12, 10, 0, 0
pfree p12
pintt p15, p13, 11, 0, 0
pfree p13
pintt p15, p14, 12, 0, 0
pfree p14
dload x10, x11, p2, 0, 1, 32
pmul p15, p15, p2, 1
pfree p2
pmodld 3
pmul p16, p15, p16
pmodld 0
pmul p16, p16, p18
pfree p18
pmul p15, p15, 1
padd p16, p16, p15
pfree p15
dload x10, x11, p2, 0, 1, 32
pmul p16, p16, p2, 1
pfree p2
pntt p16, p1, 0, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 1, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 2, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 3, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 4, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 5, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 6, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 7, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 8, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 9, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 10, 0, 0
pfree p1
dload x10, x11, p1, 0, 1, 32
pntt p16, p1, 11, 0, 0
pfree p1
pntt p16, p0, 12, 0, 0
pfree p0
dload x10, x11, p0, 0, 0, 0
psub p0, p0, p16
pfree p16
pmul p0, p0, p17
pfree p17
dstore x10, x11, p0, 1, 0
psync
