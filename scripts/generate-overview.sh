#!/usr/bin/env bash

find "$1" -type f -name "*.yaml" -print0 \
| while IFS= read -r -d '' file; do
    code=$(yq -r '.code // ""' "$file")
    summary=$(yq -r '.summary // ""' "$file")
    printf "%s\t%s\n" "$code" "$summary"
done
