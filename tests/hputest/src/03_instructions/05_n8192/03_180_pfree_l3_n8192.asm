dload x10, x11, p63, 1, 0, 32
pmodld 0
dload x10, x11, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 0, 0
pmul p0, p0, 1
dstore x10, x11, p0, 1, 0
dload x10, x11, p7, 0, 0, 0
pfree p7
dload x10, x11, p7, 0, 0, 0
pmul p7, p7, 1
dstore x10, x11, p7, 1, 0
pmodld 1
dload x10, x11, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 0, 0
pmul p0, p0, 1
dstore x10, x11, p0, 1, 0
dload x10, x11, p7, 0, 0, 0
pfree p7
dload x10, x11, p7, 0, 0, 0
pmul p7, p7, 1
dstore x10, x11, p7, 1, 0
pmodld 2
dload x10, x11, p0, 0, 0, 0
pfree p0
dload x10, x11, p0, 0, 0, 0
pmul p0, p0, 1
dstore x10, x11, p0, 1, 0
dload x10, x11, p7, 0, 0, 0
pfree p7
dload x10, x11, p7, 0, 0, 0
pmul p7, p7, 1
dstore x10, x11, p7, 1, 0
pfree p63
psync
