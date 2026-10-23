dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
pmul p1, p0, p1
pmodld 1
dload x10, x11, p2, 0, 0, 0
pmul p1, p1, p2
pfree p2
pmodld 0
dload x10, x11, p2, 0, 1, 32
pmul p0, p0, p2, 1
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 0, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 1, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 2, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 3, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 4, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 5, 0, 0
pfree p2
dload x10, x11, p2, 0, 1, 32
pntt p0, p2, 6, 0, 0
pfree p2
pmodld 1
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
pmodld 0
dload x10, x11, p2, 0, 0, 0
pmul p2, p0, p2
dload x10, x11, p3, 0, 0, 0
pmul p0, p0, p3
pfree p3
pmodld 1
dload x10, x11, p3, 0, 0, 0
pmul p3, p1, p3
dload x10, x11, p5, 0, 0, 0
pmul p1, p1, p5
pfree p5
pmodld 0
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 0, 0, 0
pintt p0, p5, 0, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 1, 0, 0
pintt p0, p5, 1, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 2, 0, 0
pintt p0, p5, 2, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 3, 0, 0
pintt p0, p5, 3, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 4, 0, 0
pintt p0, p5, 4, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 5, 0, 0
pintt p0, p5, 5, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p2, p5, 6, 0, 0
pintt p0, p5, 6, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pmul p2, p2, p5, 1
pmul p0, p0, p5, 1
pfree p5
pmodld 1
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 0, 0, 0
pintt p1, p5, 0, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 1, 0, 0
pintt p1, p5, 1, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 2, 0, 0
pintt p1, p5, 2, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 3, 0, 0
pintt p1, p5, 3, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 4, 0, 0
pintt p1, p5, 4, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 5, 0, 0
pintt p1, p5, 5, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pintt p3, p5, 6, 0, 0
pintt p1, p5, 6, 0, 0
pfree p5
dload x10, x11, p5, 0, 1, 32
pmul p3, p3, p5, 1
pmul p1, p1, p5, 1
pfree p5
pmodld 0
dload x10, x11, p5, 0, 0, 0
padd p2, p2, p5
padd p0, p0, p5
pfree p5
pmodld 1
dload x10, x11, p5, 0, 0, 0
padd p3, p3, p5
padd p1, p1, p5
pfree p5
dload x10, x11, p5, 0, 0, 0
pmul p3, p3, p5
pmul p1, p1, p5
pfree p5
pmodld 0
dload x10, x11, p5, 0, 0, 0
pmul p3, p3, p5
psub p2, p2, p3
pfree p3
pmul p1, p1, p5
pfree p5
psub p0, p0, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
pmul p2, p2, p1
pmul p0, p0, p1
pfree p1
dload x10, x11, p1, 0, 0, 0
padd p2, p2, p1
pfree p1
dstore x10, x11, p2, 1, 0
dload x10, x11, p1, 0, 0, 0
padd p1, p1, p0
pfree p0
dstore x10, x11, p1, 1, 0
psync
