DEVICE=/dev/tty1
if [ ! -e "$DEVICE" ]; then
    echo "Error: Device '$DEVICE' not found"
    return 1
fi

echo "Uploading: $1"
cd src || exit
find . -name "*.py" -type f -print0 | xargs -0 -I {} python ../pyboard.py --device "$DEVICE" -f cp {} :