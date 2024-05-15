#!/bin/bash
export JEKYLL_VERSION=4.2.2
 docker run  --volume="$PWD:/srv/jekyll" --volume="$PWD/vendor/bundle:/usr/local/bundle" --volume="$PWD/../3-deliveries/site:/home/static" -it jekyll/jekyll:$JEKYLL_VERSION sh -c 'bundle update --bundler; jekyll build --trace  --config _config.yml'
