#!/bin/bash

SCRIPT_INPUT=$(az consumption usage list -o json)

BOLD=$(tput bold)
RESET=$(tput sgr0)

echo
echo "Subscription: ${BOLD}$(az account show --query name -o tsv)${RESET}"
echo
echo "$SCRIPT_INPUT" | az-consumption-summary timeline
echo
echo "${BOLD}Total: $(echo "$SCRIPT_INPUT" | az-consumption-summary total)${RESET}"
echo "$SCRIPT_INPUT" | az-consumption-summary costs \
    --group-by resource-group | termgraph --width 20 --color yellow
echo "$SCRIPT_INPUT" | az-consumption-summary costs \
    --group-by type | termgraph --width 20 --color cyan
