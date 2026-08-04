#!/usr/bin/env bash
# 打包本目录为可安装的 .skill 文件（zip，顶层目录名必须与 SKILL.md 的 name 一致）
set -euo pipefail
cd "$(dirname "$0")"
NAME=pmaster
rm -rf /tmp/$NAME $NAME.skill
mkdir -p /tmp/$NAME
cp -r SKILL.md references /tmp/$NAME/
(cd /tmp && zip -qr - $NAME) > $NAME.skill
rm -rf /tmp/$NAME
echo "built skill/$NAME.skill"
unzip -l $NAME.skill | tail -3
