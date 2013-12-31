# Thu Dec 26 16:54:13 PST 2013
#
# The version.sh script fails on Mac OS X since mktemp requires an argument.
# I changed the line in version.sh from:
#   VERSION_FILE_TMP=`mktemp`
# to
#   VERSION_FILE_TMP=`mktemp -t exscript`
#
$ git clone https://github.com/knipknap/exscript.git

vui@Vuis-MacBook-Pro$ ./version.sh
Version is v2.1.401-gdf4810f
Version file unchanged.

