dload x10, x11, p4, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
padd p0, p0, p1
pfree p1
dstore x10, x11, p0, 1, 0
dload x10, x11, p0, 0, 0, 0
dload x10, x11, p1, 0, 0, 0
padd p0, p0, p1
pfree p1
dstore x10, x11, p0, 1, 0
psync
