#!/bin/bash

TARGET=../media/
HOST=groundup@groundup.news
SOURCE=/home/groundup/production_media/
DAYS=-$1

rsync \
    --progress \
    -ahrv \
    --files-from=<(ssh $HOST "find $SOURCE/uploads/images/ -type f -mtime $DAYS -exec realpath --relative-to=$SOURCE/uploads/images/ '{}' \;") \
    $HOST:$SOURCE/uploads/images/ \
    $TARGET/uploads/images/

rsync \
    --progress \
    -ahrv \
    --files-from=<(ssh $HOST "find $SOURCE/_versions/ -type f -mtime $DAYS -exec realpath --relative-to=$SOURCE/_versions/ '{}' \;") \
    $HOST:$SOURCE/_versions/ \
    $TARGET/_versions/

rsync \
    --progress \
    -ahrv \
    --files-from=<(ssh $HOST "find $SOURCE/targets/ -type f -mtime $DAYS -exec realpath --relative-to=$SOURCE/targets/ '{}' \;") \
    $HOST:$SOURCE/targets/ \
    $TARGET/targets/
