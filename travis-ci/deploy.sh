#!/usr/bin/env bash

# stage $RELEASE_NAME release
#
# PRECONDITION: env vars RELEASE_NAME, COMMIT_HASH and IMAGE_TAG
# exist in the calling travis shell

# map branch to GCP/MCI project
if [ "$TRAVIS_BRANCH" = "develop" ]; then
    INSTANCE="test"
    GCP_PROJECT="uwit-mci-0010"
elif [ "$TRAVIS_BRANCH" = "master" ]; then
    INSTANCE="prod"
    GCP_PROJECT="uwit-mci-0011"
else
    echo "Branch $TRAVIS_BRANCH not configured for deployment"
    exit 1
fi

GCP_HOSTNAME="gcr.io"
HELM_URL=https://get.helm.sh
HELM_TGZ=helm-v3.0.0-rc.3-linux-amd64.tar.gz
HELM_CHART_REPO=https://github.com/uw-it-aca/django-production-chart.git
HELM_CHART_DIR=django-production-chart
HELM_RELEASE=${RELEASE_NAME}-prod-${INSTANCE}
FLUX_REPO=https://github.com/uw-it-aca/gcp-flux-${INSTANCE}.git
FLUX_DIR=gcp-flux-${INSTANCE}
RELEASE_BRANCH=release/${RELEASE_NAME}:${COMMIT_HASH}
RELEASE_MANIFEST_NAME=${RELEASE_NAME}.yaml
RELEASE_MANIFEST=${HOME}/${RELEASE_MANIFEST_NAME}.yaml
export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"
export CLOUDSDK_CORE_DISABLE_PROMPTS=1

echo "#####################################"
echo "DEPLOY $HELM_RELEASE in $GCP_PROJECT"
echo "#####################################"

if [ -n "$DOCKER_USER" ]; then
    REPO_TAG="${DOCKER_USER}/${RELEASE_NAME}:${COMMIT_HASH}"
    echo -n "$DOCKER_PASS" | docker login --username="$DOCKER_USER" --password-stdin;
else
    REPO_TAG="${GCP_HOSTNAME}/${GCP_PROJECT}/${RELEASE_NAME}:${COMMIT_HASH}"

    #
    # do GCP authentication magic here?
    #
fi

if [ -n "$REPO_TAG" ]; then
    echo "PUSH image $IMAGE_TAG to $REPO_TAG"
    docker tag "$IMAGE_TAG" "$REPO_TAG"
    docker push "$REPO_TAG"
fi

if [ ! -d $HOME/helm/bin ]; then
    echo "INSTALL helm"
    if [ ! -d $HOME/helm ]; then mkdir $HOME/helm ; fi
    pushd $HOME/helm
    mkdir ./bin
    curl -Lso ${HELM_TGZ} ${HELM_URL}/${HELM_TGZ}
    tar xzf ${HELM_TGZ}
    mv ./linux-amd64/helm ./bin/helm
    popd
fi

echo "CLONE chart $HELM_CHART_REPO"
git clone --depth 1 "$HELM_CHART_REPO" --branch master $HELM_CHART_DIR

echo "GENERATE manifest for release $HELM_RELEASE"
helm template $HELM_CHART_DIR --set commitHash=$COMMIT_HASH -f docker/${INSTANCE}-values.yml > $RELEASE_MANIFEST

FLUX_RELEASE_MANIFEST=releases/${INSTANCE}/$RELEASE_MANIFEST_NAME
echo "CLONE flux $FLUX_REPO: upate ${FLUX_RELEASE_MANIFEST}"
git clone --depth 1 "$FLUX_REPO" --branch master $FLUX_DIR
pushd $FLUX_DIR
echo "The following commands would be"
echo git checkout -b $RELEASE_BRANCH
echo cp -p $RELEASE_MANIFEST $FLUX_RELEASE_MANIFEST
echo git commit -m "Automated release of ${TRAVIS_REPO_SLUG}:${COMMIT_HASH}; pushd by travis build ${TRAVIS_BUILD_NUMBER}" $FLUX_RELEASE_MANIFEST
echo git push origin $RELEASE_BRANCH
echo do github api magic here to open pull request
popd
