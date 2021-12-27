---
title: "OpenBSD 7.0 won't boot on SunBlade 100"
excerpt_separator: "<!--more-->"
toc: true
toc_sticky: true
categories:
  - Blog
tags:
  - SunBlade 100
---

What follows is a summary and outcome from a severe data corruption bug I
encountered when installing OpenBSD on my SunBlade 100 SPARC64 workstation.
"Severe" is subjective, like this a problem that only impacts 20-year-old
big-endian sparc64 computers booting from an obsolete boot medium.
<!--more-->

To summarize, the OS would install, things seemed super duper until booting
for the first time. Suddenly it was an apocalypse, cats and dogs living
together, mass hysteria, and what's worse, the computer wouldn't start!

Here is the story of the fix(?) and my first patch for OpenBSD.

## There's a bug in my UNIX

Time for some sweet UNIX bug investigation.

**Note:** For mortals (or otherwise) who want details, you can find them here:
[SunBlade 100 won't boot](https://marc.info/?t=163589643900001&r=1&w=2)
{: .notice--info}

The fun started with designing a replacement to the NVRAM IDPROM chip that Sun
used to keep track of important things like the computer serial number. Before
this work was complete, the SunBlade sat lonesome in a corner. Because of this
system's design, it isn't possible to go to the computer store and buy a new
NVRAM chip and get the machine booted again (I have a solution available to
this coming soon). The machine languished for several years un-started until I
had completed and manufactured a prototype IDPROM replacement.

Sitting unused is bad mojo; operating systems have a way of subtly breaking on
equipment that isn't regularly in use. This computer was already well over a
decade old by the time the battery in the IPROM chip drained, most users of
the machine had moved on to newer and shinier toys.

The last version of OpenBSD I knew of that worked on the SunBlade 100 was
version 6.3 because that is the version installed when the NVRAM chip died.
Released Apr 15, 2018, this meant that by the time I started testing the
computer again in September 2021, over three years of changes were introduced
to the operating system. Sure enough, version 7.0 would refuse to boot.

Bug report sent, and of course, the developers aren't using this equipment
anymore.  They have no way (or interest) in fixing the problems impacting this
older device. I realized the only person interested in finding the problem(s)
was me.

### OpenBSD SPARC64 boot process

OpenBSD boots on SPARC64 computers using the onboard OpenBoot Firmware
built-in functions to access IO devices.
[OpenBoot Firmware](https://github.com/openbios/openboot) archives are
available on GitHub for anyone interested in how it works.

The developers didn't know which specific change had caused the system to no
longer boot, but they did have some suspected files to investigate.  On
SPARC64, the OpenBSD boot process occurs in three steps.

1.  OpenFirmware loads the first stage boot block (written in the Forth
    language); this program directs the loading of the second stage binary
    boot block.
2.  The second stage boot block (written in C) talks to the OpenFirmware to
    prepare the environment for loading the OpenBSD kernel. This program is
    responsible for (among other tasks) priming seed entropy and loading the
    kernel itself for execution.
3.  The kernel finally loads and has access to all drivers and IO devices.

OpenFirmware handles all IO interactions until the kernel is running. If there
is a problem with the firmware code, there aren't many options for remediation
now.  The SunBlade 100 ended its service life in February 2008, so the vendor
will no longer fix any problems. The other option is debugging the Forth Fcode
drivers in the OpenBoot firmware.

### Finding the bug

I used a process known as bisection to identify the change causing the boot
process to fail. This process was tedious because every failed attempt
required installing an entirely new copy of the operating system. I learned
that the bug impacted versions immediately after 6.7. The methodology I used
was as follows:

1.  Configure a network boot environment to deploy OpenBSD
2.  On a separate machine, download the OpenBSD source code using the CVS
    command:
    ```
    cvs -q checkout -PD"<date>" src
    ```
3.  Enable a network file server (NFS) on this separate machine.
	1.  Share the directory containing the newly downloaded source code.
	2.  Update the source code to a specific date using the CVS command:
	    ```
        cvs -q up -PdD"2020-05-26 16:35 UTC"
        ```
4.  Install current OpenBSD snapshot
5.  Before the first boot, switch to shell access and download the file
    `ofwboot` from [FTP](https://cdn.openbsd.org/pub/OpenBSD/6.7/sparc64/).
6.  Replace the ofwboot file on the new root filesystem located on the `/mnt`
    filesystem.
7.  Boot the newly installed Operating System and login as *root*.
8.  Dismount the default source code filesystem on `/usr/src` using
    ```
    umount /usr/src
    ```
9.  Mount the source code directory using:
    ```
    mount <NFSPATH> /usr/src
    ```
10. Change the working directory using:
    ```
    cd /usr/src/sys
    ```
11. Prestage the object directories:
    ```
    make obj
    ```
12. Change the working directory with:
    ```
    cd arch/sparc64/stand
    ```
13. run the commands:
    ```
    make
    make install
    installboot -v wd0
    ```
14. Reboot and determine if the problem appears
	1. If the boot fails, repeat Step 4 and choose an earlier date.
	2. If the boot is successful, repeat Step 4 and skip step 5.
15. Stop after finding the precise date and change that caused the fault.

### Work Log

The following work log shows the bisection process:
```
Checking "2020-06-05 09:15 UTC"
- This patch is just before Otto introduced bootblock 2.1
Result : Failure, fault introduced before this change
----
Bisecting date between 2020-06-05 and 2020-05-26
Checking 2020-06-01
Result : Failure, fault introduced before this date
----
Bisecting date between 2020-05-26 and 2020-06-01
Checking 2020-05-28
Result : Failure, fault introduced before this date
----
Bisecting date between 2020-05-26 and 2020-05-28
Checking 2020-05-27
Result : Failure, fault introduced before this date
----
Resetting to 2020-05-26
Checking 2020-05-26
Result : Boots
----
Updating to "2020-05-26 16:29 UTC"
Result : Boots
----
Updating to "2020-05-26 16:35 UTC"
Result : Fault
-----
The problem for this machine is triggered by a call to fchmod in
sys/arch/sparc64/stand/ofwboot/boot.c
```

I determined that a function call named `fchmod` was causing the problem! It
turns out that the OpenBSD developers wanted a way to signal whether the
computer was booting with old random entropy seeds from a previous boot cycle.
They used the `fchmod` function to mark this entropy data as stale.
Unfortunately, for older systems, like the SunBlade 100, there appears to be a
bug in the OpenBoot Firmware that causes writing operations to fail to write
data on legacy IDE hard drives. _Modern_ systems that use SCSI hard drives do
not have this problem.

## The Fix

I designed a source code patch to the binary second stage boot block that
causes the `fchmod` function to ignore the write operation when the computer
boots from an IDE hard drive. The change was committed to the OpenBSD tree via
Mark Kettenis.

It's worth pointing out that this doesn't actually fix the problem with the
OpenBoot IDE driver. For that we'd have to enter the mystical land of fcode
debugging. Until then here is the boot code workaround for IDE drives:

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