---
title: "OpenBSD on SunBlade 100: IDE boot failure and workaround"
excerpt: "A technical guide to an OpenBSD boot failure on the SunBlade 100: the firmware limitation, the bisection process, and the historical IDE-write workaround."
last_modified_at: 2026-10-18
toc: true
toc_sticky: true
categories:
  - Blog
tags:
  - SunBlade 100
---

An OpenBSD installation on a SunBlade 100 can complete successfully yet fail at
the first boot when the bootloader writes to an IDE disk through OpenBoot
firmware. This article documents the historical failure investigated around
OpenBSD 7.0 and the bootloader workaround committed in December 2021.

**Historical context:** The commands and patch below describe that investigation.
They have not been re-tested against current OpenBSD releases. The patch is a
record of the fix, not an instruction to apply it to a current source tree.
{: .notice--info}

## The failure and its cause

On affected systems, a bootloader call to `fchmod` attempted to mark an old random
seed as stale. Writing through the OpenBoot IDE driver could corrupt disk data,
preventing the system from booting. The failure occurred after installation,
before the operating system's own drivers took control.

The workaround disables these bootloader write operations for IDE devices. It
does not repair the firmware itself. The investigation distinguished this IDE
path from the SCSI path used on other SPARC64 systems.

## OpenBSD SPARC64 boot process

The boot sequence has three stages:

1. OpenBoot loads the first-stage boot block, written in Forth.
2. That block loads the second-stage bootloader, written in C. This loader uses
   firmware services to access storage, prepare seed entropy, and load the kernel.
3. The kernel starts and takes over with its own device drivers.

This distinction matters: a disk may work during installation and still fail
when the bootloader accesses it through firmware services.

## Isolating the regression

The historical investigation used source bisection: rebuild the bootloader from
different source dates, then check which version introduces the failure.
OpenBSD 6.7's `ofwboot` provided a working bootloader for starting an otherwise
unbootable installation during that process.

The key observations were:

| Source point | Result |
| --- | --- |
| June 5, 2020 | Boot failure |
| June 1, 2020 | Boot failure |
| May 28, 2020 | Boot failure |
| May 27, 2020 | Boot failure |
| May 26, 2020, 16:29 UTC | Boots |
| May 26, 2020, 16:35 UTC | Boot failure |

The boundary identified the `fchmod` call in
`sys/arch/sparc64/stand/ofwboot/boot.c` as the trigger.

### Historical build procedure

The investigation used a separate machine to serve dated OpenBSD source over
NFS, and a network installation environment to recover from failed boot tests.
On the test workstation, the source tree was mounted at `/usr/src` and the
bootloader was rebuilt with:

```sh
cd /usr/src/sys
make obj
cd arch/sparc64/stand
make
make install
installboot -v wd0
```

These commands write boot code to the selected disk. `wd0` was the disk used in
the historical procedure; it is not a universally correct target. Reproducing
this investigation requires a recoverable test installation and backups.

## The workaround

The December 2021 patch checks the parent device type when opening a disk. If
that parent is an IDE device, the loader adds `F_NOWRITE` to the file flags.
The standalone `fchmod` implementation then returns `EOPNOTSUPP` rather than
attempting a write.

The change was committed to OpenBSD by Mark Kettenis. The historical diff below
preserves the source revision information and implementation for reference.

