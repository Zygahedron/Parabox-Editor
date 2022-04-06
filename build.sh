
if [ -z "$1" ]; then
    echo "Current $(grep -e "version = .*" build.spec)"
    echo "Enter new version (or nothing to keep current):"
    read ver
    if [ ! -z "$ver" ]; then
        echo "Using version = \"$ver\""
    else
        echo "Using $(grep -e "version = .*" build.spec)"
    fi
elif [ "$1" != "-" ]; then
    echo "Using $(grep -e "version = .*" build.spec)"
    ver=$1
fi
if [ ! -z "$ver" ]; then
    # for pynsist
    sed -i '' "1,/version=.*/s/version=.*/version=$ver/" build.ini
    # for pyinstaller
    sed -i '' "1,/version=.*/s/version = \".*\"/version = \"$ver\"/" build.spec
fi

rm -rf ./dist
pyinstaller build.spec --noconfirm
pynsist build.ini
cp ./build/nsis/Zygans_Parabox_Editor_*.exe ./dist

echo "Build finished, find output in ./dist/"