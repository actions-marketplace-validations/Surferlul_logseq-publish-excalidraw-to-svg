#!/usr/bin/env bash
echo ::debug::'$1:' "$1"
echo ::debug::'$2:' "$2"
EXCALIDRAW=$(jq '{"type": .type, "version": .version, "source": .source, "elements": .elements, "appState": {"gridSize": null, "exportWithDarkMode": '"$2"'}}' "$1")
echo ::debug::'$EXCALIDRAW' "$EXCALIDRAW"
curl localhost:8080/excalidraw/svg --data-raw "$EXCALIDRAW" > "$1.svg"
echo ::debug::"svg: $(cat $1.svg)"
