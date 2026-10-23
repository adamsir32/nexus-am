dload x10, x11, p63, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 0, 0, 0
dstore x10, x11, p0, 1, 0
pfree p1
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 1, 0, 0
dstore x10, x11, p0, 1, 0
pfree p1
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 12, 0, 0
dstore x10, x11, p0, 1, 0
pfree p1
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 0, 0, 0
dstore x10, x11, p2, 1, 0
pfree p3
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 1, 0, 0
dstore x10, x11, p2, 1, 0
pfree p3
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 12, 0, 0
dstore x10, x11, p2, 1, 0
pfree p3
pmodld 1
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 0, 0, 0
dstore x10, x11, p0, 1, 0
pfree p1
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 1, 0, 0
dstore x10, x11, p0, 1, 0
pfree p1
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 1, 32
pntt p0, p1, 12, 0, 0
dstore x10, x11, p0, 1, 0
pfree p1
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 0, 0, 0
dstore x10, x11, p2, 1, 0
pfree p3
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 1, 0, 0
dstore x10, x11, p2, 1, 0
pfree p3
dload x10, x11, p2, 0, 0, 0
dload x10, x11, p3, 0, 1, 32
pntt p2, p3, 12, 0, 0
dstore x10, x11, p2, 1, 0
pfree p3
pfree p63
psync
