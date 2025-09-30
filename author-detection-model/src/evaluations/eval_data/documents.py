documents = [
        {
            "id": "D1",
            "text": """Copyright (C) 1992, 1997-2002, 2004-2021 Free Software Foundation, Inc.

            Copying and distribution of this file, with or without modification,
            are permitted in any medium without royalty provided the copyright
            notice and this notice are preserved.

            Mike Haertel wrote the main program and the dfa and kwset matchers.

            Isamu Hasegawa wrote the POSIX regular expression matcher, which is
            part of the GNU C Library and is distributed as part of GNU grep for
            use on non-GNU systems.  Ulrich Drepper, Paul Eggert, Paolo Bonzini,
            Stanislav Brabec, Assaf Gordon, Jakub Jelinek, Jim Meyering, Arnold
            Robbins, Andreas Schwab and Florian Weimer also contributed to this
            matcher.

            Arthur David Olson contributed the heuristics for finding fixed substrings
            at the end of dfa.c.

            Henry Spencer wrote the original test suite from which grep's was derived.
            Scott Anderson invented the Khadafy test.

            David MacKenzie wrote the automatic configuration software used to
            produce the configure script.

            Authors of the replacements for standard library routines are identified
            in the corresponding source files.

            The idea of using Boyer-Moore type algorithms to quickly filter out
            non-matching text before calling the regexp matcher was originally due
            to James Woods.  He also contributed some code to early versions of
            GNU grep.

            Mike Haertel would like to thank Andrew Hume for many fascinating
            discussions of string searching issues over the years.  Hume and
            Sunday's excellent paper on fast string searching describes some of
            the history of the subject, as well as providing exhaustive
            performance analysis of various implementation alternatives.
            The inner loop of GNU grep is similar to Hume & Sunday's recommended
            "Tuned Boyer Moore" inner loop.  See: Hume A, Sunday D.
            Fast string searching. Software Pract Exper. 1991;21(11):1221-48.
            https://doi.org/10.1002/spe.4380211105

            Arnold Robbins contributed to improve dfa.[ch]. In fact
            it came straight from gawk-3.0.3 with small editing and fixes.

            Many folks contributed.  See THANKS; if I omitted someone please
            send me email.

            Alain Magloire maintained GNU grep until version 2.5e.

            Bernhard "Bero" Rosenkränzer <bero@arklinux.org> maintained GNU grep until
            version 2.5.1, ie. from Sep 2001 till 2003.

            Stepan Kasal <kasal@ucw.cz> maintained GNU grep since Feb 2004.

            Tony Abou-Assaleh <taa@acm.org> maintains GNU grep since Oct 2007.

            Jim Meyering <jim@meyering.net> and Paolo Bonzini <bonzini@gnu.org>
            began maintaining GNU grep in Nov 2009.  Paolo bowed out in 2012.

            ;; Local Variables:
            ;; coding: utf-8
            ;; End:
            """,
            "file_name": "AUTHORS",
            "type": "text",
            "entities": ["Free Software Foundation, Inc", "Alain Magloire", "Andreas Schwab", "Andrew Hume",
                         "Arnold Robbins", "Arthur David Olson", "Assaf Gordon", "Bernhard 'Bero' Rosenkränzer",
                         "David MacKenzie", "Florian Weimer", "Henry Spencer", "Isamu Hasegawa", "Jakub Jelinek",
                         "James Woods", "Jim Meyering", "Mike Haertel", "Paolo Bonzini", "Paul Eggert", "Scott Anderson",
                         "Stanislav Brabec", "Stepan Kasal", "D. Sunday", "Tony Abou-Assaleh", "Ulrich Drepper"]
        },
        {
            "id": "D2",
            "text": """
                                        /* $Copyright: $
                                         * Copyright (c) 1996 - 2018 by Steve Baker (ice@mama.indstate.edu)
                                         * All Rights reserved
                                         *
                                         * This program is free software; you can redistribute it and/or modify
                                         * it under the terms of the GNU General Public License as published by
                                         * the Free Software Foundation; either version 2 of the License, or
                                         * (at your option) any later version.
                                         *
                                         * This program is distributed in the hope that it will be useful,
                                         * but WITHOUT ANY WARRANTY; without even the implied warranty of
                                         * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                                         * GNU General Public License for more details.
                                         *
                                         * You should have received a copy of the GNU General Public License
                                         * along with this program; if not, write to the Free Software
                                         * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
                                         */

                                        #include "tree.h"

                                        static char *version ="$Version: $ tree v1.8.0 (c) 1996 - 2018 by Steve Baker, Thomas Moore, Francesc Rocher, Florian Sesser, Kyosuke Tokoro $";
                                        static char *hversion="\t\t tree v1.8.0 %s 1996 - 2018 by Steve Baker and Thomas Moore <br>\n"
                                                      "\t\t HTML output hacked and copyleft %s 1998 by Francesc Rocher <br>\n"
                                                      "\t\t JSON output hacked and copyleft %s 2014 by Florian Sesser <br>\n"
                                                      "\t\t Charsets / OS/2 support %s 2001 by Kyosuke Tokoro\n";

                                        /* Globals */
                                        bool dflag, lflag, pflag, sflag, Fflag, aflag, fflag, uflag, gflag;
                                        bool qflag, Nflag, Qflag, Dflag, inodeflag, devflag, hflag, Rflag;
                                        bool Hflag, siflag, cflag, Xflag, Jflag, duflag, pruneflag;
                                        bool noindent, force_color, nocolor, xdev, noreport, nolinks, flimit, dirsfirst;
                                        bool ignorecase, matchdirs, fromfile;
                                        bool reverse;
                                        char *pattern = NULL, *ipattern = NULL, *host = NULL, *title = "Directory Tree", *sp = " ", *_nl = "\n";
                                        char *file_comment = "#", *file_pathsep = "/";
                                        char *timefmt = NULL;
                                        const char *charset = NULL;

                                        struct _info **(*getfulltree)(char *d, u_long lev, dev_t dev, off_t *size, char **err) = unix_getfulltree;
                                        off_t (*listdir)(char *, int *, int *, u_long, dev_t) = unix_listdir;
                                        int (*cmpfunc)() = alnumsort;

                                        char *sLevel, *curdir, *outfilename = NULL;
                                        FILE *outfile;
                                        int Level, *dirs, maxdirs;

                                        int mb_cur_max;

                                        #ifdef __EMX__
                                        const u_short ifmt[]={ FILE_ARCHIVED, FILE_DIRECTORY, FILE_SYSTEM, FILE_HIDDEN, FILE_READONLY, 0};
                                        #else
                                          #ifdef S_IFPORT
                                          const u_int ifmt[] = {S_IFREG, S_IFDIR, S_IFLNK, S_IFCHR, S_IFBLK, S_IFSOCK, S_IFIFO, S_IFDOOR, S_IFPORT, 0};
                                          const char fmt[] = "-dlcbspDP?";
                                          const char *ftype[] = {"file", "directory", "link", "char", "block", "socket", "fifo", "door", "port", "unknown", NULL};
                                          #else
                                          const u_int ifmt[] = {S_IFREG, S_IFDIR, S_IFLNK, S_IFCHR, S_IFBLK, S_IFSOCK, S_IFIFO, 0};
                                          const char fmt[] = "-dlcbsp?";
                                          const char *ftype[] = {"file", "directory", "link", "char", "block", "socket", "fifo", "unknown", NULL};
                                          #endif
                                        #endif

                                        struct sorts {
                                          char *name;
                                          int (*cmpfunc)();
                                        } sorts[] = {
                                          {"name", alnumsort},
                                          {"version", versort},
                                          {"size", fsizesort},
                                          {"mtime", mtimesort},
                                          {"ctime", ctimesort},
                                          {NULL, NULL}
                                        };""",
            "type": "code",
            "file_name": "tree.c",
            "entities": ["Steve Baker", "Thomas Moore", "Francesc Rocher", "Florian Sesser", "Kyosuke Tokoro"]
        },
        {
            "id": "D3",
            "text": """
                SPDX-License-Identifier: MIT

                Copyright © 2013 Red Hat, Inc.
                Copyright © 2013 David Herrmann <dh.herrmann@gmail.com>

                Permission is hereby granted, free of charge, to any person obtaining a copy
                of this software and associated documentation files (the "Software"), to
                deal in the Software without restriction, including without limitation the
                rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
                sell copies of the Software, and to permit persons to whom the Software is
                furnished to do so, subject to the following conditions:

                The above copyright notice and this permission notice (including the next
                paragraph) shall be included in all copies or substantial portions of the
                Software.

                THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
                IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
                FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
                AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
                LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
                FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
                IN THE SOFTWARE.

                The following license is from a Linux kernel header file and there is no GPL
                code this package links to.

                Copyright (c) 1999-2002 Vojtech Pavlik

                This program is free software; you can redistribute it and/or modify it
                under the terms of the GNU General Public License version 2 as published by
                the Free Software Foundation."
                """,
            "type": "text",
            "file_name": "COPYING",
            "entities": ["Red Hat, Inc.", "David Herrmann", "Vojtech Pavlik"]
        },
        {
            "id": "D4",
            "text": """
                    /* $Copyright: $
                        * Copyright (c) 1996 - 2018 by Steve Baker (ice@mama.indstate.edu)
                        * All Rights reserved
                        *
                        * This program is free software; you can redistribute it and/or modify
                        * it under the terms of the GNU General Public License as published by
                        * the Free Software Foundation; either version 2 of the License, or
                        * (at your option) any later version.
                        *
                        * This program is distributed in the hope that it will be useful,
                        * but WITHOUT ANY WARRANTY; without even the implied warranty of
                        * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                        * GNU General Public License for more details.
                        *
                        * You should have received a copy of the GNU General Public License
                        * along with this program; if not, write to the Free Software
                        * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
                        */
                    #include "tree.h"

                    extern bool dflag, Fflag, aflag, fflag, pruneflag;
                    extern bool noindent, force_color, flimit, matchdirs;
                    extern bool reverse;
                    extern char *pattern, *ipattern;

                    extern int (*cmpfunc)();
                    extern FILE *outfile;
                    extern int Level, *dirs, maxdirs;

                    extern bool colorize;
                    extern char *endcode;

                    extern char *file_comment, *file_pathsep;

                    enum ftok { T_PATHSEP, T_DIR, T_FILE, T_EOP };

                    char *nextpc(char **p, int *tok)
                    {
                        static char prev = 0;
                        char *s = *p;
                        if (!**p) {
                        *tok = T_EOP;	// Shouldn't happen.
                        return NULL;
                        }
                        if (prev) {
                        prev = 0;
                        *tok = T_PATHSEP;
                        return NULL;
                        }
                        if (strchr(file_pathsep, **p) != NULL) {
                        (*p)++;
                        *tok = T_PATHSEP;
                        return NULL;
                        }
                        while(**p && strchr(file_pathsep,**p) == NULL) (*p)++;

                        if (**p) {
                        *tok = T_DIR;
                        prev = **p;
                        *(*p)++ = '\0';
                        } else *tok = T_FILE;
                        return s;
                    }

                    struct _info *newent(char *name) {
                        struct _info *n = xmalloc(sizeof(struct _info));
                        memset(n,0,sizeof(struct _info));
                        n->name = strdup(name);
                        n->child = NULL;
                        n->tchild = n->next = NULL;
                        return n;
                    }

                    // Should replace this with a Red-Black tree implementation or the like
                    struct _info *search(struct _info **dir, char *name)
                    {
                        struct _info *ptr, *prev, *n;
                        int cmp;

                        if (*dir == NULL) return (*dir = newent(name));

                        for(prev = ptr = *dir; ptr != NULL; ptr=ptr->next) {
                        cmp = strcmp(ptr->name,name);
                        if (cmp == 0) return ptr;
                        if (cmp > 0) break;
                        prev = ptr;
                        }
                        n = newent(name);
                        n->next = ptr;
                        if (prev == ptr) *dir = n;
                        else prev->next = n;
                        return n;
                    }
                    """,
            "type": "code",
            "file_name": "file_2.c",
            "entities": ["Steve Baker"]
        },
        {
            "id": "D5",
            "text": """
                            ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}
                            PRINT_DIRECTORY_FLAGS_1=
                            PRINT_DIRECTORY_FLAGS_0=--no-print-directory
                            PRINT_DIRECTORY_FLAGS_=$(PRINT_DIRECTORY_FLAGS_$(AM_DEFAULT_VERBOSITY))
                            AM_MAKEFLAGS = $(PRINT_DIRECTORY_FLAGS_$(V))
                            SUBDIRS = doc libevdev tools test

                            pkgconfigdir = $(libdir)/pkgconfig
                            pkgconfig_DATA = libevdev.pc

                            EXTRA_DIST = libevdev.pc.in meson.build meson_options.txt
                    """,
            "type": "code",
            "file_name": "Makefile.am",
            "entities": []
        },
]

import json

with open("documents.json", "w") as f:
    json.dump(documents, f)
