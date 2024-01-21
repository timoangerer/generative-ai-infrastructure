#!/bin/sh
set -e

URL_FILE="${URL_FILE_PATH:-./models.txt}"
DEST_DIR="${DOWNLOAD_DIR:-/mnt/storage}"

mkdir -p "$DEST_DIR"

# Read and process each line
while IFS= read -r line || [ -n "$line" ]; do
  # Split line into URL and optional rename-to part
  url=$(echo "$line" | awk '{print $1}')
  rename_to=$(echo "$line" | awk '{print $2}')

  # If rename_to is provided, use it as the filename
  filename=$(basename "$url")
  if [ ! -z "$rename_to" ]; then
    filename=$rename_to
  fi
  
  # Download and optionally rename the file
  echo "Downloading $url..."
  curl -L -o "$DEST_DIR/$filename" "$url"
done < "$URL_FILE"

echo "Download completed."
