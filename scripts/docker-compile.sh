set -e
if [ -f "./project/compile" ]; then
    ./project/compile
else
  echo "Compile file not found at /project/compile"
fi
