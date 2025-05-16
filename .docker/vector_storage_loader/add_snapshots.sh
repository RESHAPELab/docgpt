#!/bin/bash
set -e  # Exit on error

# Install curl if not present
apk add --no-cache curl || echo "Warning: Unable to install curl, assuming it's already present"

echo "Waiting for vector storage to be ready..."
BASEURL="http://${VECTOR_STORAGE_HOST:-localhost}:6333"
echo "Using BASEURL: $BASEURL"

# Wait for Qdrant to be ready
until curl -sSf "$BASEURL/healthz" > /dev/null; do
    echo "Waiting for Qdrant health check..."
    sleep 5
done
echo "Vector storage is ready!"

# Check and handle PROJECT_COLLECTION
if [ -n "$PROJECT_COLLECTION" ]; then
    echo "Verifying PROJECT_COLLECTION: $PROJECT_COLLECTION"
    
    # Validate vector size and distance if provided
    VECTOR_SIZE="${PROJECT_COLLECTION_VECTOR_SIZE:-1536}"
    VECTOR_DISTANCE="${PROJECT_COLLECTION_VECTOR_DISTANCE:-Cosine}"
    
    # Validate vector size is a positive integer
    if ! [[ "$VECTOR_SIZE" =~ ^[0-9]+$ ]] || [ "$VECTOR_SIZE" -le 0 ]; then
        echo "Error: PROJECT_COLLECTION_VECTOR_SIZE must be a positive integer, got: $VECTOR_SIZE"
        VECTOR_SIZE=1536
        echo "Falling back to default size: $VECTOR_SIZE"
    fi
    
    # Validate vector distance
    case "$VECTOR_DISTANCE" in
        "Cosine"|"Euclid"|"Dot")
            echo "Using vector distance: $VECTOR_DISTANCE"
            ;;
        *)
            echo "Error: PROJECT_COLLECTION_VECTOR_DISTANCE must be 'Cosine', 'Euclid', or 'Dot', got: $VECTOR_DISTANCE"
            VECTOR_DISTANCE="Cosine"
            echo "Falling back to default distance: $VECTOR_DISTANCE"
            ;;
    esac
    
    # Check if collection exists
    EXISTS_RESPONSE=$(curl -s -X GET "$BASEURL/collections/$PROJECT_COLLECTION/exists")
    echo "Exists response: $EXISTS_RESPONSE"
    
    if echo "$EXISTS_RESPONSE" | grep -q '"exists":true'; then
        echo "Collection '$PROJECT_COLLECTION' already exists. Continuing with existing collection."
    else
        echo "Collection '$PROJECT_COLLECTION' does not exist. Creating empty collection..."
        CREATE_RESPONSE=$(curl -s -X PUT "$BASEURL/collections/$PROJECT_COLLECTION" \
            -H "Content-Type: application/json" \
            -d "{\"vectors\": {\"size\": $VECTOR_SIZE, \"distance\": \"$VECTOR_DISTANCE\"}}")
        echo "Create response: $CREATE_RESPONSE"
        if echo "$CREATE_RESPONSE" | grep -q '"status":"ok"'; then
            echo "Empty collection '$PROJECT_COLLECTION' created successfully with size $VECTOR_SIZE and distance $VECTOR_DISTANCE."
        else
            echo "Error creating collection. Continuing anyway..."
        fi
    fi
else
    echo "PROJECT_COLLECTION not specified. Continuing with snapshot restoration only."
fi

# Set the snapshot directory path
SNAPSHOT_DIR="/snapshots"
echo "Looking for snapshots in: $SNAPSHOT_DIR"

# Loop over snapshot files
for snapshot in "$SNAPSHOT_DIR"/*.snapshot; do
    if [ -e "$snapshot" ]; then
        COLLECTION_NAME=$(basename "$snapshot" .snapshot)
        echo "Processing snapshot for collection: $COLLECTION_NAME"

        EXISTS_RESPONSE=$(curl -s -X GET "$BASEURL/collections/$COLLECTION_NAME/exists")
        echo "Exists response: $EXISTS_RESPONSE"

        if echo "$EXISTS_RESPONSE" | grep -q '"exists":true'; then
            echo "Collection '$COLLECTION_NAME' already exists. Skipping upload."
        else
            echo "Restoring snapshot for collection '$COLLECTION_NAME'..."
            UPLOAD_RESPONSE=$(curl -s -X POST "$BASEURL/collections/$COLLECTION_NAME/snapshots/upload" \
                -F "snapshot=@$snapshot")
            echo "Upload response: $UPLOAD_RESPONSE"
            if echo "$UPLOAD_RESPONSE" | grep -q '"status":"ok"'; then
                echo "Snapshot restored successfully."
            else
                echo "Error uploading snapshot."
            fi
        fi
    else
        echo "No snapshots found in $SNAPSHOT_DIR"
        break
    fi
done

echo "Snapshots restoration finished successfully."