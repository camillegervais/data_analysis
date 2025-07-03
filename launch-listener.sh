cd backend
args=""
if [[ "$@" == *"--wheel"* ]]; then
    args="$args --wheel"
fi
if [[ "$@" == *"--redis"* ]]; then
    args="$args --redis"
fi
python listener.py $args
