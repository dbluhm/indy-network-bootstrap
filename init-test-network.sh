#!/usr/bin/env bash
CONTAINER_RUNTIME=${CONTAINER_RUNTIME:-docker}
NODES=${NODES:-4}
NODE_IP=${NODE_IP:-127.0.0.1}
CLIENT_IP=${CLIENT_IP:-127.0.0.1}

source .env

if [ -z ${1+x} ]; then
  IMAGE_NAME_NODE=ghcr.io/hyperledger/indy-node-container/indy_node:latest-ubuntu20
else
  IMAGE_NAME_NODE=$1
fi

echo "using image $IMAGE_NAME_NODE"

# inits N nodes for a local test network
mkdir -p lib_indy
${CONTAINER_RUNTIME} run \
    -v "${PWD}":/home/indy:z -v "${PWD}"/etc_indy:/etc/indy:z -v "${PWD}"/lib_indy:/var/lib/indy:z \
    -e NODE_IP="${NODE_IP}" -e CLIENT_IP="${CLIENT_IP}" \
    "$IMAGE_NAME_NODE" \
    /bin/bash -c "rm -rf /var/lib/indy/* && python3 bootstrap_network.py && python3 genesis_from_files.py --trustees trustee.csv --stewards steward.csv --pool /var/lib/indy/$INDY_NETWORK_NAME/pool_transactions --domain /var/lib/indy/$INDY_NETWORK_NAME/domain_transactions && chmod -R go+w /var/lib/indy/"

for i in $(seq 1 $NODES); do
    mkdir -p "${PWD}"/etc_indy/node$i
    cp "${PWD}"/etc_indy/indy_config.py "${PWD}"/etc_indy/node$i/
    echo -e "\n# node controller container IP\ncontrolServiceHost = '10.133.133.1$i'" >> "${PWD}"/etc_indy/node$i/indy_config.py
done
