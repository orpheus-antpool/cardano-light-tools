#!/bin/bash

# User variables
BLOCKFROST=<API_KEY>
POOLID=<POOL_ID>
VRF=<VRF_SKEY_FILE>
TZ=<REGION/CITY> # For example: Europe/Amsterdam
GENESIS_PATH=<PATH_TO_JSON_GENESIS_FILES>
CNCLI_PATH=<PATH_TO_CNCLI_EXE_AND_DB>

EPOCH_DATA=`curl -s -H "project_id: $BLOCKFROST" https://cardano-mainnet.blockfrost.io/api/v0/epochs/latest`
EPOCH=`jq '.epoch' <<< $EPOCH_DATA`
ACTIVE_STAKE=`jq -r '.active_stake' <<< $EPOCH_DATA`
POOL_STAKE=`curl -s -H "project_id: $BLOCKFROST" https://cardano-mainnet.blockfrost.io/api/v0/pools/$POOLID | jq -r '.active_stake'`

echo Epoch        : $EPOCH
echo Active stake : $ACTIVE_STAKE
echo Pool stake   : $POOL_STAKE

$CNCLI_PATH/cncli sync --host relays-new.cardano-mainnet.iohk.io --port 3001 --no-service
$CNCLI_PATH/cncli leaderlog --pool-id $POOLID --pool-vrf-skey $VRF --db $CNCLI_PATH/cncli.db \
                            --byron-genesis $GENESIS_PATH/mainnet-byron-genesis.json --shelley-genesis $GENESIS_PATH/mainnet-shelley-genesis.json \
                            --ledger-set $EPOCH --tz $TZ \
                            --pool-stake $POOL_STAKE --active-stake $ACTIVE_STAKE
