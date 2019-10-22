#!/usr/bin/env bash

#
# gather pieces and configure environment for helm release
#

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

HELM_URL=https://storage.googleapis.com/kubernetes-helm
HELM_TGZ=helm-v2.14.3-linux-amd64.tar.gz
HELM_CHART_REPO=https://github.com/uw-it-aca/django-production-chart.git
HELM_RELEASE=${APP_NAME}-prod-${INSTANCE}
export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"
export CLOUDSDK_CORE_DISABLE_PROMPTS=1

echo "DEPLOYING $HELM_RELEASE in $GCP_PROJECT"

echo "PUSH image $IMAGE_TAG to repository"
echo -n "$DOCKER_PASS" | docker login --username="$DOCKER_USER" --password-stdin;
docker push "$IMAGE_TAG";

if [ ! -d $HOME/google-cloud-sdk/bin ]; then
    echo "INSTALL gcloud sdk"
    rm -rf $HOME/google-cloud-sdk
    curl https://sdk.cloud.google.com | bash > /dev/null
fi
echo "CONFIGURE gcloud sdk"
source $HOME/google-cloud-sdk/path.bash.inc
gcloud components update kubectl
gcloud version

if [ ! -d $HOME/helm/bin ]; then
    echo "INSTALL helm"
    if [ ! -d $HOME/helm ]; then mkdir $HOME/helm ; fi
    pushd $HOME/helm
    curl -Lso ${HELM_TGZ} ${HELM_URL}/${HELM_TGZ}
    tar xzf ${HELM_TGZ}
    ls -l
    mv ./linux-amd64/helm ./bin/helm
    popd
fi
echo "CONFIGURE helm"
export PATH=$HOME/helm/bin:$PATH
helm init --client-only;

echo "CLONE chart $HELM_CHART_REPO"
git clone --depth 1 "$HELM_CHART_REPO" --branch master;

echo "DEPLOY release $HELM_RELEASE"
echo helm upgrade $HELM_RELEASE ./django-production-chart --install --set commitHash=$COMMIT_HASH -f docker/${INSTANCE}-values.yml --dry-run --debug;
