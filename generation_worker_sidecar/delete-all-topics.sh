#!/bin/bash

# Check if the namespace is provided as an argument
if [ -z "$1" ]; then
    echo "Please provide a namespace as an argument."
    exit 1
fi

NAMESPACE="$1"
echo "$NAMESPACE"
# Run the command to list topics and store the result in a variable
TOPICS_OUTPUT=$(pulsarctl topics list "$NAMESPACE")
echo "$TOPICS_OUTPUT"
# Run the command to list topics and store the result in a variable
TOPICS_OUTPUT=$(pulsarctl topics list "$NAMESPACE" | grep 'persistent://')
echo "$TOPICS_OUTPUT"
# Loop through each line of the output
IFS=$'\n'
for LINE in $TOPICS_OUTPUT; do
    # Extract the topic name using awk and sed
    TOPIC=$(echo "$LINE" | awk -F'/' '{print $NF}' | sed 's/ |.*//')
    # Delete the topic
    pulsarctl topics delete -n -f -d "$NAMESPACE/$TOPIC"
    echo "Deleted topic: $NAMESPACE/$TOPIC"
done
unset IFS
