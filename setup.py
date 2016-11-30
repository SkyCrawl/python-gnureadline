#!/usr/bin/env python

import os
import sys
from distutils.command.build_ext import build_ext
import subprocess
from setuptools import setup, Extension

# Basic variables:
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.rst')).read()

# Module info:
VERSION = '6.3.4'
DESCRIPTION = 'The standard Python readline extension statically linked against the GNU readline library.'
LONG_DESCRIPTION = README + '\n\n' + NEWS
CLASSIFIERS = [
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX',
    'Programming Language :: C',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

# Since we assume readline >= 4.2, enable all readline functionality.
# Note: these macros can be found in 'pyconfig.h.in' in the main directory of the Python tarball.
DEFINE_MACROS = [
    ('HAVE_RL_APPEND_HISTORY', None),
    ('HAVE_RL_CALLBACK', None),
    ('HAVE_RL_CATCH_SIGNAL', None),
    ('HAVE_RL_COMPLETION_APPEND_CHARACTER', None),
    ('HAVE_RL_COMPLETION_DISPLAY_MATCHES_HOOK', None),
    ('HAVE_RL_COMPLETION_MATCHES', None),
    ('HAVE_RL_COMPLETION_SUPPRESS_APPEND', None),
    ('HAVE_RL_PRE_INPUT_HOOK', None),
]

# Platform check:
if sys.platform == 'win32':
    sys.exit('Error: this module is not meant to work on Windows (try pyreadline instead)')
elif sys.platform == 'cygwin':
    sys.exit('Error: this module is not needed for Cygwin (and probably does not compile anyway)')

# Input check:
rl_path = os.environ.get('RL_PATH')
if rl_path == None:
	sys.exit('Error: this setup.py expects an RL_PATH environmental variable. It must point to the directory where readline is installed on the system. E.g. if \'<path>\'/lib/libreadline.a\' exists, then \'<path>\' should be passed.')
elif not os.path.exists(os.path.join(rl_path, 'lib/libreadline.a')):
	sys.exit('Error: the RL_PATH environmental variable\'s value is not correct.')

# Workaround for OS X 10.9.2 and Xcode 5.1+.
# The latest clang treats unrecognized command-line options as errors and the
# Python CFLAGS variable contains unrecognized ones (e.g. -mno-fused-madd).
# See Xcode 5.1 Release Notes (Compiler section) and
# http://stackoverflow.com/questions/22313407 for more details. This workaround
# follows the approach suggested in http://stackoverflow.com/questions/724664.
class build_ext_subclass(build_ext):
    def build_extensions(self):
        if sys.platform == 'darwin':
            # Test the compiler that will actually be used to see if it likes flags
            proc = subprocess.Popen(self.compiler.compiler + ['-v'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
            stdout, stderr = proc.communicate()
            clang_mesg = "clang: error: unknown argument: '-mno-fused-madd'"
            if proc.returncode and stderr.splitlines()[0].startswith(clang_mesg):
                for ext in self.extensions:
                    # Use temporary workaround to ignore invalid compiler option
                    # Hopefully -mno-fused-madd goes away before this workaround!
                    ext.extra_compile_args += ['-Wno-error=unused-command-line-argument-hard-error-in-future']
        build_ext.build_extensions(self)

# Determine the target readline.
# Try version-specific 'readline.c' or fall back to major-only version.
source = os.path.join('Modules', '%d.%d' % sys.version_info[:2], 'readline.c')
if not os.path.exists(source):
    source = os.path.join('Modules', '%d.x' % (sys.version_info[0],), 'readline.c')

# Setup the module/extension.
setup(
    name="gnureadline",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    maintainer="Ludwig Schwardt; Sridhar Ratnakumar",
    maintainer_email="ludwig.schwardt@gmail.com; github@srid.name",
    url="http://github.com/ludwigschwardt/python-gnureadline",
    license="GNU GPL",
    platforms=['MacOS X', 'Posix'],
    include_package_data=True,
    py_modules=['readline'],
    cmdclass={'build_ext' : build_ext_subclass},
    ext_modules=[
        Extension(name="gnureadline",
                  sources=[source],
                  include_dirs=[os.path.join(rl_path, 'include')],
                  define_macros=DEFINE_MACROS,
                  extra_objects=[os.path.join(rl_path, 'lib/libreadline.a'), os.path.join(rl_path, 'lib/libhistory.a')],
                  libraries=['ncurses']
        ),
    ],
    zip_safe=False,
)
