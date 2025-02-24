
up() {
  local profile=$1
  if [[ -z $profile ]]; then
    profile="dist"
  fi
  docker compose --profile="${profile}" up -d
}

down() {
  local profile=$1
  if [[ -z $profile ]]; then
    profile="*"
  fi
  docker compose --profile="${profile}" down
}

usage() {
  echo "
  Usage: ./run.sh [embedded|dist|down]
  
  embedded: start the embedded profile using custom airflow image
  dist: start the dist profile using official airflow image
  down: stop the running containers
  "


}

cmd=$1
case $cmd in
  embedded)
    up "embedded"
    ;;
  dist)
    up "dist" 
    ;;
  down)
    shift 1
    down $*
    ;;
  *)
    usage
    ;;
esac

