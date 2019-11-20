#!/usr/bin/env bash
set -eu
trap 'travis_terminate 1' ERR

# stage $RELEASE_NAME as flux repository branch candidate for deployment
#
# NOTES:
#      - git clone/push redirect to /dev/null so auth_token isn't spilled
#
# PRECONDITION: inherited env vars from application's .travis.yml MUST include:
#      RELEASE_NAME: application's name as it is expressed in k8s cluster
#      COMMIT_HASH: application's source commit to be deployed
#      IMAGE_TAG: tag of docker image to be pushed to image repository
#

# branch specific settings
if [ "$TRAVIS_BRANCH" = "develop" ]; then
    APP_INSTANCE="test"
    FLUX_INSTANCE="dev"
    GCP_PROJECT="uwit-mci-0010"
elif [ "$TRAVIS_BRANCH" = "master" ]; then
    APP_INSTANCE="prod"
    FLUX_INSTANCE="prod"
    GCP_PROJECT="uwit-mci-0011"
else
    echo "Branch $TRAVIS_BRANCH not configured for deployment"
    travis_terminate 1
fi

APP_NAME=${RELEASE_NAME}-prod-${APP_INSTANCE}
HELM_CHART_NAME=django-production-chart
FLUX_REPO_NAME=gcp-flux-${FLUX_INSTANCE}
GITHUB_REPO_OWNER=uw-it-aca

HELM_APP_URL=https://get.helm.sh
HELM_APP_TGZ=helm-v3.0.0-linux-amd64.tar.gz
KUBEVAL_URL=https://github.com/instrumenta/kubeval/releases/latest/download
KUBEVAL_TGZ=kubeval-linux-amd64.tar.gz

HELM_CHART_LOCAL_DIR=${HOME}/$HELM_CHART_NAME
HELM_CHART_REPO_PATH=${GITHUB_REPO_OWNER}/${HELM_CHART_NAME}
HELM_CHART_REPO=https://github.com/${HELM_CHART_REPO_PATH}.git

FLUX_LOCAL_DIR=${HOME}/$FLUX_REPO_NAME
FLUX_REPO_PATH=${GITHUB_REPO_OWNER}/$FLUX_REPO_NAME
FLUX_REPO=https://${GH_AUTH_TOKEN}@github.com/${FLUX_REPO_PATH}.git

MANIFEST_FILE_NAME=${RELEASE_NAME}.yaml
LOCAL_MANIFEST=${HOME}/$MANIFEST_FILE_NAME
FLUX_RELEASE_MANIFEST=releases/${FLUX_INSTANCE}/$MANIFEST_FILE_NAME
FLUX_RELEASE_BRANCH_NAME=release/${FLUX_INSTANCE}/${RELEASE_NAME}/$COMMIT_HASH

COMMIT_MESSAGE="Automated ${FLUX_INSTANCE} deploy of ${TRAVIS_REPO_SLUG}:${COMMIT_HASH} by travis build ${TRAVIS_BUILD_NUMBER}"
PULL_REQUEST_MESSAGE="Automated ${FLUX_INSTANCE} deploy of [${TRAVIS_REPO_SLUG}:${COMMIT_HASH}](/${TRAVIS_REPO_SLUG}/commit/${COMMIT_HASH})  Generated travis build [${TRAVIS_BUILD_NUMBER}]($TRAVIS_BUILD_WEB_URL)"

GITHUB_API_PULLS=https://api.github.com/repos/${FLUX_REPO_PATH}/pulls

echo "#####################################"
echo "DEPLOY $APP_NAME in $GCP_PROJECT"
echo "#####################################"

if [ -n "$DOCKER_USER" ]; then
    REPO_TAG="${DOCKER_USER}/${RELEASE_NAME}:${COMMIT_HASH}"
    echo -n "$DOCKER_PASS" | docker login --username="$DOCKER_USER" --password-stdin;
else
    REPO_TAG="gcr.io/${GCP_PROJECT}/${RELEASE_NAME}:${COMMIT_HASH}"
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
    curl -Lso ${HELM_APP_TGZ} ${HELM_APP_URL}/${HELM_APP_TGZ}
    tar xzf ${HELM_APP_TGZ}
    mv ./linux-amd64/helm ./bin/helm
    popd
fi
export PATH=${PATH}:${HOME}/helm/bin

if [ ! -d $HOME/kubeval/bin ]; then
    echo "INSTALL kubeval"
    if [ ! -d $HOME/kubeval ]; then mkdir $HOME/kubeval ; fi
    pushd $HOME/kubeval
    mkdir ./bin
    curl -Lso ${KUBEVAL_TGZ} ${KUBEVAL_URL}/${KUBEVAL_TGZ}
    tar xzf ${KUBEVAL_TGZ}
    mv ./kubeval ./bin/kubeval
    popd
fi
export PATH=${PATH}:${HOME}/kubeval/bin

echo "CLONE chart repository $HELM_CHART_REPO_PATH"
git clone --depth 1 "$HELM_CHART_REPO" --branch master $HELM_CHART_LOCAL_DIR

echo "GENERATE release manifest $MANIFEST_FILE_NAME using docker/${APP_INSTANCE}-values.yml"
helm template $APP_NAME $HELM_CHART_LOCAL_DIR --set-string commitHash=$COMMIT_HASH -f docker/${APP_INSTANCE}-values.yml > $LOCAL_MANIFEST

echo "VALIDATE generated manifest $MANIFEST_FILE_NAME"
kubeval $LOCAL_MANIFEST --strict --exit-on-error --ignore-missing-schemas

echo "CLONE flux repository ${FLUX_REPO_PATH}"
git clone --depth 1 "$FLUX_REPO" --branch master $FLUX_LOCAL_DIR 2>&1 | sed -E 's/[[:xdigit:]]{32,}/[secret]/g'
pushd $FLUX_LOCAL_DIR

echo "CREATE branch $FLUX_RELEASE_BRANCH_NAME"
git checkout -b $FLUX_RELEASE_BRANCH_NAME

echo "CONTEXT"
pwd
ls -l
git branch -r

echo "ADD ${FLUX_RELEASE_MANIFEST} and COMMIT"
cp -p $LOCAL_MANIFEST $FLUX_RELEASE_MANIFEST
git add $FLUX_RELEASE_MANIFEST
git status
git commit -m "$COMMIT_MESSAGE" $FLUX_RELEASE_MANIFEST 2>&1 | sed -E 's/[[:xdigit:]]{32,}/[secret]/g'
git push origin $FLUX_RELEASE_BRANCH_NAME 2>&1 | sed -E 's/[[:xdigit:]]{32,}/[secret]/g'
git status

echo "SUBMIT $FLUX_RELEASE_BRANCH_NAME pull request"
curl -H "Authorization: Token ${GH_AUTH_TOKEN}" -H "Content-type: application/json" -X POST $GITHUB_API_PULLS -d @- <<EOF
{
  "title": "${COMMIT_MESSAGE}",
  "body": "${PULL_REQUEST_MESSAGE}",
  "head": "${FLUX_RELEASE_BRANCH_NAME}",
  "base": "master"
}
EOF
popd

exit 0
