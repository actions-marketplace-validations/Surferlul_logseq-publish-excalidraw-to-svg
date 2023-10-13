#!/usr/bin/env bash
EXCALIDRAW=$(jq '{"type": .type, "version": .version, "source": .source, "elements": .elements, "appState": {"gridSize": null, "exportWithDarkMode": $2}}' "$1")
curl localhost:8080/excalidraw/svg --data-raw "$EXCALIDRAW" > "$1.svg"
