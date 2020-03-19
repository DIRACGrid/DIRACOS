#!/usr/bin/env python3
from collections import defaultdict
import hashlib
import os
from os.path import basename, dirname, join
import sys

import lief
from lief import ELF
import magic
from tqdm import tqdm


def sha256sum(filename):
    h = hashlib.sha256()
    b = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def cached_parse(fn):
    try:
        lief_cache[fn]
    except KeyError:
        lief_cache[fn] = lief.parse(fn)
    return lief_cache[fn]


try:
    cache
except NameError:
    cache = {}

try:
    lief_cache
except NameError:
    lief_cache = {}


# Use magic to find all ELF binaries and then extract their SONAME and dependencies
elf_fns = {}
so_names = defaultdict(list)
for root, dirs, files in tqdm(list(os.walk('diracos'))):
    for fn in files:
        fn = join(root, fn)
        if fn not in cache:
            try:
                cache[fn] = magic.from_file(fn)
            except (FileNotFoundError, UnicodeDecodeError):
                print('Skipping', fn)
                continue
        result = cache[fn]
        if result.startswith('ELF '):
            binary = cached_parse(fn)
            soname = None
            deps = []
            for entry in binary.dynamic_entries:
                if entry.tag == ELF.DYNAMIC_TAGS.NEEDED:
                    deps.append(entry.name)
                elif entry.tag == ELF.DYNAMIC_TAGS.SONAME:
                    assert soname is None
                    soname = entry.name
            # For some reason libperl.so doesn't have SONAME set 🤷‍♂️
            if basename(fn) == 'libperl.so':
                assert soname is None
                soname = 'libperl.so'
            so_names[soname].append(fn)
            elf_fns[fn] = deps

for k, v in so_names.items():
    if k is None or len(v) == 1:
        continue
    # As a sanity check, ensure duplicated SONAMEs are identical
    print(f'Found duplicates for {k}: {v}')
    hashes = set()
    for fn in v:
        if 'site-packages' in fn:
            pass
        else:
            hashes.add(sha256sum(fn))
    if len(hashes) > 1:
        raise NotImplementedError(v, hashes)

# Load missing dependencies
with open(sys.argv[1]) as fp:
    allowed_missing = fp.read().strip().split()
allowed_missing.append('ld-linux-x86-64.so.2')

# Fix the RPATHs
for i, elf_fn in tqdm(enumerate(elf_fns)):
    print('Processing', i, elf_fn)
    deps = []
    for soname in elf_fns[elf_fn]:
        if so_names[soname]:
            for dep_fn in so_names[soname]:
                if 'site-packages' in dep_fn:
                    # Python packages often included shared libraries in their wheels
                    # Best practice would be to un-vendor these dependencies, but that's
                    # tricky so instead ensure that they're only added to RPATH if
                    # for binaries in the same package
                    if 'site-packages' not in elf_fn:
                        # The ELF isn't part of a Python package
                        continue
                    dep_fn_split = dep_fn.split('/')
                    elf_fn_split = elf_fn.split('/')
                    if dep_fn_split[dep_fn_split.index('site-packages')] != elf_fn_split[elf_fn_split.index('site-packages')]:
                        # The two ELFs are from different Python packages
                        continue
                # Look for filename matches next to this file to account for symlinks, e.g.
                # libncurses.so.5 -> libncurses.so.5.7
                if os.path.exists(join(dirname(dep_fn), soname)):
                    deps.append(dep_fn)
                    break
            else:
                raise NotImplementedError()
        elif soname in allowed_missing:
            print(f'Found allowed missing SONAME: {soname}')
        else:
            raise NotImplementedError()

    binary = cached_parse(elf_fn)
    rpaths = set()
    for dep in deps:
        relative_path = os.path.relpath(dirname(deps[0]), dirname(fn))
        assert relative_path.startswith('.')
        rpaths.add(os.path.join('$ORIGIN', relative_path).strip('.'))
    rpaths = list(rpaths)

    # This might be a bad idea but keep append any pre-existing RPATHs
    for entry in binary.dynamic_entries:
        if entry.tag == ELF.DYNAMIC_TAGS.RPATH:
            rpaths += entry.name.split(":")
            print('Removing RPATH:', entry.tag, entry.name, entry.value)
            binary.remove(entry)
            break

    binary.add(ELF.DynamicEntryRpath(rpaths))
    binary.write('diracos'+fn[len('diracos'):])
