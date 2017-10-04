#!/bin/bash
echo "removing existing ssh and stunnel processes"
kill $(ps -ef | grep ssh | awk {'print$2'}) &
kill $(ps -ef | grep stunnel | awk ' FNR==1 {print$2}')

ssh -L 5555:devpgsql.postgres.database.azure.com:5432 -i ~/.ssh/gcc_dw_azure gccdatauser@51.140.47.78 -N -vvv >logs/tunnel.log 2>&1 &
echo "main tunnel to azure vm started"
stunnel
echo "stunnel ssl tunnel established"
