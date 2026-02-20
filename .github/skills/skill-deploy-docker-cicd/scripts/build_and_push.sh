#!/bin/bash
# build_and_push.sh - Build and push Docker images to registry

set -e

REGISTRY="${REGISTRY:-docker.io}"
NAMESPACE="${NAMESPACE:-olympus}"
VERSION="${1:-latest}"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT=$(git rev-parse --short HEAD)

echo "Building Olympus Smart Gov images..."
echo "Registry: $REGISTRY"
echo "Version: $VERSION"
echo "Commit: $GIT_COMMIT"

# Build backend
echo "➜ Building backend..."
docker build -t "$REGISTRY/$NAMESPACE/olympus-backend:$VERSION" \
  --label "build.date=$BUILD_DATE" \
  --label "git.commit=$GIT_COMMIT" \
  ./backend

# Build frontend
echo "➜ Building frontend..."
docker build -t "$REGISTRY/$NAMESPACE/olympus-frontend:$VERSION" \
  --label "build.date=$BUILD_DATE" \
  --label "git.commit=$GIT_COMMIT" \
  ./frontend

# Tag as latest
docker tag "$REGISTRY/$NAMESPACE/olympus-backend:$VERSION" \
  "$REGISTRY/$NAMESPACE/olympus-backend:latest"
docker tag "$REGISTRY/$NAMESPACE/olympus-frontend:$VERSION" \
  "$REGISTRY/$NAMESPACE/olympus-frontend:latest"

# Login and push
if [ -z "$REGISTRY_PASSWORD" ]; then
  echo "ERROR: REGISTRY_PASSWORD not set"
  exit 1
fi

echo "$REGISTRY_PASSWORD" | docker login -u "$REGISTRY_USERNAME" --password-stdin "$REGISTRY"

echo "➜ Pushing images..."
docker push "$REGISTRY/$NAMESPACE/olympus-backend:$VERSION"
docker push "$REGISTRY/$NAMESPACE/olympus-backend:latest"
docker push "$REGISTRY/$NAMESPACE/olympus-frontend:$VERSION"
docker push "$REGISTRY/$NAMESPACE/olympus-frontend:latest"

echo "✅ Build and push complete!"
echo "Images: $REGISTRY/$NAMESPACE/olympus-{backend,frontend}:$VERSION"