```
diff --git a/sys/arch/sparc64/stand/ofwboot/ofdev.c b/sys/arch/sparc64/stand/ofwboot/ofdev.c
index c23b4129c668..2a4a37e2f787 100644
--- a/sys/arch/sparc64/stand/ofwboot/ofdev.c
+++ b/sys/arch/sparc64/stand/ofwboot/ofdev.c
@@ -1,4 +1,4 @@
-/* $OpenBSD: ofdev.c,v 1.31 2020/12/09 18:10:19 krw Exp $  */
+/* $OpenBSD: ofdev.c,v 1.32 2021/12/01 17:25:35 kettenis Exp $ */
 /* $NetBSD: ofdev.c,v 1.1 2000/08/20 14:58:41 mrg Exp $    */
 
 /*
@@ -520,7 +520,7 @@ devopen(struct open_file *of, const char *name, char **file)
    char fname[256];
    char buf[DEV_BSIZE];
    struct disklabel label;
-   int handle, part;
+   int dhandle, ihandle, part, parent;
    int error = 0;
 #ifdef SOFTRAID
    char volno;
@@ -647,23 +647,24 @@ devopen(struct open_file *of, const char *name, char **file)
        return 0;
    }
 #endif
-   if ((handle = OF_finddevice(fname)) == -1)
+   if ((dhandle = OF_finddevice(fname)) == -1)
        return ENOENT;
+
    DNPRINTF(BOOT_D_OFDEV, "devopen: found %s\n", fname);
-   if (OF_getprop(handle, "name", buf, sizeof buf) < 0)
+   if (OF_getprop(dhandle, "name", buf, sizeof buf) < 0)
        return ENXIO;
    DNPRINTF(BOOT_D_OFDEV, "devopen: %s is called %s\n", fname, buf);
-   if (OF_getprop(handle, "device_type", buf, sizeof buf) < 0)
+   if (OF_getprop(dhandle, "device_type", buf, sizeof buf) < 0)
        return ENXIO;
    DNPRINTF(BOOT_D_OFDEV, "devopen: %s is a %s device\n", fname, buf);
    DNPRINTF(BOOT_D_OFDEV, "devopen: opening %s\n", fname);
-   if ((handle = OF_open(fname)) == -1) {
+   if ((ihandle = OF_open(fname)) == -1) {
        DNPRINTF(BOOT_D_OFDEV, "devopen: open of %s failed\n", fname);
        return ENXIO;
    }
    DNPRINTF(BOOT_D_OFDEV, "devopen: %s is now open\n", fname);
    bzero(&ofdev, sizeof ofdev);
-   ofdev.handle = handle;
+   ofdev.handle = ihandle;
    ofdev.type = OFDEV_DISK;
    ofdev.bsize = DEV_BSIZE;
    if (!strcmp(buf, "block")) {
@@ -685,6 +686,16 @@ devopen(struct open_file *of, const char *name, char **file)
 
        of->f_dev = devsw;
        of->f_devdata = &ofdev;
+
+       /* Some PROMS have buggy writing code for IDE block devices */
+       parent = OF_parent(dhandle);
+       if (parent && OF_getprop(parent, "device_type", buf,
+           sizeof(buf)) > 0 && strcmp(buf, "ide") == 0) {
+           DNPRINTF(BOOT_D_OFDEV, 
+               "devopen: Disable writing for IDE block device\n");
+           of->f_flags |= F_NOWRITE;
+       }
+
 #ifdef SPARC_BOOT_UFS
        bcopy(&file_system_ufs, &file_system[nfsys++], sizeof file_system[0]);
        bcopy(&file_system_ufs2, &file_system[nfsys++], sizeof file_system[0]);
@@ -712,7 +723,7 @@ devopen(struct open_file *of, const char *name, char **file)
 bad:
    DNPRINTF(BOOT_D_OFDEV, "devopen: error %d, cannot open device\n",
        error);
-   OF_close(handle);
+   OF_close(ihandle);
    ofdev.handle = -1;
    return error;
 }
diff --git a/sys/arch/sparc64/stand/ofwboot/vers.c b/sys/arch/sparc64/stand/ofwboot/vers.c
index 3ca4ec8093bf..78466bad3c06 100644
--- a/sys/arch/sparc64/stand/ofwboot/vers.c
+++ b/sys/arch/sparc64/stand/ofwboot/vers.c
@@ -1 +1 @@
-const char version[] = "1.21";
+const char version[] = "1.22";
diff --git a/sys/lib/libsa/fchmod.c b/sys/lib/libsa/fchmod.c
index 7d9bc9cac361..f6252ca9e561 100644
--- a/sys/lib/libsa/fchmod.c
+++ b/sys/lib/libsa/fchmod.c
@@ -1,4 +1,4 @@
-/* $OpenBSD: fchmod.c,v 1.1 2019/08/03 15:22:17 deraadt Exp $  */
+/* $OpenBSD: fchmod.c,v 1.2 2021/12/01 17:25:35 kettenis Exp $ */
 /* $NetBSD: stat.c,v 1.3 1994/10/26 05:45:07 cgd Exp $ */
 
 /*-
@@ -53,6 +53,11 @@ fchmod(int fd, mode_t m)
        errno = EOPNOTSUPP;
        return (-1);
    }
+   /* writing is broken or unsupported */
+   if (f->f_flags & F_NOWRITE) {
+       errno = EOPNOTSUPP;
+       return (-1);
+   }
 
    errno = (f->f_ops->fchmod)(f, m);
    return (0);
diff --git a/sys/lib/libsa/stand.h b/sys/lib/libsa/stand.h
index 9720fe6b1c42..cad63ea389ab 100644
--- a/sys/lib/libsa/stand.h
+++ b/sys/lib/libsa/stand.h
@@ -1,4 +1,4 @@
-/* $OpenBSD: stand.h,v 1.71 2021/10/24 17:49:19 deraadt Exp $  */
+/* $OpenBSD: stand.h,v 1.72 2021/12/01 17:25:35 kettenis Exp $ */
 /* $NetBSD: stand.h,v 1.18 1996/11/30 04:35:51 gwr Exp $   */
 
 /*-
@@ -107,10 +107,11 @@ struct open_file {
 extern struct open_file files[];
 
 /* f_flags values */
-#define    F_READ      0x0001  /* file opened for reading */
-#define    F_WRITE     0x0002  /* file opened for writing */
-#define    F_RAW       0x0004  /* raw device open - no file system */
-#define F_NODEV        0x0008  /* network open - no device */
+#define F_READ          0x0001 /* file opened for reading */
+#define F_WRITE         0x0002 /* file opened for writing */
+#define F_RAW           0x0004 /* raw device open - no file system */
+#define F_NODEV         0x0008 /* network open - no device */
+#define F_NOWRITE       0x0010 /* bootblock writing broken or unsupported */
 
 #define isupper(c) ((c) >= 'A' && (c) <= 'Z')
 #define islower(c) ((c) >= 'a' && (c) <= 'z')

```